import logging
from dataclasses import dataclass, field
from typing import Callable

from fastapi import Depends
from fastapi_injectable import injectable

from resentry.domain.queue import Event
from resentry.infra.telegram import TelegramService
from resentry.core.deps import get_telegram_service


@dataclass
class EventWorker:
    events: dict[str, list[Callable]] = field(default_factory=dict)

    async def process_event(self, event: Event):
        for call in self.events.get(event.level, []):
            logging.info("found binded caller %s", call)
            await call(event)

    def register(self, event_name: str, action: Callable):
        if event_name not in self.events.keys():
            self.events[event_name] = [action]
        else:
            self.events[event_name].append(action)


@injectable
async def send_telegram(
    event: Event, telegram_service: TelegramService = Depends(get_telegram_service)
):
    logging.info("sent to telegram %s", event)

    for user in event.users:
        if user.telegram_chat_id:
            logging.info(f"sending to user {user.telegram_chat_id}")
            await telegram_service.send_message(
                chat_id=user.telegram_chat_id, text="not_hello"
            )
            # await user_send(user.telegram_chat_id, event)


if __name__ == "__main__":
    event_worker = EventWorker()
    event_worker.register("error", send_telegram)
