from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from resentry.api.deps import get_db_session
from resentry.database.models.project import Project as ProjectModel
from resentry.database.schemas.project import Project as ProjectSchema, ProjectCreate, ProjectUpdate

projects_router = APIRouter()


@projects_router.get("/", response_model=List[ProjectSchema])
def get_projects(db: Session = Depends(get_db_session)):
    projects = db.query(ProjectModel).all()
    return projects


@projects_router.post("/", response_model=ProjectSchema)
def create_project(project: ProjectCreate, db: Session = Depends(get_db_session)):
    db_project = ProjectModel(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@projects_router.get("/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(get_db_session)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@projects_router.put("/{project_id}", response_model=ProjectSchema)
def update_project(
    project_id: int, project: ProjectUpdate, db: Session = Depends(get_db_session)
):
    db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


@projects_router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db_session)):
    db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}