from dataclasses import dataclass
import datetime
import typing

from resentry.database.models.envelope import EnvelopeItem
from resentry.repos.envelope import EnvelopeItemRepository, EnvelopeRepository
from resentry.database.models.envelope import Envelope as EnvelopeModel


from resentry.sentry import unpack_sentry_envelope_from_request


@dataclass(frozen=True)
class StoreEnvelope:
    repo: EnvelopeRepository
    repo_items: EnvelopeItemRepository
    body: bytes
    content_encoding: str | None
    project_id: int

    async def execute(self) -> EnvelopeModel | None:  # type: ignore[override]
        try:
            envelope = unpack_sentry_envelope_from_request(
                self.body, self.content_encoding
            )
        except ValueError:
            return None

        # Create envelope record in database
        sent_at_str = envelope.headers.get("sent_at")
        sent_at = datetime.datetime.fromisoformat(sent_at_str) if sent_at_str else None

        envelope_db = EnvelopeModel(
            project_id=self.project_id,
            payload=self.body,
            event_id=envelope.event_id,
            sent_at=sent_at,
            dsn=envelope.headers.get("dsn"),
        )
        envelope_db = typing.cast(EnvelopeModel, await self.repo.create(envelope_db))
        for item_id, item in enumerate(envelope.items):
            item_db = EnvelopeItem(
                event_id=typing.cast(int, envelope_db.id),
                item_id=str(item_id),
                payload=item.get_payload_bytes(),
            )
            await self.repo_items.create(item_db)

        return envelope_db
