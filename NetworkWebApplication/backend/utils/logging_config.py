import logging
import os
from typing import Optional


# PUBLIC_INTERFACE
def configure_logging(level: Optional[str] = None) -> None:
    """Configure basic logging for the application."""
    log_level_name = level or os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
