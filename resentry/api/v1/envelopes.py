from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Path, Header
from asyncio import Queue

from resentry.api.deps import get_router_repo, get_current_user_id, get_queue
from resentry.repos.project import ProjectRepository
from resentry.repos.user import UserRepository
from resentry.repos.envelope import EnvelopeItemRepository, EnvelopeRepository
from resentry.domain.project import ProjectDTO
from resentry.services.project import ProjectService
from resentry.services.user import UserService
from resentry.database.schemas.envelope import EnvelopeResponse
from resentry.usecases.envelope import StoreEnvelope
from resentry.usecases.events import ScheduleEnvelope

envelopes_router = APIRouter()
project_repo = get_router_repo(ProjectRepository)
envelope_repo = get_router_repo(EnvelopeRepository)
envelope_item_repo = get_router_repo(EnvelopeItemRepository)
users_repo = get_router_repo(UserRepository)


async def load_and_check_project(
    project_id: int = Path(...),
    x_sentry_auth: str = Header(...),
    repo: ProjectRepository = Depends(project_repo),
) -> ProjectDTO:
    project_service = ProjectService(repo=repo)
    project = await project_service.get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if f"sentry_key={project.key}" not in x_sentry_auth:
        raise HTTPException(status_code=403, detail="Forbidden")

    return project


@envelopes_router.post("/{project_id}/envelope/")
async def store_envelope(
    request: Request,
    project: ProjectDTO = Depends(load_and_check_project),
    repo: EnvelopeRepository = Depends(envelope_repo),
    repo_items: EnvelopeItemRepository = Depends(envelope_item_repo),
    repo_users: UserRepository = Depends(users_repo),
    queue: Queue = Depends(get_queue),
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

    # Check if envelope_db.items exists and is iterable before the loop
    user_service = UserService(repo=repo_users)

    if user_dtos := await user_service.get_all():
        await ScheduleEnvelope(queue=queue, project=project, users=user_dtos).execute(
            envelope_db
        )

    return {"message": "Envelope stored successfully", "envelope_id": envelope_db.id}


@envelopes_router.get(
    "/projects/{project_id}/events", response_model=List[EnvelopeResponse]
)
async def get_project_events(
    project_id: int,
    _: int = Depends(get_current_user_id),
    repo: EnvelopeRepository = Depends(envelope_repo),
):
    return await repo.get_all_by_project(project_id)
