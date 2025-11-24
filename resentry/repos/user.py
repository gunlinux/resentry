from resentry.repos.base import BaseRepo
from resentry.database.models.user import User


class UserRepository(BaseRepo):
    entity_type = User
