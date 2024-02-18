import os
import secrets
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sqlalchemy.exc
from fastapi import APIRouter, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.middleware.sessions import SessionMiddleware

from edea_ms.core.auth import AuthenticationMiddleware
from edea_ms.core.staticfiles import get_asset

from .db.models import Model
from .routers import (
    auth_oidc,
    config,
    export,
    files,
    forcing_condition,
    jobs,
    measurement_columns,
    measurement_entries,
    projects,
    specifications,
    testruns,
    users,
)

description = """
EDeA MS helps you to consistently store and query data from test runs of your electronics projects.
"""

tags_metadata = [
    {
        "name": "testrun",
        "description": "Used to batch related measurements (same board, same device) taken typically "
        "without user-interaction. Used to store metadata about the DUT.",
    },
    {
        "name": "specification",
        "description": "Specifications (min, max, typical) of measurement columns",
    },
    {
        "name": "measurement_column",
        "description": "Specify measurement parameters here; set name, description, unit, etc.",
    },
    {
        "name": "measurement_entry",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "forcing_condition",
        "description": "Like *measurement_column* but for forcing conditions (DUT environment / test parameters).",
    },
    {
        "name": "jobqueue",
        "description": "General-purpose distributed task runner FIFO.",
    },
    {
        "name": "projects",
        "description": "Store project names and identifiers.",
    },
    {
        "name": "configuration",
        "description": "Simple key:value store to store application configuration.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    engine = create_async_engine("sqlite+aiosqlite:///edea-ms.sqlite")
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield
    # cleanup here


api_prefix = "/api"

app = FastAPI(
    title="EDeA Measurement Server",
    description=description,
    version="0.1.0",
    license_info={
        "name": "EUPL 1.2",
        "url": "https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(AuthenticationMiddleware)
app.add_middleware(
    SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", secrets.token_hex(16))
)

api = APIRouter(prefix=api_prefix)
api.include_router(testruns.router)
api.include_router(projects.router)
api.include_router(specifications.router)
api.include_router(measurement_columns.router)
api.include_router(measurement_entries.router)
api.include_router(forcing_condition.router)
api.include_router(export.router)
api.include_router(jobs.router)
api.include_router(config.router)
api.include_router(files.router)
api.include_router(users.router)
api.include_router(auth_oidc.router)

app.include_router(api)


@app.exception_handler(sqlalchemy.exc.NoResultFound)
async def sqlalchemy_no_result_found_handler(
    request: Request, exc: sqlalchemy.exc.NoResultFound
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"message": str(exc)}},
    )


@app.exception_handler(sqlalchemy.exc.IntegrityError)
async def sqlalchemy_integrity_error(
    request: Request, exc: sqlalchemy.exc.IntegrityError
) -> JSONResponse:
    # error_code: int | None = None
    msg = str(exc.orig)
    err = {"error": {"message": msg}}

    # if hasattr(exc.orig, "sqlite_errorcode"):
    #    error_code = getattr(exc.orig, "sqlite_errorcode")

    if msg.startswith("UNIQUE constraint failed"):
        constraint = msg[25:]
        if "." in constraint:
            constraint = constraint.split(".")[1]
        err["error"]["field"] = constraint
        err["error"]["type"] = "unique_violation"

    # TODO: support postgres exception format too

    return JSONResponse(
        status_code=422,
        content=err,
    )


@app.get("/{path_name:path}")
async def catch_all(request: Request, path_name: str) -> Response:
    # as this is a catch all, we get anything that isn't matched before, anything we get
    # that starts with /api most likely indicates a bug (or typo).
    if path_name.startswith("api/"):
        raise HTTPException(
            status_code=404, detail=f"route {path_name} not available under /api/*"
        )

    # in SPA mode, paths covered by the frontend should also just return the page
    # because the frontend will then sort out what the client requested.
    frontend_paths = ("project", "testrun")

    return (
        get_asset("index.html")
        if not path_name or path_name.startswith(frontend_paths)
        else get_asset(path_name)
    )
