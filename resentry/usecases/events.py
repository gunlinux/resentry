from dataclasses import dataclass
from asyncio import Queue
import json
import typing

from resentry.database.models.project import Project
from resentry.database.models.user import User
from resentry.domain.queue import Event, LogLevel
from resentry.database.models.envelope import Envelope


@dataclass
class ScheduleEnvelope:
    queue: Queue
    project: Project
    users: list[User]

    def _get_level(self, payload: dict[str, typing.Any]) -> LogLevel:
        if level := payload.get("level", None):
            return LogLevel(level)
        raise ValueError("Cant get log level")

    def _get_payload(self, payload: bytes) -> dict[str, typing.Any]:
        return json.loads(payload.decode("utf-8", "replace"))

    async def execute(self, envelope: Envelope):
        for envelope_item in await envelope.async_items():
            payload = self._get_payload(envelope_item.payload)
            event = Event(
                event_id=envelope_item.event_id,
                project=self.project,
                level=self._get_level(payload),
                payload=payload,
                users=self.users,
                sent_at=envelope.sent_at,
            )
            await self.queue.put(event)
