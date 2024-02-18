from pathlib import Path
from tempfile import TemporaryDirectory

import aiosqlite
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from edea_ms.core.authz import Role, has_roles

from ..db import DATABASE_URL

router = APIRouter()


@router.get("/export/db", dependencies=[has_roles(Role.BACKUP)])
async def export_database(r: Request) -> FileResponse:
    dbfile = DATABASE_URL.replace("sqlite:///", "")
    main_db = await aiosqlite.connect(dbfile)
    db_name = Path(dbfile).name
    backup_dir = TemporaryDirectory()
    backup_path = Path(backup_dir.name, db_name)
    backup_db = await aiosqlite.connect(backup_path)

    await main_db.backup(backup_db)

    await backup_db.close()
    await main_db.close()

    # return the database backup and remove it afterward
    return FileResponse(
        path=backup_path,
        media_type="application/vnd.sqlite3",
        filename=db_name,
        background=BackgroundTask(backup_dir.cleanup),
    )
