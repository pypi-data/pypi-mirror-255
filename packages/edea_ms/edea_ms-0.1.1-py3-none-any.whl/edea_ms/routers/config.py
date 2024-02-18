from operator import and_
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from edea_ms.core.auth import CurrentUser
from edea_ms.db import async_session, models


class Setting(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str


router = APIRouter()


@router.get("/config", tags=["configuration"])
async def get_all_configuration_variables(
    current_user: CurrentUser,
) -> dict[str, str]:
    items: List[Setting] = []

    async with async_session() as session:
        for item in (
            await session.scalars(
                select(models.Setting).where(models.Setting.user_id == current_user.id)
            )
        ).all():
            items.append(Setting.model_validate(item))

    return {v.key: v.value for v in items}


@router.get("/config/{key}", tags=["configuration"])
async def get_specific_variable(
    key: str,
    current_user: CurrentUser,
) -> str:
    async with async_session() as session:
        v = Setting.model_validate(
            (
                await session.scalars(
                    select(models.Setting).where(
                        and_(
                            models.Setting.key == key,
                            models.Setting.user_id == current_user.id,
                        )
                    )
                )
            ).one()
        )
        return v.value


@router.post("/config", tags=["configuration"], status_code=201)
async def add_variable(
    setting: Setting,
    current_user: CurrentUser,
) -> Setting:
    async with async_session() as session:
        s = models.Setting(
            key=setting.key, value=setting.value, user_id=current_user.id
        )

        session.add(s)
        await session.commit()

        return Setting.model_validate(s)


@router.put("/config", tags=["configuration"])
async def update_variable(
    setting: Setting,
    current_user: CurrentUser,
) -> Setting:
    async with async_session() as session:
        try:
            cur = (
                await session.scalars(
                    select(models.Setting).where(
                        and_(
                            models.Setting.key == setting.key,
                            models.Setting.user_id == current_user.id,
                        )
                    )
                )
            ).one()

            cur.update_from_model(setting)
            await session.commit()

            return Setting.model_validate(cur)
        except NoResultFound as e:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Can't modify {setting.key!r}; it doesn't exists in the database. (use POST to create)"
                },
            ) from e


@router.delete("/config/{key}", tags=["configuration"])
async def delete_variable(
    key: str,
    current_user: CurrentUser,
) -> dict[str, int]:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.Setting).where(
                    and_(
                        models.Setting.key == key,
                        models.Setting.user_id == current_user.id,
                    )
                )
            )
        ).one()
        await session.delete(cur)
        await session.commit()

    return {"deleted_rows": 1}
