from fastapi import APIRouter, Depends, HTTPException

from resentry.api.deps import (
    get_router_repo,
)
from resentry.database.schemas.project import (
    Project as ProjectSchema,
    ProjectCreate,
    ProjectUpdate,
)
from resentry.repos.project import ProjectRepository
from resentry.usecases.project import CreateProject

projects_router = APIRouter()
repo_dep = get_router_repo(ProjectRepository)


@projects_router.get("/", response_model=list[ProjectSchema])
async def get_projects(repo: ProjectRepository = Depends(repo_dep)):
    return await repo.get_all()


@projects_router.post("/", response_model=ProjectSchema)
async def create_project(
    project: ProjectCreate, repo: ProjectRepository = Depends(repo_dep)
):
    return await CreateProject(body=project, repo=repo).execute()


@projects_router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(project_id: int, repo: ProjectRepository = Depends(repo_dep)):
    project = await repo.get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@projects_router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    repo: ProjectRepository = Depends(repo_dep),
):
    update_project = await repo.update(project_id, project)
    if update_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return update_project


@projects_router.delete("/{project_id}")
async def delete_project(project_id: int, repo: ProjectRepository = Depends(repo_dep)):
    await repo.delete(id=project_id)
    return {"message": "Project deleted successfully"}
