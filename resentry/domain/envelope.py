from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EnvelopeItemDTO:
    id: int
    event_id: int
    item_id: str
    payload: bytes


@dataclass
class EnvelopeDTO:
    id: int
    project_id: int
    payload: bytes
    event_id: str
    sent_at: Optional[datetime]
    dsn: Optional[str]
