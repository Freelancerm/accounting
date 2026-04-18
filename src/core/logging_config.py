"""Central logging setup for application."""

from __future__ import annotations

import logging
import os
from typing import Final

DEFAULT_LOG_LEVEL: Final[str] = "INFO"
LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def configure_logging() -> None:
    """Configure root logger once for app and tests."""
    if logging.getLogger().handlers:
        return

    level_name = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format=LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    """Return configured module logger."""
    configure_logging()
    return logging.getLogger(name)
