from fastapi.testclient import TestClient


def test_store_envelope(client: TestClient, create_test_token):
    # First create a project since envelope requires a project_id
    token = create_test_token()
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "lang": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_data = project_response.json()
    project_id = project_data["id"]
    project_key = project_data["key"]

    # Create a simple envelope payload
    envelope_payload = b'{"event_id": "abc123", "sent_at": "2023-01-01T00:00:00Z"}\n{"type": "event", "length": 20}\n{"message": "test event"}'

    # Store envelope with required x-sentry-auth header
    headers = {"x-sentry-auth": f"Sentry sentry_key={project_key}, sentry_version=7"}
    response = client.post(
        f"/api/{project_id}/envelope/", content=envelope_payload, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Envelope stored successfully"
    assert "envelope_id" in data


def test_get_project_events(client: TestClient, create_test_token):
    token = create_test_token()
    # First create a project
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "lang": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_data = project_response.json()
    project_id = project_data["id"]
    project_key = project_data["key"]

    # Create an envelope for this project
    envelope_payload = b'{"event_id": "abc123", "sent_at": "2023-01-01T00:00:00Z"}\n{"type": "event", "length": 20}\n{"message": "test event"}'
    headers = {"x-sentry-auth": f"Sentry sentry_key={project_key}, sentry_version=7"}
    client.post(
        f"/api/v1/{project_id}/envelope/", content=envelope_payload, headers=headers
    )

    # Get project events
    response = client.get(
        f"/api/projects/{project_id}/events",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    # This endpoint returns the list of envelopes
    assert isinstance(response.json(), list)
