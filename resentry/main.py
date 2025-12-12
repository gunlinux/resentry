import asyncio
from contextlib import asynccontextmanager
from asyncio import Queue

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from resentry.api.v1.router import api_router
from resentry.api.v1.router import sentry_router
from resentry.api.health import health_router
from resentry.core.events import EventWorker, send_telegram
from resentry.domain.queue import LogLevel
import logging


def create_app(lifespan) -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    queue = Queue()

    event_worker = EventWorker()
    event_worker.register(LogLevel.error, send_telegram)
    logging.info("lifespan registed events  %s", event_worker.events)

    async def worker():
        while True:
            item = await queue.get()
            if item is not None:
                logging.info("got new item %s", item)
                await event_worker.process_event(item)
            # finally:
            #    queue.task_done()
            await asyncio.sleep(0.1)

    worker_task = asyncio.create_task(worker())
    app.state.queue = queue

    yield

    worker_task.cancel()

    try:
        await worker_task
    except asyncio.CancelledError:
        pass


app = create_app(lifespan=lifespan)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("resentry.main:app", host="0.0.0.0", port=8000, reload=True)
