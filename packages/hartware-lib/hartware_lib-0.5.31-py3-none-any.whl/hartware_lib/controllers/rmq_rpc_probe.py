from __future__ import annotations

import asyncio
import traceback
from typing import Any

from hartware_lib.adapters.rabbitmq import RabbitMQDefaultExchangeAdapter


class RpcProbe:
    def __init__(
        self,
        rpc_in: RabbitMQDefaultExchangeAdapter,
        rpc_out: RabbitMQDefaultExchangeAdapter,
        subject: Any,
    ):
        self.rpc_in = rpc_in
        self.rpc_out = rpc_out
        self.subject = subject

    async def run(self) -> None:
        await self.rpc_in.consume(self.handle_message)  # type: ignore[arg-type]

    async def handle_message(
        self, _origin: RabbitMQDefaultExchangeAdapter, message: Any
    ) -> None:
        assert isinstance(message, dict)

        func = message.get("func")
        property = message.get("property")
        property_set = message.get("property_set")
        args = message.get("args") or []
        kwargs = message.get("kwargs") or {}

        if not func and not property:
            await self.rpc_out.publish(
                {"error": "should have func or property specified"}
            )

            return

        result = None
        try:
            if func:
                func = getattr(self.subject, func)

                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
            else:
                assert isinstance(property, str)

                if "property_set" in message:
                    setattr(self.subject, property, property_set)
                else:
                    result = getattr(self.subject, property)
        except Exception:
            await self.rpc_out.publish({"error": traceback.format_exc()})

            return

        await self.rpc_out.publish({"result": result})
