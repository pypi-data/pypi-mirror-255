from typing import Any, Callable, Dict, TypeVar, Union

T = TypeVar("T")

HeadersDict = Dict[str, str]
AnyDict = Dict[str, Any]
Dataclass = TypeVar("Dataclass")

Serializer = Callable[[Any], bytes]
Deserializer = Callable[[Union[bytes, str]], Any]

ExtraSerializer = Callable[[Any], AnyDict]
ExtraDeserializer = Callable[[AnyDict], Any]
