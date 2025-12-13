from dataclasses import dataclass, field
from enum import StrEnum
from datetime import datetime
import typing

from resentry.database.models.project import Project
from resentry.database.models.user import User


class LogLevel(StrEnum):
    critical = "critical"
    fatal = "fatal"
    error = "error"
    warning = "warning"
    warn = "warning"
    info = "info"
    debug = "debug"
    notset = "notset"


@dataclass
class Event:
    level: LogLevel
    event_id: int
    project: Project
    payload: dict[str, typing.Any]
    users: list[User] = field(default_factory=list)
    sent_at: datetime | None = None
