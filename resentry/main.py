from typing import List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from resentry.api.v1.router import api_router
from resentry.api.v1.router import sentry_router
from resentry.api.health import health_router
from resentry.database.models.envelope import Envelope as EnvelopeModel
from resentry.database.schemas.envelope import Envelope as EnvelopeSchema
from resentry.api.deps import get_async_db_session, get_current_user_id


def create_app() -> FastAPI:
    app = FastAPI(
        title="Resentry API",
        description="A FastAPI application for Sentry envelope storage and processing",
        version="0.1.0",
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
    app.include_router(sentry_router, prefix="/api", tags=["api"])

    # Add the specific endpoint for getting all project events
    @app.get(
        "/api/projects/events", response_model=List[EnvelopeSchema], tags=["envelopes"]
    )
    async def get_project_events(
        current_user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_async_db_session),
    ):
        result = await db.execute(select(EnvelopeModel))
        envelopes = result.all()
        return [envelope[0] for envelope in envelopes]

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("resentry.main:app", host="0.0.0.0", port=8000, reload=True)
