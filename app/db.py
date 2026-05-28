import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Default: local Postgres via docker-compose (assignment-compliant primary path).
DEFAULT_DATABASE_URL = "postgresql+psycopg://library:library@localhost:5432/library_db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def to_async_database_url(url: str) -> str:
    """Normalize common sync-style URLs to async SQLAlchemy drivers."""
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


ASYNC_DATABASE_URL = to_async_database_url(DATABASE_URL)

connect_args: dict = {}
if ASYNC_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(ASYNC_DATABASE_URL, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
