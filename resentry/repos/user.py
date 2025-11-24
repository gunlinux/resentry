from resentry.repos.base import BaseRepo
from resentry.database.models.user import User
from sqlmodel import select


class UserRepository(BaseRepo):
    entity_type = User

    async def get_by_name(self, name: str) -> User | None:
        result = await self.db.exec(select(User).where(User.name == name))
        return result.first()
