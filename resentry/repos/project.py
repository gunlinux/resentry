from resentry.repos.base import BaseRepo
from resentry.database.models.project import Project


class ProjectRepository(BaseRepo):
    entity_type = Project
