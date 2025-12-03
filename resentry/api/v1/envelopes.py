from typing import List
import typing
from fastapi import APIRouter, Depends, HTTPException, Request, Path, Header

from resentry.api.deps import get_router_repo, get_current_user_id
from resentry.repos.project import ProjectRepository
from resentry.repos.envelope import EnvelopeItemRepository, EnvelopeRepository
from resentry.database.models.project import Project as ProjectModel
from resentry.database.schemas.envelope import EnvelopeResponse
from resentry.usecases.envelope import StoreEnvelope

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
    repo: EnvelopeRepository = Depends(envelope_repo),
    repo_items: EnvelopeItemRepository = Depends(envelope_item_repo),
):
    # Read the raw body bytes
    body = await request.body()
    content_encoding = request.headers.get("content-encoding", None)

    envelope_handler = StoreEnvelope(
        content_encoding=content_encoding,
        body=body,
        repo=repo,
        repo_items=repo_items,
        project_id=project.id,
    )
    envelope_db = await envelope_handler.execute()

    if envelope_db is None:
        raise HTTPException(status_code=400, detail="Invalid envelope format")

    return {"message": "Envelope stored successfully", "envelope_id": envelope_db.id}


@envelopes_router.get(
    "/projects/{project_id}/events", response_model=List[EnvelopeResponse]
)
async def get_project_events(
    project_id: int,
    current_user_id: int = Depends(get_current_user_id),
    repo: EnvelopeRepository = Depends(envelope_repo),
):
    temp = await repo.get_all_by_project(project_id)
    for i in temp:
        print(i.items)
    return temp
