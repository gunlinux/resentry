"""Data models for Resentry API client."""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class HealthCheck(BaseModel):
    """Health check response model."""

    status: str = "OK"


class LoginSchema(BaseModel):
    """Login request model."""

    login: str
    password: str


class RefreshTokenSchema(BaseModel):
    """Refresh token request model."""

    refresh_token: str


class TokenSchema(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str


class User(BaseModel):
    """User model."""

    id: int
    name: str
    telegram_chat_id: Optional[str] = None


class UserCreate(BaseModel):
    """User creation model."""

    name: str
    telegram_chat_id: Optional[str] = None
    password: str


class UserUpdate(BaseModel):
    """User update model."""

    name: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class Project(BaseModel):
    """Project model."""

    id: int
    name: str
    lang: str
    key: str


class ProjectCreate(BaseModel):
    """Project creation model."""

    name: str
    lang: str


class ProjectUpdate(BaseModel):
    """Project update model."""

    name: str
    lang: str


class Envelope(BaseModel):
    """Envelope model."""

    id: int
    project_id: int
    # payload: str  # This might be binary data in practice
    event_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    dsn: Optional[str] = None
