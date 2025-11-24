from dataclasses import dataclass
import typing
from uuid import uuid4

from resentry.database.schemas.project import ProjectCreate
from resentry.repos.project import ProjectRepository
from resentry.database.models.project import Project


@dataclass(frozen=True)
class CreateProject:
    repo: ProjectRepository

    def _generate_key(self):
        return uuid4().hex

    async def execute(self, body: ProjectCreate) -> Project:
        project_db = Project(**body.model_dump())
        project_db.key = self._generate_key()
        return typing.cast("Project", await self.repo.create(project_db))
