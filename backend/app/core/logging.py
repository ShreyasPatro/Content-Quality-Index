"""Logging configuration for the application."""

import logging
import sys
from typing import Any

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.is_development else logging.WARNING
    )
    logging.getLogger("celery").setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class StructuredLogger:
    """Structured logger for JSON-formatted logs (production use)."""

    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)

    def log(self, level: str, message: str, **kwargs: Any) -> None:
        """Log with structured context."""
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.log("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.log("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.log("error", message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.log("debug", message, **kwargs)
