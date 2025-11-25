from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from resentry.api.v1.router import api_router
from resentry.api.v1.router import sentry_router
from resentry.api.health import health_router


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

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("resentry.main:app", host="0.0.0.0", port=8000, reload=True)
