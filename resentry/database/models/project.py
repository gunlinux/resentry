from sqlmodel import SQLModel, Field


class Project(SQLModel, table=True):
    __tablename__ = "projects"  # type: ignore

    id: int = Field(primary_key=True, default=None, index=True)
    name: str = Field(index=True)
    lang: str = Field(index=True)
    key: str = Field(max_length=32, nullable=True, default=None)
