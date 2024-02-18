from authlib.integrations.starlette_client import OAuth  # type: ignore
from fastapi import APIRouter, HTTPException, Request
import httpx
from starlette.config import Config
from starlette.responses import RedirectResponse

router = APIRouter()

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

oauth = OAuth(config)
_providers_str: str = config.get("OIDC_PROVIDERS", default="")
providers = _providers_str.split(",") if "," in _providers_str else [_providers_str]

for provider in providers:
    if provider != "":
        oauth.register(
            name=provider.lower(),
            client_kwargs={"scope": config.get(f"{provider.upper()}_SCOPE")},
        )


@router.get("/login")
async def login_default(request: Request) -> RedirectResponse:
    if len(providers) == 1:
        return RedirectResponse(f"{request.url}/{providers[0]}")
    else:
        raise HTTPException(404, "More than one provider configured and none specified")


@router.get("/login/{provider}")
async def login(request: Request, provider: str) -> RedirectResponse:
    # absolute url for callback
    # we will define it below
    p = provider.lower()
    if p not in providers:
        raise NotImplementedError(f"provider {p} not implemented")

    prov = getattr(oauth, p)
    try:
        resp = await prov.authorize_redirect(request, f"{config.get('API_BASE_URL')}/auth/{p}")
        print(f"login redirect: {resp}")
        return resp
    except httpx.ConnectError as e:
        raise HTTPException(
            status_code=500,
            detail=f"could not connect to configured OIDC backend: {e}",
        ) from e


@router.get("/auth/{provider}")
async def auth(request: Request, provider: str) -> RedirectResponse:
    p = provider.lower()
    if p not in providers:
        raise NotImplementedError(f"{provider} not implemented")

    prov = getattr(oauth, p)
    token = await prov.authorize_access_token(request)

    if user := token.get("userinfo"):
        request.session["user"] = dict(user)
    elif p == "github":
        # special code-path for github because they don't to implement OIDC properly
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                config.get("GITHUB_USERINFO_ENDPOINT"),
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
            info = resp.json()
            info["sub"] = f"github_{info['id']}"
            info["picture"] = info["avatar_url"]

            # TODO: simple graphql query to get all org and team memberships

            request.session["user"] = info
    else:
        raise NotImplementedError("")
    return RedirectResponse(url="/")


@router.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    request.session.pop("user", None)
    return RedirectResponse(url="/")
