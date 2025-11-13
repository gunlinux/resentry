from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EnvelopeBase(BaseModel):
    project_id: int
    payload: bytes
    event_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    dsn: Optional[str] = None


class EnvelopeCreate(EnvelopeBase):
    pass


class Envelope(EnvelopeBase):
    id: int

    class Config:
        from_attributes = True


class EnvelopeItemBase(BaseModel):
    event_id: int
    item_id: str
    payload: bytes


class EnvelopeItemCreate(EnvelopeItemBase):
    pass


class EnvelopeItem(EnvelopeItemBase):
    id: int

    class Config:
        from_attributes = True