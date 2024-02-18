from datetime import datetime, timezone
from typing import Any, List

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import select

from edea_ms.core.auth import get_current_active_user
from edea_ms.db import async_session, models
from edea_ms.db.models import JobState, User

router = APIRouter()


class Job(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    state: JobState | None = None
    worker: str | None = None
    updated_at: datetime | None = None
    function_call: str
    parameters: dict[Any, Any]


class NewJob(BaseModel):
    function_call: str
    parameters: dict[Any, Any]


@router.get("/jobs/all", tags=["jobqueue"])
async def get_all_jobs(
    current_user: User = Depends(get_current_active_user),
) -> List[Job]:
    async with async_session() as session:
        jobs: List[Job] = [
            Job.model_validate(job)
            for job in (
                await session.scalars(
                    select(models.Job).where(models.Job.user_id == current_user.id)
                )
            ).all()
        ]
        return jobs


@router.get("/jobs/new", tags=["jobqueue"])
async def get_new_job(
    request: Request, current_user: User = Depends(get_current_active_user)
) -> Job | None:
    async with async_session() as session:
        try:
            res = await session.scalars(
                select(models.Job).where(
                    and_(
                        models.Job.state == JobState.NEW,
                        models.Job.user_id == current_user.id,
                    ),
                )
            )
            item = res.first()
            if item is None:
                return None

            if request.client is not None:
                item.worker = request.client.host
            item.state = JobState.PENDING
            item.updated_at = datetime.now(timezone.utc)

            await session.commit()
        except NoResultFound:
            item = None

        return Job.model_validate(item)


@router.get("/jobs/{job_id}", tags=["jobqueue"])
async def get_specific_job(
    job_id: int, current_user: User = Depends(get_current_active_user)
) -> Job:
    async with async_session() as session:
        return Job.model_validate(
            (
                await session.scalars(
                    select(models.Job).where(
                        and_(
                            models.Job.id == job_id,
                            models.Job.user_id == current_user.id,
                        )
                    )
                )
            ).one()
        )


@router.post("/jobs/new", tags=["jobqueue"])
async def create_job(
    new_task: NewJob, current_user: User = Depends(get_current_active_user)
) -> Job:
    async with async_session() as session:
        task = models.Job(
            state=JobState.NEW,
            updated_at=datetime.now(timezone.utc),
            function_call=new_task.function_call,
            parameters=new_task.parameters,
            user_id=current_user.id,
        )

        session.add(task)
        await session.commit()

        return Job.model_validate(task)


@router.put("/jobs/{job_id}", tags=["jobqueue"])
async def update_specific_job(
    job_id: int, task: Job, current_user: User = Depends(get_current_active_user)
) -> Job:
    async with async_session() as session:
        job = (
            await session.scalars(
                select(models.Job).where(
                    and_(models.Job.id == job_id, models.Job.user_id == current_user.id)
                )
            )
        ).one()

        session.add(job.update_from_model(task))
        await session.commit()

        return Job.model_validate(job)


@router.delete("/jobs/{job_id}", tags=["jobqueue"])
async def delete_job(
    job_id: int, request: Request, current_user: User = Depends(get_current_active_user)
) -> Job | None:
    async with async_session() as session:
        try:
            item = (
                await session.scalars(
                    select(models.Job).where(
                        and_(
                            models.Job.id == job_id,
                            models.Job.user_id == current_user.id,
                        )
                    )
                )
            ).one()
            if item is None:
                return None

            item.state = JobState.COMPLETE
            item.updated_at = datetime.now()
            if request.client is not None:
                item.worker = request.client.host

            session.add(item)
            await session.commit()
        except NoResultFound:
            item = None
        return Job.model_validate(item)
