"""API client for Resentry service."""

from typing import List
from http import HTTPStatus
import json
from client.http_client import HttpClient


from client.models import (
    User,
    UserCreate,
    UserUpdate,
    Project,
    ProjectCreate,
    ProjectUpdate,
    Envelope,
    TokenSchema,
    LoginSchema,
    RefreshTokenSchema,
    HealthCheck,
)
from client.exceptions import LoginError
from client.config import Config


class ResentryAPIClient:
    """Client for interacting with the Resentry API."""

    def __init__(self, config: Config):
        self.config = config
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self._client = HttpClient(
            base_url=config.api_url,
            timeout=30.0,
            reauth=self._reauth,
        )

        temp_tokens = self._load_tokens()
        if not temp_tokens:
            tokens = self.login(self.config.login, self.config.password)
            if tokens is None:
                raise LoginError("Cant login")
            self._safe_tokens(tokens)
        else:
            self.access_token = temp_tokens.access_token
            self.refresh_token = temp_tokens.refresh_token

        # Add authorization header if token is available
        if self.access_token:
            self._client.update_header("Authorization", f"Bearer {self.access_token}")

    def _reauth(self) -> None:
        if self.refresh_token:
            if tokens := self.refresh_token_call(self.refresh_token):
                self._safe_tokens(tokens)
                return
        if tokens := self.login(self.config.login, self.config.password):
            self._safe_tokens(tokens)

    def _load_tokens(self) -> TokenSchema | None:
        try:
            with open(self.config.tokens, "r") as f:
                tokens = json.load(f)
                return TokenSchema(**tokens)
        except FileNotFoundError:
            return None

    def _safe_tokens(self, new_tokens: TokenSchema) -> None:
        with open(self.config.tokens, "w") as f:
            json.dump(new_tokens.model_dump(), f)

    def _add_auth_header(self):
        """Add authorization header if token is available."""
        if self.access_token:
            self._client.update_header("Authorization", f"Bearer {self.access_token}")

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def login(self, login: str, password: str) -> TokenSchema | None:
        """Authenticate with the API."""
        login_data = LoginSchema(login=login, password=password)
        response = self._client.post("/api/v1/auth/login", json=login_data.model_dump())

        if response.status_code == HTTPStatus.OK:
            token_data = response.json()
            # Update the config with new tokens
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            # Update the client headers
            self._add_auth_header()
            return TokenSchema(**token_data)
        return None

    def refresh_token_call(self, refresh_token: str) -> TokenSchema | None:
        """Refresh the authentication token."""
        token_data = RefreshTokenSchema(refresh_token=refresh_token)
        response = self._client.post(
            "/api/v1/auth/refresh_token", json=token_data.model_dump(), retry=False,
        )

        if response.status_code == HTTPStatus.OK:
            new_tokens = response.json()
            # Update the config with new tokens
            self.access_token = new_tokens.get("access_token")
            self.refresh_token = new_tokens.get("refresh_token")
            # Update the client headers
            self._add_auth_header()
            return TokenSchema(**new_tokens)
        else:
            return None

    def health_check(self) -> HealthCheck | None:
        """Check the health of the API."""
        response = self._client.get("/health/")

        if response.status_code == HTTPStatus.OK:
            return HealthCheck(**response.json())
        else:
            response.raise_for_status()

    # User management methods
    def get_users(self) -> List[User] | None:
        """Get all users."""
        response = self._client.get("/api/v1/users/")

        if response.status_code == HTTPStatus.OK:
            users_data = response.json()
            return [User(**user_data) for user_data in users_data]
        else:
            response.raise_for_status()

    def get_user(self, user_id: int) -> User | None:
        """Get a specific user by ID."""
        response = self._client.get(f"/api/v1/users/{user_id}")

        if response.status_code == HTTPStatus.OK:
            return User(**response.json())
        else:
            response.raise_for_status()

    def create_user(self, user_create: UserCreate) -> User | None:
        """Create a new user."""
        response = self._client.post("/api/v1/users/", json=user_create.model_dump())

        if response.status_code == HTTPStatus.OK:
            return User(**response.json())
        else:
            response.raise_for_status()

    def update_user(self, user_id: int, user_update: UserUpdate) -> User | None:
        """Update a user."""
        response = self._client.put(f"/api/v1/users/{user_id}", json=user_update.model_dump())

        if response.status_code == HTTPStatus.OK:
            return User(**response.json())
        else:
            response.raise_for_status()

    def delete_user(self, user_id: int):
        """Delete a user."""
        response = self._client.delete(f"/api/v1/users/{user_id}")

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

    # Project management methods
    def get_projects(self) -> List[Project] | None:
        """Get all projects."""
        response = self._client.get("/api/v1/projects/")

        if response.status_code == HTTPStatus.OK:
            projects_data = response.json()
            return [Project(**project_data) for project_data in projects_data]
        else:
            response.raise_for_status()

    def get_project(self, project_id: int) -> Project | None:
        """Get a specific project by ID."""
        response = self._client.get(f"/api/v1/projects/{project_id}")

        if response.status_code == HTTPStatus.OK:
            return Project(**response.json())
        else:
            response.raise_for_status()

    def create_project(self, project_create: ProjectCreate) -> Project | None:
        """Create a new project."""
        response = self._client.post("/api/v1/projects/", json=project_create.model_dump())

        if response.status_code == HTTPStatus.OK:
            return Project(**response.json())
        else:
            response.raise_for_status()

    def update_project(
        self, project_id: int, project_update: ProjectUpdate
    ) -> Project | None:
        """Update a project."""
        response = self._client.put(
            f"/api/v1/projects/{project_id}", json=project_update.model_dump()
        )

        if response.status_code == HTTPStatus.OK:
            return Project(**response.json())
        else:
            response.raise_for_status()

    def delete_project(self, project_id: int):
        """Delete a project."""
        response = self._client.delete(f"/api/v1/projects/{project_id}")

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

    # Event/envelope methods
    def get_project_events(self) -> List[Envelope] | None:
        """Get all project events."""
        response = self._client.get("/api/projects/events")

        if response.status_code == HTTPStatus.OK:
            envelopes_data = response.json()
            return [Envelope(**envelope_data) for envelope_data in envelopes_data]
        else:
            response.raise_for_status()

    def get_v1_project_events(self) -> List[Envelope] | None:
        """Get all v1 project events."""
        response = self._client.get("/api/v1/projects/events")

        if response.status_code == HTTPStatus.OK:
            envelopes_data = response.json()
            return [Envelope(**envelope_data) for envelope_data in envelopes_data]
        else:
            response.raise_for_status()
