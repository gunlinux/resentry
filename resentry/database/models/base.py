from sqlmodel import SQLModel, Field


class Entity(SQLModel):
    id: int = Field(primary_key=True, default=None, index=True)
