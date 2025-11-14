from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True)
    telegram_chat_id: str | None = Field(default=None)
