from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    telegram_chat_id: str | None = None


class UserCreate(UserBase):
    password: str
    name: str


class UserUpdate(UserBase):
    name: str | None = None


class User(UserBase):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)  # pyright: ignore[reportUnannotatedClassAttribute]
