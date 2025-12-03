from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
from resentry.database.models.base import Entity


class Envelope(Entity, table=True):
    __tablename__ = "envelopes"  # type: ignore

    project_id: int = Field(foreign_key="projects.id")
    payload: bytes = Field(sa_column_kwargs={"nullable": False})
    event_id: Optional[str] = Field(default=None)
    sent_at: Optional[datetime] = Field(default=None)
    dsn: Optional[str] = Field(default=None)

    items: list["EnvelopeItem"] = Relationship(back_populates="event")


class EnvelopeItem(Entity, table=True):
    __tablename__ = "envelope_items"  # type: ignore

    event_id: int = Field(foreign_key="envelopes.id")
    event: Envelope | None = Relationship(back_populates="items")
    item_id: str = Field(index=True)
    payload: bytes = Field(sa_column_kwargs={"nullable": False})
