from __future__ import annotations

import logging.config
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict


@dataclass
class LoggingBuilder:
    config: Dict[str, Any] = field(
        default_factory=lambda: {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "raw": {"format": "%(message)s"},
                "standard": {
                    "format": "%(asctime)s %(levelname)-8s %(name)-22s: %(message)s"
                },
            },
            "handlers": {},
            "loggers": {
                "": {"handlers": [], "level": "DEBUG", "propagate": False},
            },
        }
    )

    def add_default_handler(
        self, level: int = logging.DEBUG, formatter: str = "standard"
    ) -> LoggingBuilder:
        self.config["handlers"]["default"] = {
            "level": level,
            "formatter": formatter,
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        }
        self.config["loggers"][""]["handlers"].append("default")

        return self

    def add_file_handler(
        self,
        file_path: Path,
        level: int = logging.DEBUG,
        formatter: str = "standard",
    ) -> LoggingBuilder:
        self.config["handlers"]["file"] = {
            "level": level,
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": formatter,
            "filename": str(file_path),
            "maxBytes": 10_000_000,
            "backupCount": 10,
        }
        self.config["loggers"][""]["handlers"].append("file")

        return self

    def add_logger(
        self, name: str, level: int = logging.DEBUG, propagate: bool = False
    ) -> LoggingBuilder:
        root_handlers = self.config["loggers"][""]["handlers"]

        self.config["loggers"][name] = {
            "handlers": root_handlers,
            "level": level,
            "propagate": propagate,
        }

        return self

    def set_formatter(self, name: str, format: str) -> LoggingBuilder:
        self.config["formatters"][name] = {"format": format}

        return self

    def apply(self, func: Callable[[LoggingBuilder], None]) -> LoggingBuilder:
        func(self)

        return self

    def shut(self, module_name: str, level: int = logging.WARNING) -> LoggingBuilder:
        logging.getLogger(module_name).setLevel(level)

        return self

    def run(self) -> None:
        logging.config.dictConfig(self.config)
