from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_, select
from sqlalchemy.exc import NoResultFound

from edea_ms.core.auth import CurrentUser
from edea_ms.db import async_session, models
from edea_ms.routers.measurement_columns import MeasurementColumn
from edea_ms.routers.testruns import TestRun


class MeasurementEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    sequence_number: int
    numeric_value: float | None = None
    string_value: str | None = None
    created_at: datetime | None = None
    flags: int | None = None
    column: MeasurementColumn
    testrun_id: int | None = None


router = APIRouter()


class BatchInput(BaseModel):
    sequence_number: int
    testrun_id: int
    payload: dict[str, Any]  # mapping of column name to result value


@router.post("/measurement_entries/batch", tags=["measurement_entry"], status_code=201)
async def batch_create_measurement_entries(
    batch_input: BatchInput,
    current_user: CurrentUser,
) -> None:
    async with async_session() as session:
        test_run = TestRun.model_validate(
            (
                await session.scalars(
                    select(models.TestRun).where(
                        and_(
                            models.TestRun.id == batch_input.testrun_id,
                            models.TestRun.user_id == current_user.id,
                        )
                    )
                )
            ).one()
        )

        # check first if the run is in the right state
        if test_run.state != models.TestRunState.RUNNING:
            raise HTTPException(
                status_code=400, detail=f"run {test_run.id} is not set to RUNNING state"
            )

        for k, v in batch_input.payload.items():
            res = await session.scalars(
                select(models.MeasurementColumn).where(
                    and_(
                        models.MeasurementColumn.name == k,
                        models.MeasurementColumn.project_id == test_run.project_id,
                    )
                )
            )

            try:
                column = res.one()
            except NoResultFound:
                column = None

            if column is None:
                column = models.MeasurementColumn(
                    name=k, project_id=test_run.project_id
                )
                session.add(column)
                await session.commit()

            entry = models.MeasurementEntry(
                sequence_number=batch_input.sequence_number,
                testrun_id=test_run.id,
                column_id=column.id,
            )

            if type(v) in [float, int]:
                entry.numeric_value = v
            else:
                entry.string_value = str(v)
            session.add(entry)

        await session.commit()


@router.post("/measurement_entries", tags=["measurement_entry"])
async def create_measurement_entry(
    entry: MeasurementEntry,
    current_user: CurrentUser,
) -> MeasurementEntry:
    async with async_session() as session:
        testrun = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        models.TestRun.id == entry.testrun_id,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()

        res = await session.scalars(
            select(models.MeasurementColumn).where(
                and_(
                    models.MeasurementColumn.name == entry.column.name,
                    models.MeasurementColumn.project_id == testrun.project_id,
                )
            )
        )

        try:
            column = res.one()
        except NoResultFound:
            column = None

        if column is None:
            column = models.MeasurementColumn(
                name=entry.column.name, project_id=testrun.project_id
            )
            session.add(column)
            await session.commit()

        new_entry = models.MeasurementEntry(
            sequence_number=entry.sequence_number,
            testrun_id=testrun.id,
            column_id=column.id,
        )

        if entry.numeric_value is not None:
            new_entry.numeric_value = entry.numeric_value
        else:
            new_entry.string_value = entry.string_value
        session.add(new_entry)

        await session.commit()

    return MeasurementEntry.model_validate(entry)


@router.put("/measurement_entries/{id}", tags=["measurement_entry"])
async def update_measurement_entry(
    id: int,
    entry: MeasurementEntry,
    current_user: CurrentUser,
) -> MeasurementEntry:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.MeasurementEntry).where(models.MeasurementEntry.id == id)
            )
        ).one()

        cur.update_from_model(entry)
        await session.commit()

        return MeasurementEntry.model_validate(cur)


@router.delete("/measurement_entries/{id}", tags=["measurement_entry"])
async def delete_measurement_entry(
    id: int, current_user: CurrentUser
) -> dict[str, int]:
    async with async_session() as session:
        await session.delete(models.MeasurementEntry(id=id))
        await session.commit()

    return {"deleted_rows": 1}
