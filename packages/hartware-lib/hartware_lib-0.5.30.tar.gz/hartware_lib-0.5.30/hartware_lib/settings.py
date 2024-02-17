import json
import logging
import re
from collections import defaultdict
from dataclasses import _MISSING_TYPE, dataclass, is_dataclass
from os import environ
from pathlib import Path
from typing import _GenericAlias  # type: ignore[attr-defined]
from typing import _UnionGenericAlias  # type: ignore[attr-defined]
from typing import Any, Dict, List, Optional, Type, get_type_hints

import yaml
from yaml.loader import SafeLoader

from hartware_lib.types import Dataclass, T
from hartware_lib.utils.casing import pascal_to_snake_case

logger = logging.getLogger("hartware_lib.settings")

NoneType = type(None)


def transform(target_type: Type[T], value: Any) -> Optional[T]:
    if value is None:
        return value

    if target_type is bool:
        if not isinstance(value, str):
            value = str(value)
        if value.lower() in ("0", "no", "false"):
            return False  # type: ignore[return-value]
        if value.lower() in ("1", "yes", "true"):
            return True  # type: ignore[return-value]

        raise Exception(f"Can't parse '{value}' as boolean")

    return target_type(value)  # type: ignore[call-arg]


def load_settings(  # noqa: C901
    cls: Type[Dataclass],
    config: Optional[Dict[str, Any]] = None,
    path: Optional[List[str]] = None,
    set_prefix: str = "",
    hide_prefix: bool = False,
) -> Dataclass:
    settings = {}

    if path is None:
        path = []

    if config is None:
        config = {}

    if not hide_prefix:
        if set_prefix:
            prefix = set_prefix
        else:
            prefix = getattr(
                cls,
                "_prefix",
                pascal_to_snake_case(cls.__name__.replace("Settings", "")),
            )

        path = path + [prefix]

    type_hints = get_type_hints(cls)

    for option_name, option in cls.__dataclass_fields__.items():  # type: ignore[attr-defined]
        option_type = type_hints[option_name]

        option_name_target = option.metadata.get("prefix", option_name)

        env_path = "_".join(path + [option_name_target]).upper()
        config_value = config.get(option_name)

        is_list = False
        is_optional = False
        if type(option_type) is _GenericAlias and option_type.__origin__ is list:
            option_type = option_type.__args__[0]

            is_list = True
        elif (
            type(option_type) is _UnionGenericAlias and NoneType in option_type.__args__
        ):
            option_type = list(option_type.__args__)
            option_type.remove(NoneType)

            assert len(option_type) == 1

            option_type = option_type[0]
            is_optional = True

        if is_dataclass(option_type):
            if is_list:
                config_values = {
                    i: load_settings(
                        option_type,
                        _config_value,
                        path + [option_name_target, str(i)],
                        hide_prefix=True,
                    )
                    for i, _config_value in enumerate(config_value or [])
                }

                extra_conf: Dict[int, Dict[Any, Any]] = defaultdict(dict)
                for k, v in environ.items():
                    if env_path not in k:
                        continue

                    m = re.match(rf"{env_path}_(?P<index>\d+)_(?P<attr>\w+)", k)
                    if not m:
                        logger.warning(f"Could not parse key: {k}")
                        continue
                    index = int(m.group("index"))
                    if index in config_values:
                        continue
                    extra_conf[index][m.group("attr")] = v
                for i, config_value in extra_conf.items():
                    try:
                        config_values[i] = load_settings(
                            option_type,
                            config_value,
                            path + [option_name_target, str(i)],
                            hide_prefix=True,
                        )
                    except Exception as exc:
                        logger.warning(f"Incomplete settings: {exc}")

                config_value = [
                    i[1] for i in sorted(config_values.items(), key=lambda x: x[0])
                ]
            else:
                try:
                    config_value = load_settings(
                        option_type,
                        config_value,
                        path,
                        set_prefix=option.metadata.get("prefix", ""),
                    )
                except Exception:
                    if is_optional:
                        config_value = None
                    else:
                        raise
        else:
            if env_value := environ.get(env_path):
                config_value = env_value
            if (cast_func := option.metadata.get("cast")) and isinstance(
                config_value, str
            ):
                config_value = cast_func(config_value)
            elif isinstance(config_value, str) and is_list:
                config_value = [option_type(x) for x in json.loads(config_value)]
            elif not isinstance(config_value, option_type):
                config_value = transform(option_type, config_value)
        if config_value is None:
            if not isinstance(option.default, _MISSING_TYPE):
                config_value = option.default
            elif not isinstance(option.default_factory, _MISSING_TYPE):
                config_value = option.default_factory()

            if not isinstance(config_value, option_type):
                if not is_optional:
                    raise Exception(f"No value for {'.'.join(path + [option_name])}")

        settings[option_name] = config_value

    return cls(**settings)  # type: ignore[call-arg]


def load_settings_from_file(
    base_dataclass: Type[Dataclass], config_path: Path, **kwargs: Any
) -> Dataclass:
    with open(config_path) as f:
        config = yaml.load(f, Loader=SafeLoader)

        return load_settings(base_dataclass, config or {}, **kwargs)


@dataclass
class RabbitMQSettings:
    _prefix = "rabbitmq"

    username: str
    password: str
    host: str
    port: int = 5672


@dataclass
class MongoDBSettings:
    _prefix = "mongodb"

    username: str
    password: str
    database: str
    host: str
    srv_mode: bool
    port: int = 27017
    timeout_ms: int = 2000


@dataclass
class HttpRpcSettings:
    host: str
    port: int


@dataclass
class MetaTraderSettings:
    _prefix = "metatrader"

    login: int
    password: str
    path: Path
    server: str
    utc_offset: int = 0
    order_offset: int = 0
    price_offset: int = 0


@dataclass
class SlackBotSettings:
    api_token: str
    default_channel: str
