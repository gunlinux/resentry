from dataclasses import dataclass, field
from enum import StrEnum
from datetime import datetime
import typing

from resentry.domain.project import ProjectDTO
from resentry.domain.user import UserDTO


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
    project: ProjectDTO
    payload: dict[str, typing.Any]
    users: list[UserDTO] = field(default_factory=list)
    sent_at: datetime | None = None
