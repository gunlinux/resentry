from dataclasses import dataclass


@dataclass
class UserDTO:
    id: int
    name: str
    telegram_chat_id: str | None = None
    password: str | None = None  # Usually we don't expose passwords in DTOs
