from fastapi import APIRouter, Depends

from resentry.api.deps import get_router_repo
from resentry.core.hashing import Hasher
from resentry.database.schemas.auth import (
    LoginSchema,
    RefreshTokenSchema,
    TokenSchema,
)
from resentry.repos.user import UserRepository
from resentry.config import settings
from resentry.usecases.auth import Login, RefreshToken

auth_router = APIRouter()
repo_dep = get_router_repo(UserRepository)


@auth_router.post("/login", response_model=TokenSchema)
async def login_route(body: LoginSchema, repo: UserRepository = Depends(repo_dep)):
    return await Login(repo=repo, hasher=Hasher(salt=settings.SALT)).execute(body)


@auth_router.post("/refresh_token", response_model=TokenSchema)
async def refresh_token_route(refresh_token: RefreshTokenSchema):
    return await RefreshToken().execute(refresh_token)
