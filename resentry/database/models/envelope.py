from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Envelope(SQLModel, table=True):
    __tablename__ = "envelopes"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    project_id: int = Field(foreign_key="projects.id")
    payload: bytes = Field(sa_column_kwargs={"nullable": False})
    event_id: Optional[str] = Field(default=None)
    sent_at: Optional[datetime] = Field(default=None)
    dsn: Optional[str] = Field(default=None)


class EnvelopeItem(SQLModel, table=True):
    __tablename__ = "envelope_items"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    event_id: int = Field(foreign_key="envelopes.id")
    item_id: str = Field(index=True)
    payload: bytes = Field(sa_column_kwargs={"nullable": False})
