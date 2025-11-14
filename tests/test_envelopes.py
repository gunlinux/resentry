from fastapi.testclient import TestClient


def test_store_envelope(client: TestClient):
    # First create a project since envelope requires a project_id
    project_response = client.post(
        "/api/v1/projects/", json={"name": "Test Project", "lang": "python"}
    )
    project_id = project_response.json()["id"]

    # Create a simple envelope payload
    envelope_payload = b'{"event_id": "abc123", "sent_at": "2023-01-01T00:00:00Z"}\n{"type": "event", "length": 20}\n{"message": "test event"}'

    # Store envelope
    response = client.post(f"/api/v1/{project_id}/envelope/", content=envelope_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Envelope stored successfully"
    assert "envelope_id" in data


def test_get_project_events(client: TestClient):
    # First create a project
    project_response = client.post(
        "/api/v1/projects/", json={"name": "Test Project", "lang": "python"}
    )
    project_id = project_response.json()["id"]

    # Create an envelope for this project
    envelope_payload = b'{"event_id": "abc123", "sent_at": "2023-01-01T00:00:00Z"}\n{"type": "event", "length": 20}\n{"message": "test event"}'
    client.post(f"/api/v1/{project_id}/envelope/", content=envelope_payload)

    # Get project events
    response = client.get("/api/projects/events")
    assert response.status_code == 200
    # This endpoint returns the list of envelopes
    assert isinstance(response.json(), list)
