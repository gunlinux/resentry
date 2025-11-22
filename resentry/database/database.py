from typing import AsyncGenerator, Generator
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from resentry.config import settings


# Create the async engine for async operations (use regular SQLite for sync operations)
print(settings.DATABASE_URL)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to True for SQL debugging
)

# Create the sync engine for sync operations (like tests)
# Replace aiosqlite with regular sqlite for sync operations
sync_db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "sqlite:///")
sync_engine = create_engine(
    sync_db_url,
    echo=True,  # Set to True for SQL debugging
)


# Create async session factory with proper type handling
def create_async_session():
    return AsyncSession(async_engine, expire_on_commit=False)


# Create sync session
SyncSessionLocal = sessionmaker(
    bind=sync_engine, class_=Session, expire_on_commit=False
)  # type: ignore

# For compatibility with existing imports
Base = SQLModel


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with create_async_session() as session:
        yield session


def get_sync_db() -> Generator[Session, None, None]:
    with Session(sync_engine) as session:
        yield session
