from fastapi import APIRouter
from pydantic import BaseModel

from edea_ms.core.auth import CurrentUser

router = APIRouter()


class User(BaseModel):
    id: int
    subject: str
    displayname: str
    groups: list[str]
    roles: list[str]
    disabled: bool


@router.get(
    "/users/self",
    tags=["users"],
    description="Get information about the currently logged in user.",
)
async def get_self(
    current_user: CurrentUser,
) -> User:
    return User.model_validate(current_user, from_attributes=True)
