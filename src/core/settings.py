"""Application settings."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings sourced from environment."""

    app_title: str = os.getenv("APP_TITLE", "Minimal Accounting")
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


def get_settings() -> AppSettings:
    """Return application settings."""
    return AppSettings()
