from dataclasses import dataclass, field
from enum import StrEnum
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
