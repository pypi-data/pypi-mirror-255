from enum import StrEnum
from typing import Any

from fastapi import Depends, HTTPException, params

from edea_ms.core.auth import get_current_active_user


class Role(StrEnum):
    NONE = "none"
    DEFAULT = "default"
    READ_ONLY = "read-only"
    AUTOMATION = "automation"
    BACKUP = "backup"
    CARETAKER = "caretaker"


# to use different names for existing roles override them in this map
# e.g. custom_role_mapping["maintainer"] = Role.CARETAKER
# to disable an existing role name use Role.NONE
custom_role_mapping: dict[str, Role] = {}


class UserHasRole:
    roles: set[Role]

    def __init__(self, *args: Role) -> None:
        self.roles = set(args)

    def __call__(self) -> Any:
        u = get_current_active_user()

        if len(custom_role_mapping) == 0:
            user_roles = set(u.roles)
        else:
            user_roles = {custom_role_mapping.get(v, v) for v in u.roles}

        if self.roles.isdisjoint(user_roles):
            if len(self.roles) == 1:
                msg = f"user is missing {self.roles} role"
            else:
                msg = f"user is missing one of {self.roles} roles"

            raise HTTPException(status_code=403, detail=msg)


def has_roles(*args: Role) -> params.Depends:
    return Depends(UserHasRole(*args))
