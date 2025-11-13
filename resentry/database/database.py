from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy import create_engine

from resentry.config import settings


# Create the async engine for async operations
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
)

# Create the sync engine for sync operations (like tests)
sync_engine = create_engine("sqlite:///./test.db", echo=False)


# Create async session factory with proper type handling
def create_async_session():
    return AsyncSession(async_engine, expire_on_commit=False)


# Create sync session
SyncSessionLocal = sessionmaker(
    bind=sync_engine, class_=Session, expire_on_commit=False
)  # type: ignore

# Create base class for models
Base = declarative_base()


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with create_async_session() as session:
        yield session


def get_sync_db() -> Generator[Session, None, None]:
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
