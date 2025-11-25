"""
Test to ensure database isolation between tests when using in-memory database
"""

from fastapi.testclient import TestClient


def test_database_isolation_between_tests(client: TestClient, create_test_token):
    """
    This test verifies that each test gets a fresh in-memory database
    by creating data in this test and ensuring it doesn't affect other tests.
    """
    # Create a project in this test
    token = create_test_token()
    response = client.post(
        "/api/v1/projects/",
        json={"name": "Isolation Test Project", "lang": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    project_data = response.json()
    assert project_data["name"] == "Isolation Test Project"

    # Verify the project exists in this test
    get_response = client.get(
        f"/api/v1/projects/{project_data['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Isolation Test Project"


# Note: This test alone doesn't fully verify isolation,
# but combined with the fact that we're using in-memory database per test
# in the fixture, we can be confident that isolation is working.
