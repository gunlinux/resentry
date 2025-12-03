import httpx
from httpx import Response

# from http import HTTPStatus
from typing import Callable


class HttpClient:
    def __init__(self, base_url: str, reauth: Callable, timeout: float = 30.0):
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        self.reauth = reauth

    def update_header(self, key: str, value: str) -> None:
        self._client.headers[key] = value

    def request(self, method: str, url: str, retry=True, **kwargs) -> Response:
        response = self._client.request(method=method, url=url, **kwargs)
        if response.status_code == 401:
            if retry:
                self.reauth()
                return self._client.request(method=method, url=url, **kwargs)
        return response

    def post(self, url: str, **kwargs) -> Response:
        return self.request(method="post", url=url, **kwargs)

    def get(self, url: str, **kwargs) -> Response:
        return self.request(method="get", url=url, **kwargs)

    def patch(self, url: str, **kwargs) -> Response:
        return self.request(method="patch", url=url, **kwargs)

    def put(self, url: str, **kwargs) -> Response:
        return self.request(method="put", url=url, **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        return self.request(method="delete", url=url, **kwargs)

    def close(self) -> None:
        return self._client.close()
