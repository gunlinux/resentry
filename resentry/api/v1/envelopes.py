from typing import List
import typing
from fastapi import APIRouter, Depends, HTTPException, Request, Path, Header
import datetime

from resentry.api.deps import get_router_repo
from resentry.repos.project import ProjectRepository
from resentry.repos.envelope import EnvelopeItemRepository, EnvelopeRepository
from resentry.database.models.envelope import Envelope as EnvelopeModel, EnvelopeItem
from resentry.database.models.project import Project as ProjectModel
from resentry.database.schemas.envelope import Envelope as EnvelopeSchema
from resentry.sentry import unpack_sentry_envelope_from_request_async

envelopes_router = APIRouter()
project_repo = get_router_repo(ProjectRepository)
envelope_repo = get_router_repo(EnvelopeRepository)
envelope_item_repo = get_router_repo(EnvelopeItemRepository)


async def load_and_check_project(
    project_id: int = Path(...),
    x_sentry_auth: str = Header(...),
    repo: ProjectRepository = Depends(project_repo),
) -> ProjectModel:
    project = typing.cast(ProjectModel | None, await repo.get_by_id(project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if f"sentry_key={project.key}" not in x_sentry_auth:
        raise HTTPException(status_code=403, detail="Forbidden")

    return project


@envelopes_router.post("/{project_id}/envelope/")
async def store_envelope(
    request: Request,
    project: ProjectModel = Depends(load_and_check_project),
    repo: ProjectRepository = Depends(envelope_repo),
    repo_items: ProjectRepository = Depends(envelope_item_repo),
):
    # Read the raw body bytes
    body = await request.body()
    content_encoding = request.headers.get("content-encoding", None)

    # Parse the envelope using existing sentry functionality
    try:
        envelope = await unpack_sentry_envelope_from_request_async(
            body, content_encoding
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid envelope format: {str(e)}"
        )

    # Create envelope record in database
    sent_at_str = envelope.headers.get("sent_at")
    sent_at = datetime.datetime.fromisoformat(sent_at_str) if sent_at_str else None

    envelope_db = EnvelopeModel(
        project_id=project.id,
        payload=body,
        event_id=envelope.event_id,
        sent_at=sent_at,
        dsn=envelope.headers.get("dsn"),
    )
    envelope_db = await repo.create(envelope_db)
    for item_id, item in enumerate(envelope.items):
        item_db = EnvelopeItem(
            event_id=typing.cast(int, envelope_db.id),
            item_id=str(item_id),
            payload=item.get_payload_bytes(),
        )
        await repo_items.create(item_db)

    return {"message": "Envelope stored successfully", "envelope_id": envelope_db.id}


@envelopes_router.get("/projects/events", response_model=List[EnvelopeSchema])
async def get_project_events(repo: EnvelopeRepository = Depends(envelope_repo)):
    return await repo.get_all()
