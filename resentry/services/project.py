from dataclasses import dataclass
import typing

from resentry.repos.project import ProjectRepository
from resentry.database.models.project import Project
from resentry.domain.project import ProjectDTO


@dataclass
class ProjectService:
    repo: ProjectRepository

    async def get_project_by_id(self, project_id: int) -> ProjectDTO | None:
        if project := typing.cast(
            Project | None, await self.repo.get_by_id(project_id)
        ):
            return ProjectDTO(
                id=project.id,
                name=project.name,
                lang=project.lang,
                key=project.key,
            )
        return None
