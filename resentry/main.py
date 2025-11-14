from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from resentry.api.v1.router import api_router
from resentry.api.health import health_router
from resentry.database.database import async_engine, Base, sync_engine
from resentry.config import settings
from resentry.database.models.envelope import Envelope as EnvelopeModel
from resentry.database.schemas.envelope import Envelope as EnvelopeSchema
from resentry.api.deps import get_async_db_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    print("lifespan start")

    print(settings.DATABASE_URL)

    if settings.DATABASE_URL.startswith("sqlite+aiosqlite"):
        print("create_ async engine")
        # For async engine (production)
        async with async_engine.begin() as conn:
            print("metadata create")
            await conn.run_sync(Base.metadata.create_all)
    else:
        print("sync bd create")
        # For sync engine (testing)
        Base.metadata.create_all(bind=sync_engine)
    yield
    # Perform any cleanup on shutdown if needed


def create_app() -> FastAPI:
    app = FastAPI(
        title="Resentry API",
        description="A FastAPI application for Sentry envelope storage and processing",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, be more restrictive
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(api_router, prefix="/api/v1", tags=["api"])

    # Add the specific endpoint for getting all project events
    @app.get(
        "/api/projects/events", response_model=List[EnvelopeSchema], tags=["envelopes"]
    )
    async def get_project_events(db: AsyncSession = Depends(get_async_db_session)):
        result = await db.execute(select(EnvelopeModel))
        envelopes = result.all()
        return [envelope[0] for envelope in envelopes]

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("resentry.main:app", host="0.0.0.0", port=8000, reload=True)
