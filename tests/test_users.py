from fastapi.testclient import TestClient

from resentry.main import create_app
from resentry.database.database import sync_engine, Base


def test_create_user():
    app = create_app()
    Base.metadata.create_all(bind=sync_engine)

    with TestClient(app) as client:
        response = client.post("/api/v1/users/", json={"name": "Test User", "telegram_chat_id": "123456"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["telegram_chat_id"] == "123456"


def test_get_users():
    app = create_app()
    Base.metadata.create_all(bind=sync_engine)

    with TestClient(app) as client:
        # First create a user
        client.post("/api/v1/users/", json={"name": "Test User", "telegram_chat_id": "123456"})
        # Then get all users
        response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_user_by_id():
    app = create_app()
    Base.metadata.create_all(bind=sync_engine)

    with TestClient(app) as client:
        # Create a user first
        create_response = client.post("/api/v1/users/", json={"name": "Test User", "telegram_chat_id": "123456"})
        user_id = create_response.json()["id"]
        
        # Get the user by ID
        response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"


def test_update_user():
    app = create_app()
    Base.metadata.create_all(bind=sync_engine)

    with TestClient(app) as client:
        # Create a user first
        create_response = client.post("/api/v1/users/", json={"name": "Test User", "telegram_chat_id": "123456"})
        user_id = create_response.json()["id"]
        
        # Update the user
        response = client.put(f"/api/v1/users/{user_id}", 
                               json={"name": "Updated User", "telegram_chat_id": "654321"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User"
    assert data["telegram_chat_id"] == "654321"


def test_delete_user():
    app = create_app()
    Base.metadata.create_all(bind=sync_engine)

    with TestClient(app) as client:
        # Create a user first
        create_response = client.post("/api/v1/users/", json={"name": "Test User", "telegram_chat_id": "123456"})
        user_id = create_response.json()["id"]
        
        # Delete the user
        response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"