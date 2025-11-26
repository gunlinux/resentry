import pytest
from fastapi.testclient import TestClient


def test_create_user(client: TestClient, create_test_user):
    response = create_test_user
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["telegram_chat_id"] == "123456"


def test_get_users(client: TestClient, create_test_token, create_test_user):
    # First create a user - need token for this too
    token = create_test_token()
    # Then get all users
    response = client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_user_by_id(client: TestClient, create_test_token, create_test_user):
    # Create a user first
    token = create_test_token()
    user_id = create_test_user.json()["id"]

    # Get the user by ID
    response = client.get(
        f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"


def test_get_wrong_user_by_id(client: TestClient, create_test_token, create_test_user):
    # Create a user first
    token = create_test_token()

    # Get the user by ID
    response = client.get(
        "/api/v1/users/999", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_update_user(client: TestClient, create_test_token, create_test_user):
    # Create a user first
    token = create_test_token()
    user_id = create_test_user.json()["id"]

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


@pytest.mark.parametrize(
    "user_id,status",
    [
        (1, 200),
        (999, 200),
    ],
)
def test_delete_user(
    client: TestClient, user_id, status, create_test_token, create_test_user
):
    # Create a user first
    token = create_test_token()

    # Delete the user
    response = client.delete(
        f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status
    assert response.json()["message"] == "User deleted successfully"
