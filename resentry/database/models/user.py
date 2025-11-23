from sqlmodel import Field
from resentry.database.models.base import Entity


class User(Entity, table=True):
    __tablename__ = "users"  # type: ignore

    name: str = Field(index=True)
    telegram_chat_id: str | None = Field(default=None)
    password: str = Field(nullable=False)
