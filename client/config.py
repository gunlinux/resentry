"""Configuration for Resentry API client."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Config(BaseSettings):
    """Configuration model for the API client."""

    login: str = Field(default_factory=str)
    password: str = Field(default_factory=str)
    api_url: str = "http://localhost:8000"
    tokens: str = "tokens.json"

    model_config = SettingsConfigDict(
        env_prefix="RESENTRYCLI_",
        env_file=".clienv",
        case_sensitive=False,
        cli_ignore_unknown_args=True,
    )
