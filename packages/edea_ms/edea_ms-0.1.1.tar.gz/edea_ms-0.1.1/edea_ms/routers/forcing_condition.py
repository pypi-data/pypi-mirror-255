from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from edea_ms.core.auth import CurrentUser
from edea_ms.db import async_session, models


class ForcingCondition(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    column_id: int
    testrun_id: int
    sequence_number: int
    numeric_value: float | None = None
    string_value: str | None = None


router = APIRouter()


async def get_user_testrun(
    testrun_id: int, current_user: CurrentUser, session: AsyncSession
) -> models.TestRun:
    q = select(models.TestRun).where(
        and_(
            models.TestRun.id == testrun_id,
            models.TestRun.user_id == current_user.id,
        )
    )
    # raise an exception if the testrun does not belong to the user
    return (await session.scalars(q)).one()


@router.get("/forcing_conditions", tags=["forcing_condition"])
async def get_forcing_conditions(
    current_user: CurrentUser,
) -> List[ForcingCondition]:
    async with async_session() as session:
        items: List[ForcingCondition] = [
            ForcingCondition.model_validate(item)
            for item in (await session.scalars(select(models.ForcingCondition))).all()
        ]
        return items


@router.post("/forcing_conditions", tags=["forcing_condition"])
async def create_forcing_conditions(
    condition: ForcingCondition,
    current_user: CurrentUser,
) -> ForcingCondition:
    async with async_session() as session:
        await get_user_testrun(condition.testrun_id, current_user, session)

        cond = models.ForcingCondition()
        session.add(cond.update_from_model(condition))

        await session.commit()

        return ForcingCondition.model_validate(cond)


@router.put("/forcing_conditions/{id}", tags=["forcing_condition"])
async def update_forcing_condition(
    id: int,
    condition: ForcingCondition,
    current_user: CurrentUser,
) -> ForcingCondition:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.ForcingCondition).where(models.ForcingCondition.id == id)
            )
        ).one()

        await get_user_testrun(cur.id, current_user, session)
        if condition.testrun_id != cur.testrun_id:
            raise HTTPException(
                429, "changing testrun id of forcing condition is not allowed"
            )

        cur.update_from_model(condition)
        await session.commit()

        return ForcingCondition.model_validate(cur)


@router.delete("/forcing_conditions/{id}", tags=["forcing_condition"])
async def delete_forcing_condition(
    id: int, current_user: CurrentUser
) -> dict[str, int]:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.ForcingCondition).where(models.ForcingCondition.id == id)
            )
        ).one()

        await get_user_testrun(cur.id, current_user, session)

        await session.delete(models.ForcingCondition(id=id))
        await session.commit()

    return {"deleted_rows": 1}
