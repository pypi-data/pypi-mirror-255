import json
from datetime import datetime
from decimal import Decimal
from functools import partial
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from hartware_lib.types import AnyDict, ExtraDeserializer, ExtraSerializer


class NoSerializerMatch(Exception):
    pass


class GlobalEncoder(json.JSONEncoder):
    def __init__(
        self,
        *args: Any,
        extra_serializers: Sequence[ExtraSerializer] = (),
        **kwargs: Any,
    ):
        super(GlobalEncoder, self).__init__(*args, **kwargs)

        self.extra_serializers = extra_serializers

    def default(self, o: Any) -> AnyDict:
        if isinstance(o, datetime):
            return {"_type": o.__class__.__name__, "value": o.isoformat()}
        elif isinstance(o, set):
            return {"_type": o.__class__.__name__, "value": list(o)}
        elif isinstance(o, Decimal):
            return {"_type": o.__class__.__name__, "value": str(o)}
        elif isinstance(o, Path):
            return {"_type": "Path", "value": str(o)}
        elif self.extra_serializers:
            for extra_serializer in self.extra_serializers:
                try:
                    return extra_serializer(o)
                except NoSerializerMatch:
                    pass

        raise NoSerializerMatch(f"Unknown `{o.__class__.__name__}` type")


def serialize(
    obj: Any,
    indent: Optional[int] = None,
    extra_serializers: Sequence[ExtraSerializer] = (),
) -> bytes:
    return (
        GlobalEncoder(indent=indent, extra_serializers=extra_serializers)
        .encode(obj)
        .encode("utf-8")
    )


def _global_decoder(
    obj: AnyDict, extra_deserializers: Sequence[ExtraSerializer]
) -> Any:
    if obj_type := obj.get("_type"):
        obj_value = obj["value"]

        if obj_type == "datetime":
            return datetime.fromisoformat(obj_value)
        elif obj_type == "set":
            return set(obj_value)
        elif obj_type == "Decimal":
            return Decimal(obj_value)
        elif obj_type == "Path":
            return Path(obj_value)
        elif extra_deserializers:
            for extra_deserializer in extra_deserializers:
                try:
                    return extra_deserializer(obj)
                except NoSerializerMatch:
                    pass

        raise NoSerializerMatch(f"Unknown `{obj_type}` type")

    return obj


def deserialize(
    obj: Union[bytes, str], extra_deserializers: Sequence[ExtraDeserializer] = ()
) -> Any:
    return json.loads(
        obj,
        object_hook=partial(_global_decoder, extra_deserializers=extra_deserializers),
    )
