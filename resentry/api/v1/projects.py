from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from resentry.api.deps import get_async_db_session
from resentry.database.models.project import Project as ProjectModel
from resentry.database.schemas.project import (
    Project as ProjectSchema,
    ProjectCreate,
    ProjectUpdate,
)

projects_router = APIRouter()


@projects_router.get("/", response_model=List[ProjectSchema])
async def get_projects(db: AsyncSession = Depends(get_async_db_session)):
    result = await db.execute(select(ProjectModel))
    projects = result.all()
    return [project[0] for project in projects]


@projects_router.post("/", response_model=ProjectSchema)
async def create_project(
    project: ProjectCreate, db: AsyncSession = Depends(get_async_db_session)
):
    db_project = ProjectModel(**project.model_dump())
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


@projects_router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    project_id: int, db: AsyncSession = Depends(get_async_db_session)
):
    result = await db.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    project = result.first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project[0]


@projects_router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: AsyncSession = Depends(get_async_db_session),
):
    result = await db.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    db_project = result.first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_project = db_project[0]  # Get the actual project object
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)

    await db.commit()
    await db.refresh(db_project)
    return db_project


@projects_router.delete("/{project_id}")
async def delete_project(
    project_id: int, db: AsyncSession = Depends(get_async_db_session)
):
    result = await db.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    db_project = result.first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_project = db_project[0]  # Get the actual project object
    await db.delete(db_project)
    await db.commit()
    return {"message": "Project deleted successfully"}
