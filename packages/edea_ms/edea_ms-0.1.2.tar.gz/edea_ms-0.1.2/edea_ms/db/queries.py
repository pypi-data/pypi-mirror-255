from typing import Any, Tuple
from edea_ms.core.helpers import prj_unique_field
from edea_ms.db import models


from sqlalchemy import Select, and_, column, func, select, true


from operator import or_


def all_projects(user: models.User) -> Select[Tuple[models.Project]]:
    return (
        select(models.Project)
        .distinct()
        .join_from(
            models.Project,
            func.json_each(models.Project.groups).table_valued(column("value")).alias("groups"),
            true(),
            isouter=True,
        )
        .where(
            or_(
                column("value").in_(user.groups),
                models.Project.user_id == user.id,
            )
        )
    )


def single_project(
    user: models.User, ident: int | str
) -> Select[Tuple[models.Project]]:
    return (
        select(models.Project)
        .distinct()
        .join_from(
            models.Project,
            func.json_each(models.Project.groups).table_valued(column("value")).alias("groups"),
            true(),
            isouter=True,
        )
        .where(
            and_(
                prj_unique_field(ident) == ident,
                or_(
                    column("value").in_(user.groups),
                    models.Project.user_id == user.id,
                ),
            )
        )
    )


def _common_project_ids(user: models.User) -> Select[Tuple[int]]:
    return (
        select(models.Project.id)
        .distinct()
        .join_from(
            models.Project,
            func.json_each(models.Project.groups).table_valued(column("value")).alias("groups"),
            true(),
            isouter=True,
        )
        .where(
            or_(
                column("value").in_(user.groups),
                models.Project.user_id == user.id,
            )
        )
    )


def common_project_ids(
    user: models.User, alias: str = "common_project_ids"
) -> Select[Tuple[Any]]:
    return select(_common_project_ids(user).cte(alias).c.id)
