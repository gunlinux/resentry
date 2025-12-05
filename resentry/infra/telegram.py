from dataclasses import dataclass
import typing
import httpx


class TelegramServiceException(Exception):
    pass


@dataclass
class TelegramService:
    token: str

    async def _request(
        self,
        method: str,
        api_method: str,
        data: typing.Mapping[str, typing.Any] | None = None,
    ) -> httpx.Response:
        url = f"https://api.telegram.org/bot{self.token}/{api_method}"
        async with httpx.AsyncClient() as client:
            return await client.request(method=method, url=url, data=data)

    async def send_message(self, chat_id: str, text: str) -> None:
        data = {
            "chat_id": chat_id,
            "text": text,
        }
        response = await self._request(
            method="post", api_method="sendMessage", data=data
        )
        if response.status_code != 200:
            raise TelegramServiceException("sendMessage failed")
