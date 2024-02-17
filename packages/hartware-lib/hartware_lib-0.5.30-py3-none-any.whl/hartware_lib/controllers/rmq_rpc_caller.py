from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, Union

from hartware_lib.adapters.rabbitmq import RabbitMQDefaultExchangeAdapter


class RpcCaller:
    _none_value = object()
    _max_wait_loop = 150

    def __init__(
        self,
        rpc_in: RabbitMQDefaultExchangeAdapter,
        rpc_out: RabbitMQDefaultExchangeAdapter,
    ):
        self.rpc_in = rpc_in
        self.rpc_out = rpc_out

        self._result: Union[object, Dict[str, Any]] = self._none_value
        self.command_lock = asyncio.Lock()
        self.consumer_task: Optional[asyncio.Task[Any]] = None

    def listen(self) -> None:
        self.consumer_task = asyncio.create_task(self.rpc_out.consume(self._store_result))  # type: ignore[arg-type]

    async def _store_result(
        self, _origin: RabbitMQDefaultExchangeAdapter, result: Dict[str, Any]
    ) -> None:
        self._result = result

    async def get_property(self, name: str) -> Any:
        return await self._process({"property": name})

    async def set_property(self, name: str, value: Any) -> None:
        await self._process({"property": name, "property_set": value})

    async def call(self, func: str, *args: Any, **kwargs: Any) -> Any:
        return await self._process({"func": func, "args": args, "kwargs": kwargs})

    async def _process(self, request: Dict[str, Any]) -> Any:
        self._result = self._none_value

        async with self.command_lock:
            await self.rpc_in.publish(request)

            for _ in range(self._max_wait_loop):
                if self._result != self._none_value:
                    assert isinstance(self._result, dict)

                    error = self._result.get("error")

                    if error:
                        raise Exception(f"{error}")

                    return self._result.get("result")
                await asyncio.sleep(0.2)
            raise Exception("Command Timeout")

    async def stop(self) -> None:
        if self.consumer_task and not self.consumer_task.done():
            self.consumer_task.cancel()

            await asyncio.wait([self.consumer_task])
