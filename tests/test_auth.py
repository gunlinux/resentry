from fastapi.testclient import TestClient

from resentry.database.schemas.auth import (
    TokenSchema,
)


def test_create_user(client: TestClient, create_test_user):
    response = create_test_user
    user_data = {
        "login": "Test User",
        "password": "secret_password",
    }

    response = client.post(
        "/api/v1/auth/login",
        json=user_data,
    )

    tokens = TokenSchema(**response.json())
    user_id = create_test_user.json()["id"]

    response = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {tokens.access_token}"},
    )
    assert response.status_code == 200

    response = client.post(
        "/api/v1/auth/refresh_token",
        json={"refresh_token": tokens.refresh_token},
    )

    new_tokens = TokenSchema(**response.json())

    # Create a user first
    user_id = create_test_user.json()["id"]

    # Get the user by ID
    response = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {new_tokens.access_token}"},
    )
    assert response.status_code == 200
