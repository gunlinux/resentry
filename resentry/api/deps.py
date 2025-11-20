from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends


from resentry.database.database import get_async_db
from resentry.repos.project import ProjectRepository


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for db in get_async_db():
        try:
            yield db
        finally:
            await db.close()


async def get_repo_project(
    db: AsyncSession = Depends(get_async_db_session),
) -> ProjectRepository:
    return ProjectRepository(db)
