"""Tests for the Resentry API client."""

import pytest
from unittest.mock import Mock, patch
from client.api_client import ResentryAPIClient
from client.config import Config
from client.models import User, Project, HealthCheck


@pytest.fixture
def config():
    """Sample configuration for testing."""
    return Config()  # api_url="http://testserver", login="loki", password="123123")


@pytest.fixture
def mock_client(config):
    """Mock API client for testing."""
    with patch("client.http_client.httpx.Client") as MockHttpxClient:
        # Create a mock client instance with necessary attributes
        mock_client_instance = Mock()
        mock_client_instance.headers = {}

        # Mock the Client constructor to return our mock instance
        MockHttpxClient.return_value = mock_client_instance

        api_client = ResentryAPIClient(config)
        yield api_client, mock_client_instance


def test_health_check(mock_client):
    """Test health check method."""
    api_client, httpx_client = mock_client

    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "OK"}
    httpx_client.get.return_value = mock_response

    result = api_client.health_check()

    assert isinstance(result, HealthCheck)
    assert result.status == "OK"
    httpx_client.get.assert_called_once_with("/health/")


def test_get_users(mock_client):
    """Test get_users method."""
    api_client, httpx_client = mock_client

    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "name": "User 1", "telegram_chat_id": "123"},
        {"id": 2, "name": "User 2", "telegram_chat_id": "456"},
    ]
    httpx_client.get.return_value = mock_response

    users = api_client.get_users()

    assert len(users) == 2
    assert all(isinstance(user, User) for user in users)
    assert users[0].name == "User 1"
    assert users[1].name == "User 2"
    httpx_client.get.assert_called_once_with("/api/v1/users/")


def test_get_projects(mock_client):
    """Test get_projects method."""
    api_client, httpx_client = mock_client

    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "name": "Project 1", "lang": "python", "key": "key1"},
        {"id": 2, "name": "Project 2", "lang": "javascript", "key": "key2"},
    ]
    httpx_client.get.return_value = mock_response

    projects = api_client.get_projects()
    print(projects)

    assert len(projects) == 2
    assert all(isinstance(proj, Project) for proj in projects)
    assert projects[0].name == "Project 1"
    assert projects[1].lang == "javascript"
    httpx_client.get.assert_called_once_with("/api/v1/projects/")
