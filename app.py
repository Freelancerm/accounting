"""Streamlit entrypoint for minimal accounting app."""

from src.core.logging_config import configure_logging, get_logger
from src.ui.app_view import render_app


configure_logging()
logger = get_logger(__name__)


def main() -> None:
    """Run Streamlit application."""
    logger.debug("Starting Streamlit accounting app")
    render_app()


if __name__ == "__main__":
    main()
