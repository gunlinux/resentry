from sqlmodel import Field
from resentry.database.models.base import Entity


class Project(Entity, table=True):
    __tablename__ = "projects"  # type: ignore

    name: str = Field(index=True)
    lang: str = Field(index=True)
    key: str = Field(max_length=32, nullable=True, default=None)
