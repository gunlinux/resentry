from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    name: str
    telegram_chat_id: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        from_attributes = True
