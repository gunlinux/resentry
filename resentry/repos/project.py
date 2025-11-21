"""Repository for Post entities."""

from typing import Sequence, Type
from sqlmodel.ext.asyncio.session import AsyncSession

from resentry.database.models.project import Project
from resentry.database.models.base import Entity
from sqlmodel import SQLModel, select

from pydantic import BaseModel

from resentry.database.models.user import User


class BaseRepo:
    def __init__(self, db: AsyncSession, entity: Type[Entity]):
        self.db = db
        self.entity = entity

    async def get_by_id(self, id: int) -> SQLModel | None:
        result = await self.db.exec(select(self.entity).where(self.entity.id == id))
        return result.first()

    async def get_all(self) -> Sequence[Entity]:
        result = await self.db.exec(select(self.entity))
        return result.all()

    async def create(self, entity: Entity) -> Entity:
        self.db.add(entity)
        await self.db.commit()
        return entity

    async def update(self, id: int, entity: BaseModel) -> Entity | None:
        result = await self.db.exec(select(Entity).where(Entity.id == id))
        db_project = result.first()
        if db_project is None:
            return None

        for key, value in entity.model_dump().items():
            setattr(db_project, key, value)

        await self.db.commit()
        await self.db.refresh(db_project)
        return db_project

    async def delete(self, id: int) -> bool:
        result = await self.db.exec(select(Project).where(Project.id == id))
        db_project = result.first()
        if db_project is None:
            return False

        await self.db.delete(db_project)
        await self.db.commit()
        return True


class ProjectRepository(BaseRepo):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Project)


class UserRepository(BaseRepo):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
