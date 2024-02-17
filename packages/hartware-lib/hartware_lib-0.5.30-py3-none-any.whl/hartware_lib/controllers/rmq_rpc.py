from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator

from hartware_lib.adapters.rabbitmq import (
    RabbitMQAdapter,
    RabbitMQDefaultExchangeAdapter,
)
from hartware_lib.controllers.rmq_rpc_caller import RpcCaller
from hartware_lib.controllers.rmq_rpc_probe import RpcProbe
from hartware_lib.settings import RabbitMQSettings


@dataclass
class RmqRpcController:
    rpc_in: RabbitMQDefaultExchangeAdapter
    rpc_out: RabbitMQDefaultExchangeAdapter

    @classmethod
    def build(
        cls, rabbitmq_settings: RabbitMQSettings, queue_name: str, **kwargs: Any
    ) -> RmqRpcController:
        rabbitmq = RabbitMQAdapter.build(settings=rabbitmq_settings, **kwargs)

        rpc_in = rabbitmq.get_flavor_adapter("default", routing_key=f"{queue_name}_in")
        rpc_out = rabbitmq.get_flavor_adapter(
            "default", routing_key=f"{queue_name}_out"
        )

        assert isinstance(rpc_in, RabbitMQDefaultExchangeAdapter)
        assert isinstance(rpc_out, RabbitMQDefaultExchangeAdapter)

        return cls(rpc_in, rpc_out)

    @asynccontextmanager
    async def connected(self) -> AsyncIterator[None]:
        async with await self.rpc_in.connect():
            async with await self.rpc_out.connect():
                yield

    def get_probe(self, subject: object) -> RpcProbe:
        return RpcProbe(self.rpc_in, self.rpc_out, subject)

    def get_caller(self) -> RpcCaller:
        return RpcCaller(self.rpc_in, self.rpc_out)
