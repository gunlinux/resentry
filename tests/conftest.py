import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session
from sqlalchemy.pool import StaticPool

from resentry.main import create_app
from resentry.database.database import get_sync_db


@pytest.fixture(scope="function")
def client():
    # Create an in-memory SQLite database for each test
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(bind=engine)

    # Create a sessionmaker that uses the test engine
    from sqlalchemy.orm import sessionmaker

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=Session
    )

    # Dependency override to use the test database
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Create app instance and apply the override
    app = create_app()
    app.dependency_overrides[get_sync_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
