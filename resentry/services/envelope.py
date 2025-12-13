from dataclasses import dataclass
import typing

from resentry.repos.envelope import EnvelopeRepository, EnvelopeItemRepository
from resentry.database.models.envelope import Envelope, EnvelopeItem
from resentry.domain.envelope import EnvelopeDTO, EnvelopeItemDTO


@dataclass
class EnvelopeService:
    repo: EnvelopeRepository
    repo_items: EnvelopeItemRepository

    async def get_envelope_by_id(self, envelope_id: int) -> EnvelopeDTO | None:
        if envelope := typing.cast(
            Envelope | None, await self.repo.get_by_id(envelope_id)
        ):
            return EnvelopeDTO(
                id=envelope.id,
                project_id=envelope.project_id,
                payload=envelope.payload,
                event_id=envelope.event_id,
                sent_at=envelope.sent_at,
                dsn=envelope.dsn,
            )
        return None

    async def get_envelope_item_by_id(self, item_id: int) -> EnvelopeItemDTO | None:
        if item := typing.cast(
            EnvelopeItem | None, await self.repo_items.get_by_id(item_id)
        ):
            return EnvelopeItemDTO(
                id=item.id,
                event_id=item.event_id,
                item_id=item.item_id,
                payload=item.payload,
            )
        return None
