from typing import Any, Optional

from aiohttp import ClientResponse, ClientSession

from hartware_lib.types import AnyDict, HeadersDict


class HttpAsyncAdapter:
    def __init__(self, headers: Optional[HeadersDict] = None):
        self.headers = headers or {}

    async def request(
        self,
        method: str,
        url: str,
        extra_headers: Optional[HeadersDict] = None,
        **kwargs: Any
    ) -> ClientResponse:
        headers = self.headers

        if extra_headers:
            headers.update(extra_headers)

        async with ClientSession() as session:
            response = await session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()

            return response

    async def get_text(self, *args: Any, **kwargs: Any) -> str:
        response = await self.request(*args, **kwargs)

        return await response.text()

    async def get_json(self, *args: Any, **kwargs: Any) -> AnyDict:
        response = await self.request(*args, **kwargs)

        return await response.json()  # type: ignore[no-any-return]
