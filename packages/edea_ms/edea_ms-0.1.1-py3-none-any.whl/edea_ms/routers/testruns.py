import contextlib
import io
from collections.abc import Iterator
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Any, List

import polars as pl
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from edea_ms.core.auth import CurrentUser
from edea_ms.core.helpers import tr_unique_field, tryint
from edea_ms.db import async_session, models
from edea_ms.db.models import TestRunState
from edea_ms.db.queries import common_project_ids

with contextlib.suppress(ImportError):
    import altair as alt
    import vl_convert as vlc  # type: ignore


router = APIRouter()


class NewTestRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    short_code: str | None = None
    dut_id: str
    machine_hostname: str
    user_name: str
    test_name: str
    data: dict[str, Any] | None = None


class TestRun(NewTestRun):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    state: TestRunState


class TestColumn(BaseModel):
    """
    MeasurementColumn with a few fields omitted
    """

    data_source: str | None = None
    description: str | None = None
    user_note: str | None = None
    measurement_unit: str | None = None
    flags: int | None = None


class TestSetup(BaseModel):
    steps: list[dict[str, str | float]]
    columns: dict[str, TestColumn]


class DataExportFormat(Enum):
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"


class ChartExportFormat(Enum):
    PNG = "png"
    SVG = "svg"
    HTML = "html"


class WrappedIO:
    """WrappedIO is a minimal wrapper to allow string or bytes writes to the same
    underlying buffer.
    """

    def __init__(self) -> None:
        self.buf = io.BytesIO()

    def write(self, b: bytes | str) -> int:
        return self.buf.write(b.encode()) if isinstance(b, str) else self.write(b)

    def seek(self, offset: int) -> int:
        return self.buf.seek(offset)

    def __iter__(self) -> Iterator[bytes]:
        return self.buf.__iter__()

    def __next__(self) -> bytes:
        return self.buf.__next__()


@router.get("/testruns", tags=["testrun"])
async def get_all_testruns(
    current_user: CurrentUser,
) -> List[TestRun]:
    async with async_session() as session:
        items: List[TestRun] = [
            TestRun.model_validate(item)
            for item in (
                await session.scalars(
                    select(models.TestRun).where(
                        or_(
                            models.TestRun.user_id == current_user.id,
                            models.TestRun.project_id.in_(
                                common_project_ids(current_user)
                            ),
                        )
                    )
                )
            ).all()
        ]
        return items


@router.get("/testruns/overview", tags=["testrun"])
async def testruns_overview(
    current_user: CurrentUser,
) -> List[TestRun]:
    """
    testruns_overview returns up to the five most recent testruns from the last 7 days.
    """
    q = (
        select(models.TestRun)
        .where(
            or_(
                models.TestRun.user_id == current_user.id,
                models.TestRun.project_id.in_(common_project_ids(current_user)),
            )
        )
        .where(models.TestRun.created_at >= datetime.now() - timedelta(days=7))
        .order_by(models.TestRun.created_at.desc())
        .limit(5)
    )

    async with async_session() as session:
        items: List[TestRun] = [
            TestRun.model_validate(item) for item in (await session.scalars(q)).all()
        ]
        return items


@router.get("/testruns/{ident}", tags=["testrun"])
async def get_testrun(
    ident: Annotated[int | str, Depends(tryint)], current_user: CurrentUser
) -> TestRun:
    """
    Get a testrun by numeric id or short-code string

    - **id**: int id or short code str
    """

    q = select(models.TestRun).where(
        and_(
            tr_unique_field(ident) == ident,
            or_(
                models.TestRun.user_id == current_user.id,
                models.TestRun.project_id.in_(common_project_ids(current_user)),
            ),
        )
    )

    async with async_session() as session:
        return TestRun.model_validate((await session.scalars(q)).one())


@router.get("/testruns/project/{ident}", tags=["testrun"])
async def get_project_testruns(
    ident: Annotated[int | str, Depends(tryint)], current_user: CurrentUser
) -> list[TestRun]:
    """
    Retrieve all testruns for a project

    - **id**: project id or project number string
    """

    async with async_session() as session:
        # check if it's a project short code and iff, get the project id
        if isinstance(ident, str):
            project_q = select(models.Project).where(models.Project.short_code == ident)
            ident = (await session.scalars(project_q)).one().id

        q = select(models.TestRun).where(
            and_(
                models.TestRun.project_id == ident,
                or_(
                    models.TestRun.user_id == current_user.id,
                    models.TestRun.project_id.in_(common_project_ids(current_user)),
                ),
            )
        )
        specs: List[TestRun] = [
            TestRun.model_validate(run) for run in ((await session.scalars(q)).all())
        ]
        return specs


@router.post("/testruns", tags=["testrun"], status_code=201)
async def create_testrun(new_run: NewTestRun, current_user: CurrentUser) -> TestRun:
    async with async_session() as session:
        res = await session.scalars(
            select(models.TestRun).where(
                and_(
                    models.TestRun.short_code == new_run.short_code,
                    or_(
                        models.TestRun.user_id == current_user.id,
                        models.TestRun.project_id.in_(common_project_ids(current_user)),
                    ),
                )
            )
        )
        try:
            run = res.one()
        except NoResultFound:
            run = None

        if run is None:
            run = models.TestRun(user_id=current_user.id)
            run.update_from_model(new_run)
            session.add(run)
            await session.commit()

        return TestRun.model_validate(run)


@router.put("/testruns/{ident}", tags=["testrun"])
async def update_testrun(
    ident: Annotated[int | str, Depends(tryint)],
    run: TestRun,
    current_user: CurrentUser,
) -> TestRun:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        tr_unique_field(ident) == ident,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()

        cur.update_from_model(run)
        await session.commit()

        return TestRun.model_validate(cur)


@router.put("/testruns/{ident}/field/{field_name}", tags=["testrun"])
async def update_testrun_field(
    ident: Annotated[int | str, Depends(tryint)],
    field_name: str,
    field_value: Annotated[str | int | list[Any] | dict[Any, Any] | None, Body()],
    current_user: CurrentUser,
) -> TestRun:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        tr_unique_field(ident) == ident,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()

        if cur.data is None:
            cur.data = {field_name: field_value}
        else:
            cur.data = (
                cur.data.copy()
            )  # sqlalchemy can't detect value changes within a dict
            cur.data[field_name] = field_value

        await session.commit()
        return TestRun.model_validate(cur)


@router.delete("/testruns/{ident}/field/{field_name}", tags=["testrun"])
async def delete_testrun_field(
    ident: Annotated[int | str, Depends(tryint)],
    field_name: str,
    current_user: CurrentUser,
) -> Response:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        tr_unique_field(ident) == ident,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()

        if cur.data is None:
            return Response(status_code=410)

        cur.data = (
            cur.data.copy()
        )  # sqlalchemy can't detect value changes within a dict
        cur.data[field_name] = None

        await session.commit()
        return Response(status_code=200)


@router.delete("/testruns/{ident}", tags=["testrun"])
async def delete_testrun(
    ident: Annotated[int | str, Depends(tryint)], current_user: CurrentUser
) -> dict[str, int]:
    async with async_session() as session:
        cur = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        tr_unique_field(ident) == ident,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()
        await session.delete(cur)
        await session.commit()

    return {"deleted_rows": 1}


async def _get_testrun_df(run: models.TestRun) -> pl.DataFrame:
    async with async_session() as session:
        # aliases allow for more compact queries
        me = aliased(models.MeasurementEntry)
        mc = aliased(models.MeasurementColumn)
        fc = aliased(models.ForcingCondition)
        sp = aliased(models.Specification)

        query_conditions = (
            select(
                fc.sequence_number,
                mc.measurement_unit.label("unit"),
                mc.name,
                fc.numeric_value,
                fc.string_value,
            )
            .join(mc, mc.id == fc.column_id)
            .where(fc.testrun_id == run.id)
        )

        conditions = [list(e) for e in await session.execute(query_conditions)]
        schema_cond = {
            c.name: c.type.python_type for c in query_conditions.selected_columns
        }
        cond_df = pl.DataFrame(conditions, schema=schema_cond).pivot(
            values=["string_value", "numeric_value"],
            index="sequence_number",
            columns=["name", "unit"],
            aggregate_function="first",
        )

        query_measured_entries = (
            select(
                me.numeric_value.label("me_numeric_value"),
                me.string_value.label("me_string_value"),
                sp.name.label("sp_name"),
                sp.minimum.label("sp_min"),
                sp.typical.label("sp_typ"),
                sp.maximum.label("sp_max"),
            )
            .join(mc, mc.id == me.column_id)
            .join(sp, sp.id == mc.specification_id, isouter=True)
            .where(me.testrun_id == run.id)
        )

        measured_entries = [
            list(e) for e in await session.execute(query_measured_entries)
        ]
        schema_meas = {
            c.name: c.type.python_type for c in query_measured_entries.selected_columns
        }
        meas_df = pl.DataFrame(measured_entries, schema=schema_meas)

        df = pl.concat([cond_df, meas_df], how="horizontal")

        # drop columns which are all nulls
        df = df[[s.name for s in df if s.null_count() != df.height]]

        # strip field types from forcing condition column names, they're always either or
        mapping = {
            col: f'fc{col.removeprefix("string_value").removeprefix("numeric_value")}'
            for col in df.schema.keys()
            if col.startswith("string_value_") or col.startswith("numeric_value_")
        }

        df = df.rename(mapping)

        return df


async def _get_user_testrun(
    ident: str | int, current_user: CurrentUser
) -> models.TestRun:
    async with async_session() as session:
        run = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        tr_unique_field(ident) == ident,
                        or_(
                            models.TestRun.user_id == current_user.id,
                            models.TestRun.project_id.in_(
                                common_project_ids(current_user)
                            ),
                        ),
                    )
                )
            )
        ).one()

    return run


@router.get("/testruns/measurements/{ident}", tags=["testrun"])
async def testrun_measurements(
    ident: Annotated[int | str, Depends(tryint)],
    current_user: CurrentUser,
    data_format: DataExportFormat
    | None = Query(default=DataExportFormat.JSON, alias="format"),
) -> StreamingResponse:
    """
    This returns the results for a specific measurement run. It first retrieves the conditions, pivots them and then
    merges them together with the results. As a last step, all columns only consisting of null values get removed.
    """

    # check if the run exists before we do other more expensive tasks
    run = await _get_user_testrun(ident, current_user)

    df = await _get_testrun_df(run)

    f = io.BytesIO()

    # polars can directly export a variety of formats which works nicely here
    if data_format == DataExportFormat.JSON:
        df.write_json(f, row_oriented=True)
        media_type = "application/json"
    elif data_format == DataExportFormat.PARQUET:
        df.write_parquet(f)
        media_type = "application/octet-stream"
    elif data_format == DataExportFormat.CSV:
        df.write_csv(f)
        media_type = "text/csv"
    else:
        raise HTTPException(423, "unknown export format")

    f.seek(0)

    headers = {}
    if data_format != DataExportFormat.JSON:
        headers[
            "Content-Disposition"
        ] = f'attachment; filename="{run.short_code}_{run.dut_id}.{data_format}"'

    return StreamingResponse(f, headers=headers, media_type=media_type)


@router.get("/testruns/plot/{ident}", tags=["testrun"])
async def testrun_plot_charts(
    ident: Annotated[int | str, Depends(tryint)],
    current_user: CurrentUser,
    data_format: ChartExportFormat
    | None = Query(default=ChartExportFormat.SVG, alias="format"),
    dpi: int = Query(default=150),
) -> StreamingResponse:
    """
    This returns the results for a specific measurement run. It first retrieves the conditions, pivots them and then
    merges them together with the results. As a last step, all columns only consisting of null values get removed.
    """

    if not alt:
        raise HTTPException(
            status_code=400, detail="Plotting dependency 'altair' is not available"
        )
    if not vlc and data_format in [ChartExportFormat.PNG, ChartExportFormat.SVG]:
        raise HTTPException(
            status_code=400,
            detail="Plotting to PNG or SVG requires the vl-convert-python library",
        )

    # check if the run exists before we do other more expensive tasks
    run = await _get_user_testrun(ident, current_user)

    if run.data and "vega_lite" in run.data:
        chart_spec = alt.Chart.from_dict(run.data["vega_lite"])
    else:
        raise HTTPException(
            status_code=400, detail="testrun has no 'vega_lite' chart specification"
        )

    df = await _get_testrun_df(run)
    chart_spec.data = df

    f = WrappedIO()

    # polars can directly export a variety of formats which works nicely here
    if data_format == ChartExportFormat.HTML:
        chart_spec.save(fp=f, format="html")
        media_type = "text/html"
    elif data_format == ChartExportFormat.SVG:
        chart_spec.save(fp=f, format="svg")
        media_type = "image/svg"
    elif data_format == ChartExportFormat.PNG:
        chart_spec.save(fp=f, format="png", ppi=dpi)
        media_type = "image/png"
    else:
        raise HTTPException(423, "unknown export format")

    f.seek(0)

    headers = {}
    if data_format != DataExportFormat.JSON:
        headers[
            "Content-Disposition"
        ] = f'attachment; filename="{run.short_code}_{run.dut_id}.{data_format}"'

    return StreamingResponse(f, headers=headers, media_type=media_type)


@router.post("/testruns/setup/{ident}", tags=["testrun"])
async def setup_testrun(
    ident: Annotated[int | str, Depends(tryint)],
    setup: TestSetup,
    current_user: CurrentUser,
) -> Response:
    unique_field = tr_unique_field(ident)

    async with async_session() as session:
        run = (
            await session.scalars(
                select(models.TestRun).where(
                    and_(
                        unique_field == ident,
                        models.TestRun.user_id == current_user.id,
                    )
                )
            )
        ).one()

        # check if the TestRun is already set up or in progress
        if run.state != TestRunState.NEW:
            raise HTTPException(
                400,
                f"run already in state {run.state}, started at {run.started_at} "
                f"by {run.user_name} on {run.machine_hostname}",
            )

        meas_cols: dict[str, models.MeasurementColumn] = {}

        # create the columns first if they don't exist yet
        for name, values in setup.columns.items():
            m_res = await session.scalars(
                select(models.MeasurementColumn).where(
                    and_(
                        models.MeasurementColumn.name == name,
                        models.MeasurementColumn.project_id == run.project_id,
                    )
                )
            )

            try:
                column = m_res.one()
            except NoResultFound:
                column = None

            if column is None:
                column = models.MeasurementColumn(
                    name=name,
                    project_id=run.project_id,
                    data_source=values.data_source,
                    description=values.description,
                    user_note=values.user_note,
                    measurement_unit=values.measurement_unit,
                    flags=values.flags,
                )
                session.add(column)

            meas_cols[name] = column

        await session.commit()

    # run a second tx to create the forcing conditions too
    async with async_session() as session:
        for step in setup.steps:
            sequence_number = step["idx"]
            step_names = set(step.keys())
            step_names.discard("idx")
            for name in step_names:
                column = meas_cols[name]
                fc = models.ForcingCondition(
                    column_id=column.id,
                    testrun_id=run.id,
                    sequence_number=sequence_number,
                )
                target_value = step[name]
                if isinstance(target_value, float):
                    fc.numeric_value = target_value
                elif isinstance(target_value, int):
                    fc.numeric_value = float(target_value)
                else:
                    fc.string_value = target_value

                session.add(fc)

        await session.commit()

    # finally, set the testrun state to SETUP_COMPLETE to accept measurements now
    async with async_session() as session:
        run = (
            await session.scalars(select(models.TestRun).where(unique_field == ident))
        ).one()
        run.state = TestRunState.SETUP_COMPLETE
        await session.commit()

    return Response(status_code=200)


async def transition_state(
    session: AsyncSession,
    run_id: int | str,
    to_state: TestRunState,
    current_user: models.User,
) -> models.TestRun:
    q = select(models.TestRun).where(
        and_(
            tr_unique_field(run_id) == run_id,
            models.TestRun.user_id == current_user.id,
        )
    )

    cur = (await session.scalars(q)).one()

    allowed = []

    if cur.state == TestRunState.SETUP_COMPLETE:
        allowed = [TestRunState.FAILED, TestRunState.INTERRUPTED, TestRunState.RUNNING]
    elif cur.state == TestRunState.RUNNING:
        allowed = [TestRunState.FAILED, TestRunState.INTERRUPTED, TestRunState.COMPLETE]

    if to_state in allowed:
        cur.state = to_state
    else:
        msg = f"testrun {run_id} not in one of the following allowed states: {allowed}"
        raise HTTPException(status_code=400, detail=msg)

    return cur


@router.put("/testruns/start/{ident}", tags=["testrun"])
async def start_testrun(
    ident: Annotated[int | str, Depends(tryint)], current_user: CurrentUser
) -> TestRun:
    async with async_session() as session:
        cur = await transition_state(session, ident, TestRunState.RUNNING, current_user)
        cur.started_at = datetime.now()
        session.add(cur)
        await session.commit()

        return TestRun.model_validate(cur)


@router.put("/testruns/complete/{ident}", tags=["testrun"])
async def complete_testrun(
    ident: Annotated[int | str, Depends(tryint)], current_user: CurrentUser
) -> TestRun:
    async with async_session() as session:
        cur = await transition_state(
            session, ident, TestRunState.COMPLETE, current_user
        )
        cur.completed_at = datetime.now()
        session.add(cur)
        await session.commit()

        return TestRun.model_validate(cur)


@router.put("/testruns/fail/{ident}", tags=["testrun"])
async def fail_testrun(
    ident: Annotated[int | str, Depends(tryint)], current_user: CurrentUser
) -> TestRun:
    async with async_session() as session:
        cur = await transition_state(session, ident, TestRunState.FAILED, current_user)
        cur.completed_at = datetime.now()
        session.add(cur)
        await session.commit()

        return TestRun.model_validate(cur)
