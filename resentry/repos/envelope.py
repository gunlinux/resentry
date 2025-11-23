from resentry.repos.base import BaseRepo
from resentry.database.models.envelope import Envelope, EnvelopeItem


class EnvelopeRepository(BaseRepo):
    entity_type = Envelope


class EnvelopeItemRepository(BaseRepo):
    entity_type = EnvelopeItem
