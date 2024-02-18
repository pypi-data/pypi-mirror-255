from operator import or_
from typing import List

import sqlalchemy
import sqlalchemy.exc
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from edea_ms.core.auth import CurrentUser
from edea_ms.db import async_session, models
from edea_ms.db.queries import common_project_ids


class Specification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    project_id: int
    name: str
    unit: str
    minimum: float | None = None
    typical: float | None = None
    maximum: float | None = None


router = APIRouter()


async def has_user_project_access(
    project_id: int, current_user: models.User, session: AsyncSession
) -> None:
    try:
        (
            await session.scalars(
                select(models.Project).where(
                    and_(
                        models.Project.id == project_id,
                        or_(
                            models.Project.user_id == current_user.id,
                            models.Project.id.in_(common_project_ids(current_user)),
                        ),
                    )
                )
            )
        ).one()
    except sqlalchemy.exc.NoResultFound as e:
        # TODO: handle user access exception
        raise e


@router.get("/specifications/project/{project_id}", tags=["specification"])
async def get_project_specifications(
    project_id: int, current_user: CurrentUser
) -> list[Specification]:
    async with async_session() as session:
        # check if project is owned by the user
        await has_user_project_access(project_id, current_user, session)

        specs: List[Specification] = [
            Specification.model_validate(spec)
            for spec in (
                (
                    await session.scalars(
                        select(models.Specification).where(
                            models.Specification.project_id == project_id
                        )
                    )
                ).all()
            )
        ]
        return specs


@router.post("/specifications", tags=["specification"], status_code=201)
async def create_specification(
    spec: Specification, current_user: CurrentUser
) -> Specification:
    async with async_session() as session:
        await has_user_project_access(spec.project_id, current_user, session)

        cur = models.Specification()
        cur.update_from_model(spec)

        session.add(cur)
        await session.commit()

        return Specification.model_validate(cur)


@router.put("/specifications/{id}", tags=["specification"])
async def update_specification(
    id: int,
    spec: Specification,
    current_user: CurrentUser,
) -> Specification:
    async with async_session() as session:
        await has_user_project_access(spec.project_id, current_user, session)

        cur = (
            await session.scalars(
                select(models.Specification).where(models.Specification.id == id)
            )
        ).one()

        cur.update_from_model(spec)
        await session.commit()

        return Specification.model_validate(cur)


@router.delete("/specifications/{id}", tags=["specification"])
async def delete_specification(id: int, current_user: CurrentUser) -> dict[str, int]:
    async with async_session() as session:
        spec = (
            await session.scalars(
                select(models.Specification).where(
                    and_(
                        models.Specification.id == id,
                        models.Specification.project_id.in_(
                            common_project_ids(current_user)
                        ),
                    )
                )
            )
        ).one()

        await session.delete(spec)
        await session.commit()

    return {"deleted_rows": 1}
