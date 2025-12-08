import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    TELEGRAM_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RESENTRY_",
        case_sensitive=False,
        extra="ignore",
    )  # pyright: ignore[reportUnannotatedClassAttribute]


class DevSettings(Settings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./resentry.db"
    SECRET_KEY: str = "your-secret-key-here"
    SALT: bytes = b"$2b$12$gj7lkAtmwGLm8W8Wg50h6."


class ProdSettings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SALT: bytes


class TestSettings(Settings):
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    SECRET_KEY: str = "your-secret-key-here"
    SALT: bytes = b"$2b$12$gj7lkAtmwGLm8W8Wg50h6."
    model_config = SettingsConfigDict(
        extra="ignore",
    )  # pyright: ignore[reportUnannotatedClassAttribute]


settings_envs = {
    "dev": DevSettings,
    "prod": ProdSettings,
    "test": TestSettings,
}

settings = settings_envs[os.getenv("RESENTRY_ENV", "dev")]()
