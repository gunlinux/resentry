"""Tests for the Resentry API client."""

import pytest
from unittest.mock import Mock, patch
from client.api_client import ResentryAPIClient
from client.config import Config


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
