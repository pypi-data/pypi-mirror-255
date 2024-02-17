from __future__ import annotations

from functools import partial
from typing import Set

from hartware_lib.serializers.dataclasses import (
    dataclasses_extra_deserializer,
    dataclasses_extra_serializer,
)
from hartware_lib.serializers.main import deserialize, serialize
from hartware_lib.serializers.pandas import (
    pandas_extra_deserializer,
    pandas_extra_serializer,
)
from hartware_lib.types import (
    Dataclass,
    Deserializer,
    ExtraDeserializer,
    ExtraSerializer,
    Serializer,
)


class SerializerBuilder:
    def __init__(self) -> None:
        self.extra_serializers: Set[ExtraSerializer] = set()

    def add_serializer(self, extra_serializer: ExtraSerializer) -> SerializerBuilder:
        self.extra_serializers.add(extra_serializer)

        return self

    def with_pandas(self) -> SerializerBuilder:
        return self.add_serializer(pandas_extra_serializer)

    def with_dataclasses(self) -> SerializerBuilder:
        return self.add_serializer(dataclasses_extra_serializer)

    def get(self) -> Serializer:
        return partial(serialize, extra_serializers=list(self.extra_serializers))


class DeserializerBuilder:
    def __init__(self) -> None:
        self.extra_deserializers: Set[ExtraDeserializer] = set()

    def add_deserializer(
        self, extra_deserializer: ExtraDeserializer
    ) -> DeserializerBuilder:
        self.extra_deserializers.add(extra_deserializer)

        return self

    def with_pandas(self) -> DeserializerBuilder:
        return self.add_deserializer(pandas_extra_deserializer)

    def with_dataclasses(self, *dataclasses: Dataclass) -> DeserializerBuilder:
        return self.add_deserializer(dataclasses_extra_deserializer(*dataclasses))

    def get(self) -> Deserializer:
        return partial(deserialize, extra_deserializers=list(self.extra_deserializers))
