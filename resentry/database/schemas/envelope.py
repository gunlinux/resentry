from pydantic import BaseModel, ConfigDict
from datetime import datetime


class EnvelopeBase(BaseModel):
    project_id: int
    payload: bytes
    event_id: str | None = None
    sent_at: datetime | None = None
    dsn: str | None = None


class EnvelopeCreate(EnvelopeBase):
    pass


class Envelope(EnvelopeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # pyright: ignore[reportUnannotatedClassAttribute]


class EnvelopeItemBase(BaseModel):
    event_id: int
    item_id: str
    payload: bytes


class EnvelopeResponse(BaseModel):
    id: int
    project_id: int
    event_id: str | None = None
    sent_at: datetime | None = None
    dsn: str | None = None
    items: list["EnvelopeItem"] | None = None


class EnvelopeItemCreate(EnvelopeItemBase):
    pass


class EnvelopeItem(EnvelopeItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # pyright: ignore[reportUnannotatedClassAttribute]
