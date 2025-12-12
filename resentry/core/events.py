import logging
from dataclasses import dataclass, field
from typing import Callable, override

from resentry.domain.queue import Event
from resentry.infra.telegram import TelegramService


@dataclass
class EventWorker:
    events: dict[str, list[Callable]] = field(default_factory=dict)

    async def process_event(self, event: Event):
        for call in self.events.get(event.level, []):
            await call(event)

    def register(self, event_name: str, sender: "Sender"):
        if event_name not in self.events.keys():
            self.events[event_name] = [sender.action]
        else:
            self.events[event_name].append(sender.action)


@dataclass
class Sender:
    async def action(self, event: Event) -> None:
        pass


@dataclass
class TelegramSender(Sender):
    telegram_service: TelegramService

    @override
    async def action(self, event: Event) -> None:
        for user in event.users:
            if user.telegram_chat_id:
                logging.info(f"sending to user {user.telegram_chat_id}")
                await self.telegram_service.send_message(
                    chat_id=user.telegram_chat_id,
                    text="not_hello",
                )
