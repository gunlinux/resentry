from typing import Sequence, ClassVar

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel

from resentry.database.models.base import Entity


class BaseRepo:
    entity_type: ClassVar[type[Entity]] = Entity

    def __init__(self, db: AsyncSession):
        if self.entity_type is None:
            raise Exception()
        self.db = db

    async def get_by_id(self, id: int) -> SQLModel | None:
        result = await self.db.exec(
            select(self.entity_type).where(self.entity_type.id == id)
        )
        return result.first()

    async def get_all(self) -> Sequence[Entity]:
        result = await self.db.exec(select(self.entity_type))
        return result.all()

    async def create(self, entity: Entity) -> Entity:
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def update(self, id: int, entity: BaseModel) -> Entity | None:
        result = await self.db.exec(
            select(self.entity_type).where(self.entity_type.id == id)
        )
        db_entity = result.first()
        if db_entity is None:
            return None

        for key, value in entity.model_dump().items():
            setattr(db_entity, key, value)

        await self.db.flush()
        return db_entity

    async def delete(self, id: int) -> bool:
        result = await self.db.exec(
            select(self.entity_type).where(self.entity_type.id == id)
        )
        db_entity = result.first()
        if db_entity is None:
            return False

        await self.db.delete(db_entity)
        await self.db.flush()
        return True
