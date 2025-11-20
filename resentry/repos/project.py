"""Repository for Post entities."""

from typing import Sequence
from sqlmodel.ext.asyncio.session import AsyncSession

from resentry.database.models.project import Project
from sqlmodel import select

from fastapi import HTTPException

from resentry.database.schemas.project import ProjectBase


class ProjectRepository:
    """Repository for Post entities."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: int) -> Project | None:
        result = await self.db.exec(select(Project).where(Project.id == id))
        return result.first()

    async def get_all(self) -> Sequence[Project]:
        result = await self.db.exec(select(Project))
        return result.all()

    async def create(self, entity: Project) -> Project:
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, id: int, entity: ProjectBase) -> Project:
        result = await self.db.exec(select(Project).where(Project.id == id))
        db_project = result.first()
        if db_project is None:
            raise HTTPException(status_code=404, detail="Project not found")

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
