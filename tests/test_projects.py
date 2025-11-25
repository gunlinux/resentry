from fastapi.testclient import TestClient


def test_create_project(client: TestClient, create_test_token):
    token = create_test_token()
    response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "lang": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["lang"] == "python"


def test_get_projects(client: TestClient, create_test_token):
    # First create a project
    token = create_test_token()
    client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "lang": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Then get all projects
    response = client.get(
        "/api/v1/projects/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_project_by_id(client: TestClient, create_test_token):
    # Create a project first
    token = create_test_token()
    create_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "lang": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_response.json()["id"]

    # Get the project by ID
    response = client.get(
        f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"


def test_update_project(client: TestClient, create_test_token):
    # Create a project first
    token = create_test_token()
    create_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "lang": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_response.json()["id"]

    # Update the project
    response = client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated Project", "lang": "javascript"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["lang"] == "javascript"


def test_delete_project(client: TestClient, create_test_token):
    # Create a project first
    token = create_test_token()
    create_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "lang": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_response.json()["id"]

    # Delete the project
    response = client.delete(
        f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"
