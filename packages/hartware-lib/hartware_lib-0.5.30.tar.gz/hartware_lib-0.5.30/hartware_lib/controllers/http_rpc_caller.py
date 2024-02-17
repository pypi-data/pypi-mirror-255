from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from aiohttp import ClientSession, ClientTimeout

from hartware_lib.serializers.builders import DeserializerBuilder, SerializerBuilder
from hartware_lib.settings import HttpRpcSettings
from hartware_lib.types import AnyDict, Deserializer, Serializer

logger = logging.getLogger("hartware_lib.http_rpc_caller")


@dataclass
class HttpRpcCaller:
    settings: HttpRpcSettings
    serializer: Serializer
    deserializer: Deserializer

    @classmethod
    def build(
        cls,
        settings: HttpRpcSettings,
        serializer: Serializer = SerializerBuilder().get(),
        deserializer: Deserializer = DeserializerBuilder().get(),
    ) -> HttpRpcCaller:
        return cls(settings, serializer, deserializer)

    async def _process(self, data: AnyDict, timeout: float = 300.0) -> Any:
        async with ClientSession(
            timeout=ClientTimeout(timeout), raise_for_status=True
        ) as session:
            response = await session.post(
                f"http://{self.settings.host}:{self.settings.port}/",
                data={"order": self.serializer(data).decode("utf-8")},
                raise_for_status=True,
            )

            text = await response.text()

        data = self.deserializer(text)
        error = data.get("error")

        logger.info(f"received {len(text)} bytes ({type(data).__name__})")

        if error:
            raise Exception(f"{error}")

        return data.get("result")

    async def ping(self, timeout: float = 5.0) -> bool:
        logger.info("ping")

        try:
            result = await self._process({"ping": True}, timeout=timeout)

            if result.get("pong") is True:
                logger.info("pong received")

                return True
        except asyncio.exceptions.TimeoutError:
            logger.info("No pong received")
        except Exception as exc:
            logger.warning(f"No pong received: {exc}", exc_info=True)

        return False

    async def get_property(self, name: str, timeout: float = 10.0) -> Any:
        logger.info(f"get_property: {name}")

        return await self._process({"property": name}, timeout=timeout)

    async def set_property(self, name: str, value: Any, timeout: float = 10.0) -> None:
        logger.info(f"set_property: {name} to {value:r}")

        await self._process({"property": name, "property_set": value}, timeout=timeout)

    async def call(
        self, func: str, *args: Any, timeout: float = 300.0, **kwargs: Any
    ) -> Any:
        logger.info(f"call: {str(func)} = *{args}, **{kwargs}")

        return await self._process(
            {"func": func, "args": args, "kwargs": kwargs}, timeout=timeout
        )
