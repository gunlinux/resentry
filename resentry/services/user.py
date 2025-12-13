from dataclasses import dataclass
import typing

from resentry.repos.user import UserRepository
from resentry.database.models.user import User
from resentry.domain.user import UserDTO


@dataclass
class UserService:
    repo: UserRepository

    async def get_user_by_id(self, user_id: int) -> UserDTO | None:
        if user := typing.cast(User | None, await self.repo.get_by_id(user_id)):
            return UserDTO(
                id=user.id,
                name=user.name,
                telegram_chat_id=user.telegram_chat_id,
                password=None,  # Never expose password in DTOs
            )
        return None

    async def get_all(self) -> list[UserDTO]:
        out = []
        for user in await self.repo.get_all():
            user = typing.cast(User, user)
            out.append(
                UserDTO(
                    id=user.id,
                    name=user.name,
                    telegram_chat_id=user.telegram_chat_id,
                    password=None,  # Never expose password in DTOs
                )
            )
        return out

    async def get_user_by_name(self, name: str) -> UserDTO | None:
        if user := await self.repo.get_by_name(name):
            return UserDTO(
                id=user.id,
                name=user.name,
                telegram_chat_id=user.telegram_chat_id,
                password=None,  # Never expose password in DTOs
            )
        return None
