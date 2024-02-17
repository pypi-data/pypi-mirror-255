from dataclasses import is_dataclass
from typing import Any, Callable

from hartware_lib.serializers.main import NoSerializerMatch
from hartware_lib.types import AnyDict, Dataclass


def dataclasses_extra_serializer(o: Any) -> AnyDict:
    if is_dataclass(o):
        return {"_type": o.__class__.__name__, "value": o.__dict__}

    raise NoSerializerMatch()


def dataclasses_extra_deserializer(*dataclasses: Dataclass) -> Callable[[AnyDict], Any]:
    registered_dataclasses = {
        dataclass.__name__: dataclass for dataclass in dataclasses  # type: ignore[attr-defined]
    }

    def wrapper(obj: AnyDict) -> Any:
        if obj_type := obj.get("_type"):
            obj_value = obj["value"]

            if dataclass := registered_dataclasses.get(obj_type):
                return dataclass(**obj_value)  # type: ignore[operator]

        raise NoSerializerMatch()

    return wrapper
