from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import JSON, ForeignKey, LargeBinary, UniqueConstraint, func
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

T = TypeVar("T", bound="Model")


class Model(DeclarativeBase):
    def update_from_model(self: T, mod: BaseModel) -> T:
        for field in mod.model_fields_set:
            if field != "id":
                setattr(self, field, getattr(mod, field))

        return self


class ProvidesUserMixin:
    "A mixin that adds a 'user' relationship to classes."

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship("User")


class ProvidesProjectMixin:
    "A mixin that adds a 'project' relationship to classes."

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    @declared_attr
    def project(cls) -> Mapped["Project"]:
        return relationship("Project")


class ProvidesSpecificationMixin:
    "A mixin that adds a 'specification' relationship to classes."

    specification_id: Mapped[int | None] = mapped_column(
        ForeignKey("specifications.id")
    )

    @declared_attr
    def specification(cls) -> Mapped["Specification"]:
        return relationship("Specification")


class ProvidesMeasurementColumnMixin:
    "A mixin that adds a 'measurement_column' relationship to classes."

    column_id: Mapped[int] = mapped_column(ForeignKey("measurement_columns.id"))

    @declared_attr
    def column(cls) -> Mapped["MeasurementColumn"]:
        return relationship("MeasurementColumn")


class ProvidesTestRunColumnMixin:
    "A mixin that adds a 'testrun' relationship to classes."

    testrun_id: Mapped[int] = mapped_column(ForeignKey("testruns.id"))

    @declared_attr
    def testrun(cls) -> Mapped["TestRun"]:
        return relationship("TestRun")


class User(Model):
    __tablename__: str = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(unique=True)
    displayname: Mapped[str]
    groups: Mapped[MutableList[str]] = mapped_column(JSON)
    roles: Mapped[MutableList[str]] = mapped_column(JSON)
    disabled: Mapped[bool]


class Project(Model, ProvidesUserMixin):
    __tablename__: str = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str | None] = mapped_column(unique=True)
    name: Mapped[str]
    groups: Mapped[MutableList[str]] = mapped_column(JSON)


class Specification(Model, ProvidesProjectMixin):
    __tablename__: str = "specifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    unit: Mapped[str]
    minimum: Mapped[float]
    typical: Mapped[float]
    maximum: Mapped[float]


class TestRunState(int, enum.Enum):
    NEW = 1
    SETUP_COMPLETE = 2
    RUNNING = 3
    INTERRUPTED = 4
    COMPLETE = 5
    FAILED = 6


class TestRun(Model, ProvidesProjectMixin, ProvidesUserMixin):
    __tablename__: str = "testruns"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str | None] = mapped_column(unique=True)  # String(max_length=4)
    dut_id: Mapped[str]
    machine_hostname: Mapped[str]
    user_name: Mapped[str]
    test_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    started_at: Mapped[datetime | None]
    completed_at: Mapped[datetime | None]
    state: Mapped[TestRunState] = mapped_column(default=TestRunState.NEW)
    data: Mapped[dict[Any, Any] | None] = mapped_column(JSON)

    __mapper_args__ = {"eager_defaults": True}


class MeasurementColumn(Model, ProvidesProjectMixin, ProvidesSpecificationMixin):
    __tablename__: str = "measurement_columns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    data_source: Mapped[str | None] = mapped_column(default="")
    description: Mapped[str | None] = mapped_column(default="")
    user_note: Mapped[str | None] = mapped_column(default="")
    measurement_unit: Mapped[str | None] = mapped_column(default="")
    flags: Mapped[int | None] = mapped_column(default=0)


class MeasurementEntry(
    Model, ProvidesTestRunColumnMixin, ProvidesMeasurementColumnMixin
):
    __tablename__ = "measurement_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    sequence_number: Mapped[int]
    numeric_value: Mapped[float | None]
    string_value: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    flags: Mapped[int | None] = mapped_column(default=0)


class ForcingCondition(
    Model, ProvidesMeasurementColumnMixin, ProvidesTestRunColumnMixin
):
    __tablename__: str = "forcing_conditions"

    id: Mapped[int] = mapped_column(primary_key=True)
    sequence_number: Mapped[int]
    numeric_value: Mapped[float | None]
    string_value: Mapped[str | None]


class Setting(Model, ProvidesUserMixin):
    __tablename__: str = "sysconfig"
    __table_args__ = (UniqueConstraint("key", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    key: Mapped[str]
    value: Mapped[str]


class JobState(int, enum.Enum):
    NEW = 1
    PENDING = 2
    COMPLETE = 3
    FAILED = 4


class Job(Model, ProvidesUserMixin):
    __tablename__: str = "jobqueue"

    id: Mapped[int] = mapped_column(primary_key=True)
    state: Mapped[JobState] = mapped_column(default=JobState.NEW)
    worker: Mapped[str] = mapped_column(default="N/A")
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    function_call: Mapped[str]
    parameters: Mapped[dict[Any, Any]] = mapped_column(JSON)

    __mapper_args__ = {"eager_defaults": True}


class TestrunFile(Model, ProvidesTestRunColumnMixin):
    __tablename__: str = "testrun_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str]
    content_type: Mapped[str]
    size: Mapped[int]
    content: Mapped[bytes | None] = mapped_column(
        LargeBinary
    )  # if blob is none, filename must be a path or URL
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __mapper_args__ = {"eager_defaults": True}
