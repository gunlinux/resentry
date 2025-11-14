import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session
from sqlalchemy.pool import StaticPool
from unittest.mock import patch
import asyncio

from resentry.main import create_app
from resentry.database.database import get_sync_db, get_async_db
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel


@pytest.fixture(scope="function")
def client():
    # Create an in-memory SQLite database for each test
    sync_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Also create an async version of the in-memory engine for consistency
    async_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    print(f"Using in-memory database for tests: {sync_engine.url}")

    # Create all tables using the async engine (run synchronously for the fixture)
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    # Run the async table creation
    asyncio.run(create_tables())

    # Create a sessionmaker that uses the test engine
    from sqlalchemy.orm import sessionmaker

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=sync_engine, class_=Session
    )

    # Create async session maker for async operations
    async def override_get_async_db():
        async with AsyncSession(async_engine) as session:
            yield session

    # Dependency override to use the test database
    def override_get_sync_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Create app instance
    app = create_app()

    # Apply the overrides
    app.dependency_overrides[get_sync_db] = override_get_sync_db
    app.dependency_overrides[get_async_db] = override_get_async_db

    # Override the async session creator to use in-memory engine
    with (
        patch("resentry.database.database.async_engine", async_engine),
        patch(
            "resentry.database.database.create_async_session",
            lambda: AsyncSession(async_engine, expire_on_commit=False),
        ),
    ):
        with TestClient(app) as test_client:
            yield test_client
