import os
import sys

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

dbfile = "edea-ms.sqlite"
default_db = f"sqlite+aiosqlite:///{dbfile}"
DATABASE_URL = os.getenv("DATABASE_URL", default_db)

if "pytest" in sys.modules:
    DATABASE_URL = "sqlite+aiosqlite:///test.db"

print(f"using DB from {DATABASE_URL}")
engine = create_async_engine(DATABASE_URL)


def override_db(db: AsyncEngine) -> None:
    global engine
    engine = db


def async_session() -> AsyncSession:
    return async_sessionmaker(engine, expire_on_commit=False)()
