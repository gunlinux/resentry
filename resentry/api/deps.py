from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


from resentry.database.database import get_async_db


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for db in get_async_db():
        try:
            yield db
        finally:
            await db.close()
