from typing import AsyncGenerator, Type
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession


from resentry.database.database import get_async_db
from resentry.repos.project import BaseRepo
from resentry.config import settings


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for db in get_async_db():
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()


def get_repo(
    repo_cls: Type[BaseRepo],
    db: AsyncSession,
) -> BaseRepo:
    return repo_cls(db)


security_scheme = HTTPBearer()


def get_router_repo(repo_cls: Type[BaseRepo]):
    def inner(db: AsyncSession = Depends(get_async_db_session)):
        return get_repo(repo_cls, db)

    return inner


async def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return int(user_id_str)  # Convert back to int for use in the application
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(current_user_id: int = Depends(verify_access_token)) -> int:
    """Dependency to get the current user ID from the token."""
    return current_user_id
