from typing import AsyncGenerator, Type

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends


from resentry.database.database import get_async_db
from resentry.repos.project import ProjectRepository, BaseRepo


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


def get_repo(
    repo_cls: Type[BaseRepo],
    db: AsyncSession,
) -> BaseRepo:
    return repo_cls(db)


def get_router_repo(repo_cls: Type[BaseRepo]):
    def inner(db: AsyncSession = Depends(get_async_db_session)):
        return get_repo(repo_cls, db)

    return inner
