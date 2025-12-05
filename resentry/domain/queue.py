from dataclasses import dataclass, field
from enum import StrEnum

from resentry.database.models.project import Project
from resentry.database.models.envelope import EnvelopeItem
from resentry.database.models.user import User


class LogLevel(StrEnum):
    critical = "CRITICAL"
    fatal = "FATAL"
    error = "ERROR"
    warning = "WARNING"
    warn = "WARNING"
    info = "INFO"
    debug = "DEBUG"
    notset = "NOTSET"


@dataclass
class Event:
    level: LogLevel
    event_id: str
    project: Project
    items: list[EnvelopeItem] | None = None
    users: list[User] = field(default_factory=list)
