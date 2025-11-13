from fastapi import APIRouter
from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str = "OK"


health_router = APIRouter()


@health_router.get("/", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="OK")
