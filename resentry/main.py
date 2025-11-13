from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from resentry.api.v1.router import api_router
from resentry.api.health import health_router
from resentry.database.database import async_engine, Base, sync_engine, get_sync_db
from resentry.config import settings
from resentry.database.models.envelope import Envelope as EnvelopeModel
from resentry.database.schemas.envelope import Envelope as EnvelopeSchema


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    if settings.DATABASE_URL.startswith('sqlite+aiosqlite'):
        # For async engine (production)
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
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
    @app.get("/api/projects/events", response_model=List[EnvelopeSchema], tags=["envelopes"])
    def get_project_events(db: Session = Depends(get_sync_db)):
        envelopes = db.query(EnvelopeModel).all()
        return envelopes

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("resentry.main:app", host="0.0.0.0", port=8000, reload=True)