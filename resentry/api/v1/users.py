from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from resentry.api.deps import get_async_db_session
from resentry.database.models.user import User as UserModel
from resentry.database.schemas.user import User as UserSchema, UserCreate, UserUpdate

users_router = APIRouter()


@users_router.get("/", response_model=List[UserSchema])
async def get_users(db: AsyncSession = Depends(get_async_db_session)):
    result = await db.execute(select(UserModel))
    users = result.all()
    return [user[0] for user in users]


@users_router.post("/", response_model=UserSchema)
async def create_user(
    user: UserCreate, db: AsyncSession = Depends(get_async_db_session)
):
    db_user = UserModel(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@users_router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db_session)):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user[0]


@users_router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_async_db_session)
):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    db_user = result.first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user = db_user[0]  # Get the actual user object
    for key, value in user.model_dump().items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


@users_router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_db_session)):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    db_user = result.first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user = db_user[0]  # Get the actual user object
    await db.delete(db_user)
    await db.commit()
    return {"message": "User deleted successfully"}
