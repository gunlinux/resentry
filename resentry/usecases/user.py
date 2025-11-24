from dataclasses import dataclass
import typing

from resentry.database.schemas.user import UserCreate
from resentry.database.models.user import User
from resentry.repos.user import UserRepository
from resentry.core.hashing import Hasher


@dataclass(frozen=True)
class CreateUser:
    repo: UserRepository
    hasher: Hasher

    def _get_password_hash(self, password: str):
        return self.hasher.generate_hash(password)

    async def execute(self, body: UserCreate) -> User:
        user_db = User(**body.model_dump())
        user_db.password = self._get_password_hash(user_db.password)
        return typing.cast("User", await self.repo.create(user_db))
