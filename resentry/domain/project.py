from dataclasses import dataclass


@dataclass
class ProjectDTO:
    id: int
    name: str
    lang: str
    key: str | None = None
