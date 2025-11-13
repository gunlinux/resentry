import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from resentry.main import create_app
from resentry.database.database import Base, get_sync_db


@pytest.fixture(scope="function")
def client():
    # Create an in-memory SQLite database for each test
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    # Create a sessionmaker that uses the test engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
