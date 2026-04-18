"""Common Streamlit UI helpers."""

from __future__ import annotations

from typing import Iterable

import streamlit as st

from src.core.logging_config import get_logger

logger = get_logger(__name__)


def render_notification() -> None:
    """Render one queued UI notification."""
    notice = st.session_state.pop("ui_notice", None)
    if not notice:
        return

    level = notice["level"]
    message = notice["message"]
    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    else:
        st.error(message)


def queue_notification(level: str, message: str) -> None:
    """Queue one message for next render."""
    st.session_state["ui_notice"] = {"level": level, "message": message}


def render_empty_state(message: str) -> None:
    """Render simple empty-state text."""
    st.info(message)


def render_error(message: str, error: Exception) -> None:
    """Show user-safe error and log details."""
    logger.exception("UI operation failed", extra={"ui_message": message})
    st.error(f"{message}: {error}")


def render_table(rows: Iterable[dict[str, object]], *, empty_message: str) -> None:
    """Render dataframe or empty-state."""
    rows = list(rows)
    if not rows:
        render_empty_state(empty_message)
        return
    st.dataframe(rows, use_container_width=True)
