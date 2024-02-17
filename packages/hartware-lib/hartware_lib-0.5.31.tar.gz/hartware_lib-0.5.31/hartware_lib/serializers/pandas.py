from io import StringIO
from typing import Any

from pandas import DataFrame, Series, read_json

from hartware_lib.serializers.main import NoSerializerMatch
from hartware_lib.types import AnyDict


def pandas_extra_serializer(o: Any) -> AnyDict:
    if isinstance(o, DataFrame):
        return {
            "_type": o.__class__.__name__,
            "index": o.index.name,
            "value": o.reset_index().to_json(orient="records"),
        }
    if isinstance(o, Series):
        return {"_type": o.__class__.__name__, "value": o.to_json()}

    raise NoSerializerMatch()


def pandas_extra_deserializer(obj: AnyDict) -> Any:
    if obj_type := obj.get("_type"):
        obj_value = obj["value"]

        if obj_type == "DataFrame":
            df = read_json(StringIO(obj_value), orient="records")

            if obj["index"]:
                df = df.set_index(obj["index"])
            else:
                df = df.set_index("index")
                df.index.name = None

            return df
        if obj_type == "Series":
            return read_json(StringIO(obj_value), typ="series")

    raise NoSerializerMatch()
