from fastapi.testclient import TestClient


def test_create_user(client: TestClient, create_test_token):
    token = create_test_token()
    response = client.post(
        "/api/v1/users/",
        json={
            "name": "Test User",
            "telegram_chat_id": "123456",
            "password": "secret_password",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["telegram_chat_id"] == "123456"


def test_get_users(client: TestClient, create_test_token):
    # First create a user - need token for this too
    token = create_test_token()
    client.post(
        "/api/v1/users/",
        json={
            "name": "Test User",
            "telegram_chat_id": "123456",
            "password": "secret_password",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    # Then get all users
    response = client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_user_by_id(client: TestClient, create_test_token):
    # Create a user first
    token = create_test_token()
    create_response = client.post(
        "/api/v1/users/",
        json={
            "name": "Test User",
            "telegram_chat_id": "123456",
            "password": "secret_password",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = create_response.json()["id"]

    # Get the user by ID
    response = client.get(
        f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"


def test_update_user(client: TestClient, create_test_token):
    # Create a user first
    token = create_test_token()
    create_response = client.post(
        "/api/v1/users/",
        json={
            "name": "Test User",
            "telegram_chat_id": "123456",
            "password": "secret_password",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = create_response.json()["id"]

    # Update the user
    response = client.put(
        f"/api/v1/users/{user_id}",
        json={
            "name": "Updated User",
            "telegram_chat_id": "654321",
            "password": "secret_password",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User"
    assert data["telegram_chat_id"] == "654321"


def test_delete_user(client: TestClient, create_test_token):
    # Create a user first
    token = create_test_token()
    create_response = client.post(
        "/api/v1/users/",
        json={
            "name": "Test User",
            "telegram_chat_id": "123456",
            "password": "secret_password",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = create_response.json()["id"]

    # Delete the user
    response = client.delete(
        f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"
