from __future__ import annotations

import asyncio
import logging
import traceback
from dataclasses import dataclass
from typing import Any

from aiohttp import web

from hartware_lib.serializers.builders import DeserializerBuilder, SerializerBuilder
from hartware_lib.settings import HttpRpcSettings
from hartware_lib.types import Deserializer, Serializer

logger = logging.getLogger("hartware_lib.http_rpc_probe")


@dataclass
class HttpRpcProbe:
    app: web.Application
    runner: web.AppRunner
    subject: Any
    settings: HttpRpcSettings
    serializer: Serializer
    deserializer: Deserializer

    @classmethod
    def build(
        cls,
        settings: HttpRpcSettings,
        subject: Any,
        serializer: Serializer = SerializerBuilder().get(),
        deserializer: Deserializer = DeserializerBuilder().get(),
    ) -> HttpRpcProbe:
        app = web.Application()
        runner = web.AppRunner(app)

        obj = cls(app, runner, subject, settings, serializer, deserializer)

        app.add_routes([web.post("/", obj.handle)])

        return obj

    async def handle(self, request: web.Request) -> web.Response:
        data = (await request.post())["order"]
        assert isinstance(data, str)

        order = self.deserializer(data)
        assert isinstance(order, dict)

        if "ping" in order:
            logger.info("ping received, pong sent")

            return web.Response(body=self.serializer({"result": {"pong": True}}))

        func = order.get("func")
        property = order.get("property")
        property_set = order.get("property_set")
        args = order.get("args") or []
        kwargs = order.get("kwargs") or {}

        if not func and not property:
            return web.Response(
                body=self.serializer(
                    {"error": "should have func or property specified"}
                ),
            )

        result = None
        try:
            if func:
                logger.info(f"call: {str(func)} = {args=}, {kwargs=}")

                func = getattr(self.subject, func)

                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
            else:
                assert isinstance(property, str)

                if "property_set" in order:
                    logger.info(f"set_property: {property} to {property_set:r}")

                    setattr(self.subject, property, property_set)
                else:
                    logger.info(f"get_property: {property}")

                    result = getattr(self.subject, property)
        except Exception:
            logger.info("got an exception:", exc_info=True)

            return web.Response(body=self.serializer({"error": traceback.format_exc()}))

        body = self.serializer({"result": result})

        logger.info(f"returns {len(body)} bytes ({type(result).__name__})")

        return web.Response(body=body)

    async def run(self) -> None:
        logger.info("start")

        await self.runner.setup()

        site = web.TCPSite(self.runner, self.settings.host, self.settings.port)
        await site.start()

        await asyncio.Future()

    async def cleanup(self) -> None:
        logger.info("cleaning up")

        await self.runner.cleanup()

        logger.info("stopped")
