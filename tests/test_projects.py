from fastapi.testclient import TestClient
from resentry.main import app


def test_create_project():
    with TestClient(app) as client:
        response = client.post("/api/v1/projects/", json={"name": "Test Project", "lang": "python"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["lang"] == "python"


def test_get_projects():
    with TestClient(app) as client:
        # First create a project
        client.post("/api/v1/projects/", json={"name": "Test Project", "lang": "python"})
        # Then get all projects
        response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_project_by_id():
    with TestClient(app) as client:
        # Create a project first
        create_response = client.post("/api/v1/projects/", json={"name": "Test Project", "lang": "python"})
        project_id = create_response.json()["id"]
        
        # Get the project by ID
        response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"


def test_update_project():
    with TestClient(app) as client:
        # Create a project first
        create_response = client.post("/api/v1/projects/", json={"name": "Test Project", "lang": "python"})
        project_id = create_response.json()["id"]
        
        # Update the project
        response = client.put(f"/api/v1/projects/{project_id}", 
                               json={"name": "Updated Project", "lang": "javascript"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["lang"] == "javascript"


def test_delete_project():
    with TestClient(app) as client:
        # Create a project first
        create_response = client.post("/api/v1/projects/", json={"name": "Test Project", "lang": "python"})
        project_id = create_response.json()["id"]
        
        # Delete the project
        response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"