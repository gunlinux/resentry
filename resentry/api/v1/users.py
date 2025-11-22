from typing import List
from fastapi import APIRouter, Depends, HTTPException

from resentry.api.deps import get_router_repo
from resentry.database.models.user import User as UserModel
from resentry.database.schemas.user import User as UserSchema, UserCreate, UserUpdate
from resentry.repos.user import UserRepository

users_router = APIRouter()
repo_dep = get_router_repo(UserRepository)


@users_router.get("/", response_model=List[UserSchema])
async def get_users(repo: UserRepository = Depends(repo_dep)):
    return await repo.get_all()


@users_router.post("/", response_model=UserSchema)
async def create_user(user: UserCreate, repo: UserRepository = Depends(repo_dep)):
    new_user = UserModel(**user.model_dump())
    return await repo.create(new_user)


@users_router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, repo: UserRepository = Depends(repo_dep)):
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@users_router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int, user: UserUpdate, repo: UserRepository = Depends(repo_dep)
):
    update_user = await repo.update(user_id, user)
    if update_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return update_user


@users_router.delete("/{user_id}")
async def delete_user(user_id: int, repo: UserRepository = Depends(repo_dep)):
    await repo.delete(user_id)
    return {"message": "User deleted successfully"}
