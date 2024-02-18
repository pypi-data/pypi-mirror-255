import asyncio
import os
import re
import socket
from typing import Any, AsyncGenerator, List

import httpx
import nest_asyncio  # type: ignore
import pytest
import uvicorn
from playwright.async_api import async_playwright, expect
from pytest_docker.plugin import Services

from ..main import app
from ..routers import auth_oidc


class UvicornServer(uvicorn.Server):
    serve_task: asyncio.Task[None]
    did_start: asyncio.Event
    did_close: asyncio.Event

    def __init__(self, config: uvicorn.Config):
        super().__init__(config=config)
        self.did_start = asyncio.Event()
        self.did_close = asyncio.Event()

    async def start(self) -> None:
        self.serve_task = asyncio.create_task(self.serve())
        self.serve_task.add_done_callback(lambda _: self.did_close.set())
        await self.did_start.wait()

    async def startup(self, sockets: List[socket.socket] | None = None) -> None:
        await super().startup(sockets)
        self.did_start.set()

    async def shutdown(self, sockets: List[socket.socket] | None = None) -> None:
        await super().shutdown(sockets)
        self.serve_task.cancel()


@pytest.fixture(scope="module")
async def uvicorn_server() -> AsyncGenerator[str, Any]:
    server = UvicornServer(config=uvicorn.Config(app=app, host="127.0.0.1", port=8000))
    await server.start()
    yield "http://127.0.0.1:8000"
    await server.shutdown()


def is_responsive(url: str) -> bool:
    try:
        response = httpx.get(url)
        if response.status_code == 200:
            return True
    except Exception:
        return False

    return False


@pytest.fixture(scope="session")
def dex_service(docker_ip: str | Any, docker_services: Services) -> str:
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("dex", 5556)
    url = f"http://{docker_ip}:{port}/dex/.well-known/openid-configuration"
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url


def test_env_sanity_check() -> None:
    assert auth_oidc.providers is not None


@pytest.mark.anyio
async def test_oidc_backend_connect_error(client: httpx.AsyncClient) -> None:
    """by default, when the OIDC backend is unreachable it should return an error"""
    r = await client.get("/api/login/dex")
    assert r.status_code == 500


@pytest.mark.anyio
async def test_oidc_backend_connect_success(
    client: httpx.AsyncClient, dex_service: str
) -> None:
    r = await client.get("/api/login/dex")
    print(r.content)
    assert r.status_code == 302


@pytest.mark.anyio
async def test_login_with_oidc(uvicorn_server: str, dex_service: str) -> None:
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch()
        nest_asyncio.apply(browser._loop)

        page = await browser.new_page()
        # page.set_default_timeout(5000)

        page.on("request", lambda request: print(">>", request.method, request.url))
        page.on("response", lambda response: print("<<", response.status, response.url))

        await page.goto("http://localhost:8000/")

        await expect(page.get_by_text("Login")).to_be_visible()

        # Expect a title "to contain" a substring.
        await expect(page).to_have_title(re.compile("EDeA-MS"))

        await page.get_by_role("link", name="Login").click()

        # wait for dex login page to be loaded
        await expect(page.get_by_text("Login")).to_be_visible()

        await page.get_by_placeholder("email address").fill("alice@example.com")
        await page.get_by_placeholder("password").fill("alice")
        await page.get_by_role("button", name="Login").click()

        # wait for "Grant Access" page
        await expect(page.get_by_role("button", name="Grant Access")).to_be_visible()
        await page.get_by_role("button", name="Grant Access").click()

        # check that we're logged in
        await expect(page.get_by_text("Logout")).to_be_visible()
