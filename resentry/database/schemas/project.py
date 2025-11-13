from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    lang: str


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True
