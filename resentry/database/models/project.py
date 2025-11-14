from sqlmodel import SQLModel, Field
from typing import Optional


class Project(SQLModel, table=True):
    __tablename__ = "projects"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True)
    lang: str = Field(index=True)
