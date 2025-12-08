from resentry.infra.telegram import TelegramService
from resentry.config import settings


def get_telegram_service() -> TelegramService | None:
    return TelegramService(token=settings.TELEGRAM_TOKEN)
