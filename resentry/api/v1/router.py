from fastapi import APIRouter

from resentry.api.v1 import users, projects, envelopes, auth

api_router = APIRouter()
api_router.include_router(users.users_router, prefix="/users", tags=["users"])
api_router.include_router(
    projects.projects_router, prefix="/projects", tags=["projects"]
)
api_router.include_router(auth.auth_router, prefix="/auth", tags=["auth"])

sentry_router = APIRouter()
sentry_router.include_router(envelopes.envelopes_router, tags=["envelopes"])
