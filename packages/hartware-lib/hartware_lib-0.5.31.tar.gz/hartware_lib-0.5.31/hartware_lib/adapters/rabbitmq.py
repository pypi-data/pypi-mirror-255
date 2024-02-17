from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, List, Optional

from aio_pika import (
    DeliveryMode,
    ExchangeType,
    Message,
    RobustConnection,
    connect_robust,
)
from aio_pika.abc import AbstractIncomingMessage

from hartware_lib.serializers import deserialize as default_deserializer
from hartware_lib.serializers import serialize as default_serializer
from hartware_lib.settings import RabbitMQSettings
from hartware_lib.types import Deserializer, Serializer

logger = logging.getLogger("hartware_lib.rabbitmq")


class RabbitMQAdapter:
    def __init__(
        self,
        settings: RabbitMQSettings,
        serializer: Serializer,
        deserializer: Deserializer,
        object_class: Any = object,
    ):
        self.settings = settings
        self.serializer = serializer
        self.deserializer = deserializer
        self.object_class = object_class

    @classmethod
    def build(
        cls,
        settings: RabbitMQSettings,
        serializer: Serializer = default_serializer,
        deserializer: Deserializer = default_deserializer,
        object_class: Any = dict,
    ) -> RabbitMQAdapter:
        return cls(settings, serializer, deserializer, object_class)

    async def get_connection(self) -> RobustConnection:
        return await connect_robust(  # type: ignore[return-value]
            f"amqp://{self.settings.username}:{self.settings.password}@{self.settings.host}:{self.settings.port}/"
        )

    async def wait_until_ready(self, n: int = 30, delay: float = 1.0) -> None:
        for i in range(n):
            try:
                connection = await self.get_connection()

                if not connection.is_closed:
                    await connection.close()

                    return None
            except OSError:
                if i == n - 1:
                    raise

                await asyncio.sleep(delay)

    def handle_message(self, callback: CallbackHandler) -> MessageHandler:
        async def wrapper(message: AbstractIncomingMessage) -> Any:
            async with message.process():
                obj = self.deserializer(message.body)

                return await callback(self, obj)

        return wrapper

    def encode_object(self, obj: Any) -> bytes:
        if not isinstance(obj, self.object_class):
            raise Exception(f"Message must be of type `{self.object_class.__name__}`")

        return self.serializer(obj)

    def to_message(self, obj: Any) -> Message:
        message_body = self.encode_object(obj)

        return Message(message_body, delivery_mode=DeliveryMode.PERSISTENT)

    async def run_message_on_default_exchange(
        self, connection: RobustConnection, obj: Any, routing_key: str
    ) -> None:
        channel = await connection.channel()

        await channel.default_exchange.publish(
            self.to_message(obj), routing_key=routing_key
        )

    async def run_consumer_on_default_exchange(
        self, connection: RobustConnection, callback: CallbackHandler, routing_key: str
    ) -> None:
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(routing_key, durable=True)

        await queue.consume(self.handle_message(callback))

        await asyncio.Future()

    async def run_message_on_fanout_exchange(
        self,
        connection: RobustConnection,
        obj: Any,
        exchange_name: str,
        routing_key: str = "none",
    ) -> None:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(exchange_name, ExchangeType.FANOUT)

        await exchange.publish(self.to_message(obj), routing_key=routing_key)

    async def run_consumer_on_fanout_exchange(
        self,
        connection: RobustConnection,
        callback: CallbackHandler,
        exchange_name: str,
    ) -> None:
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(exchange_name, ExchangeType.FANOUT)
        queue = await channel.declare_queue(exclusive=True)

        await queue.bind(exchange)
        await queue.consume(self.handle_message(callback))

        await asyncio.Future()

    async def run_message_on_topic_exchange(
        self,
        connection: RobustConnection,
        obj: Any,
        exchange_name: str,
        routing_key: str,
    ) -> None:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(exchange_name, ExchangeType.TOPIC)

        await exchange.publish(self.to_message(obj), routing_key=routing_key)

    async def run_consumer_on_topic_exchange(
        self,
        connection: RobustConnection,
        callback: CallbackHandler,
        exchange_name: str,
        binding_keys: List[str],
    ) -> None:
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(exchange_name, ExchangeType.TOPIC)
        queue = await channel.declare_queue("", durable=True)

        for binding_key in binding_keys:
            await queue.bind(exchange, routing_key=binding_key)

        await queue.consume(self.handle_message(callback))

        await asyncio.Future()

    def get_flavor_adapter(
        self, flavor: str, *args: Any, **kwargs: Any
    ) -> RabbitMQFlavor:
        kwargs.update(self.__dict__)

        if flavor == "default":
            return RabbitMQDefaultExchangeAdapter(*args, **kwargs)
        elif flavor == "fanout":
            return RabbitMQFanoutExchangeAdapter(*args, **kwargs)
        elif flavor == "topic":
            return RabbitMQTopicExchangeAdapter(*args, **kwargs)
        else:
            raise Exception(f"No flavor '{flavor}'")


CallbackHandler = Callable[[RabbitMQAdapter, Any], Awaitable[Any]]
MessageHandler = Callable[[AbstractIncomingMessage], Awaitable[Any]]


class RabbitMQFlavor(RabbitMQAdapter):
    def __init__(self, *args: Any, **kwargs: Any):
        super(RabbitMQFlavor, self).__init__(*args, **kwargs)

        self._connection: Optional[RobustConnection] = None

    async def ensure_connection(self) -> RobustConnection:
        if self._connection is None:
            self._connection = await self.get_connection()

        return self._connection

    async def connect(self) -> RobustConnection:
        return await self.ensure_connection()

    @property
    async def connected(self) -> bool:
        return bool(await self.ensure_connection())


class RabbitMQDefaultExchangeAdapter(RabbitMQFlavor):
    def __init__(self, *args: Any, routing_key: str, **kwargs: Any):
        super(RabbitMQDefaultExchangeAdapter, self).__init__(*args, **kwargs)

        self.routing_key = routing_key

    async def publish(self, obj: Any) -> None:
        connection = await self.ensure_connection()

        await self.run_message_on_default_exchange(connection, obj, self.routing_key)

    async def consume(self, callback: CallbackHandler) -> None:
        connection = await self.ensure_connection()

        await self.run_consumer_on_default_exchange(
            connection, callback, self.routing_key
        )


class RabbitMQFanoutExchangeAdapter(RabbitMQFlavor):
    def __init__(self, *args: Any, exchange_name: str, **kwargs: Any):
        super(RabbitMQFanoutExchangeAdapter, self).__init__(*args, **kwargs)

        self.exchange_name = exchange_name

    async def publish(self, obj: Any) -> None:
        connection = await self.ensure_connection()

        await self.run_message_on_fanout_exchange(connection, obj, self.exchange_name)

    async def consume(self, callback: CallbackHandler) -> None:
        connection = await self.ensure_connection()

        await self.run_consumer_on_fanout_exchange(
            connection, callback, self.exchange_name
        )


class RabbitMQTopicExchangeAdapter(RabbitMQFlavor):
    def __init__(self, *args: Any, exchange_name: str, **kwargs: Any):
        super(RabbitMQTopicExchangeAdapter, self).__init__(*args, **kwargs)

        self.exchange_name = exchange_name

    async def publish(self, obj: Any, routing_key: str) -> None:
        connection = await self.ensure_connection()

        await self.run_message_on_topic_exchange(
            connection, obj, self.exchange_name, routing_key
        )

    async def consume(
        self, callback: CallbackHandler, binding_keys: List[str], **kwargs: Any
    ) -> None:
        connection = await self.ensure_connection()

        await self.run_consumer_on_topic_exchange(
            connection, callback, self.exchange_name, binding_keys
        )
