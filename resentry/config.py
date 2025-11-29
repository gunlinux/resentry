from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./resentry.db"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    SALT: bytes = b"$2b$12$gj7lkAtmwGLm8W8Wg50h6."

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RESENTRY_",
        case_sensitive=False,
    )  # pyright: ignore[reportUnannotatedClassAttribute]


settings = Settings()
