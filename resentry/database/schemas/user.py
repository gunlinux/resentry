from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    name: str
    telegram_chat_id: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    name: str | None = None


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # pyright: ignore[reportUnannotatedClassAttribute]
