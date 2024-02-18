import os
from contextvars import ContextVar
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from jwt import InvalidTokenError, MissingRequiredClaimError, PyJWKClient
from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from edea_ms.db import async_session
from edea_ms.db.models import User

REQUEST_USER_CTX_KEY = "request_user"

_request_user_ctx_var: ContextVar[User | None] = ContextVar(
    REQUEST_USER_CTX_KEY, default=None
)

jwks_client = PyJWKClient(
    os.getenv("JWKS_URL", "http://test/.well-known/jwks.json"), cache_keys=True
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
claims_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication token does not contain groups claim",
)


class SingleUser:
    def __init__(
        self,
        username: str = "single_user",
        groups: list[str] | None = None,
        roles: list[str] | None = None,
    ):
        if groups is None:
            groups = ["defailt"]
        if roles is None:
            roles = ["admin"]
        self.is_enabled = False
        self.username = username
        self.groups = groups
        self.roles = roles

    def enable(
        self,
        username: str | None = None,
        groups: list[str] | None = None,
        roles: list[str] | None = None,
    ) -> None:
        self.is_enabled = True
        if username:
            self.username = username
        if groups:
            self.groups = groups
        if roles:
            self.roles = roles

    @property
    def enabled(self) -> bool:
        return self.is_enabled


single_user = SingleUser()


async def manage_user_data(
    session: AsyncSession,
    username: str,
    displayname: str,
    groups: list[str],
    roles: list[str],
) -> User:
    u: User | None = None

    try:
        u = (
            await session.scalars(select(User).where(User.subject == username))
        ).one_or_none()
    except MultipleResultsFound as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": "multiple users with the same subject found when one or none were expected",
                "exc": e,
            },
        ) from e

    if u is None:
        u = User(
            subject=username,
            displayname=displayname,
            groups=groups,
            roles=roles,
            disabled=False,
        )
        session.add(u)
        await session.commit()
    elif u.groups != groups or u.roles != roles:
        u.groups = MutableList(groups)
        u.roles = MutableList(roles)
        session.add(u)
        await session.commit()

    return u


async def get_current_user(
    request: Request,
    token: str | None = None,
    authorization: str | None = None,
    x_webauth_user: str | None = None,
    x_webauth_groups: list[str] | None = None,
    x_webauth_roles: list[str] | None = None,
) -> User | None:
    """
    get_current_user returns the currently logged in user or creates it if it's the first
    time we see them. it can take a JSON Web Token (JWT) as a cookie or an Authorization header.
    Alternatively, it also accepts X-Webauth-{User,Groups,Roles} headers which specify the user
    details further.
    """

    groups: list[str] = []
    roles: list[str] = []
    displayname: str = ""
    username: str | None = None

    if single_user.enabled:
        username = single_user.username
        groups = single_user.groups
        roles = single_user.roles
    else:
        # get the user information either from headers or a token
        if request.session:
            if u := request.session.get("user"):
                if isinstance(u, dict):
                    username = u["sub"]
                    displayname = u.get("preferred_username", u.get("name"))
                    groups = u.get("groups_direct", u.get("groups", []))
                    roles = u.get("roles", [])

        # TODO: check if headers should be trusted or not
        if not username:
            if x_webauth_user:
                username = x_webauth_user
                groups = x_webauth_groups or []
                roles = x_webauth_roles or []

                # handle multiple field values in a single header according to RFC9110, section 5.3.
                if len(groups) == 1 and "," in groups[0]:
                    groups = groups[0].split(",")
                if len(roles) == 1 and "," in roles[0]:
                    roles = roles[0].split(",")
            elif token is None and authorization is None:
                return None
            else:
                # use token or authentication header, strip off "Bearer " part for header
                p_tok = token or authorization.split(" ")[-1] if authorization else ""

                groups, roles, username = _parse_jwt(p_tok)

    async with async_session() as session:
        return await manage_user_data(session, username, displayname, groups, roles)


def _parse_jwt(token: str) -> tuple[list[str], list[str], str]:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["HS256", "ES256", "ES256K", "EdDSA"],
            options={"require": ["exp", "iss", "sub", "groups"]},
        )
        # sub and groups are required for decoding, should always be some
        username = payload.get("sub") or ""

        # groups and roles are registered claims according to RFC 9068
        groups = payload.get("groups") or []
        roles = payload.get("roles") or []
    except MissingRequiredClaimError as e:
        raise claims_exception from e
    except InvalidTokenError as e:
        raise credentials_exception from e
    return groups, roles, username


class AuthenticationMiddleware:
    """
    AuthenticationMiddleware provides the default way of extracting user information
    from a request. It supports JWTs as cookies or headers or directly trusted headers
    with the necessary information.

    For different authentication needs, another middleware can be used, it's only necessary
    that the _request_user_ctx_var gets filled with a user object.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        authorization = request.headers.get("authorization")
        x_webauth_user = request.headers.get("x-webauth-user")
        x_webauth_groups = request.headers.getlist("x-webauth-groups")
        x_webauth_roles = request.headers.getlist("x-webauth-roles")
        token = request.cookies.get("token")

        u = await get_current_user(
            request,
            token,
            authorization,
            x_webauth_user,
            x_webauth_groups,
            x_webauth_roles,
        )
        ctx_token = _request_user_ctx_var.set(u)

        await self.app(scope, receive, send)

        _request_user_ctx_var.reset(ctx_token)


def get_current_active_user() -> User:
    current_user = _request_user_ctx_var.get()

    if current_user is None:
        raise credentials_exception

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


# annotated dependency for the routers
CurrentUser = Annotated[User, Depends(get_current_active_user)]
