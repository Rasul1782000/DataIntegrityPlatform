"""Logging configuration for the application.

Single source of truth for logging:
- configure_logging(): dictConfig applied at app startup (used by main.py)
- get_logger(): helper returning a consistently formatted logger (used by services)
"""

import logging
import logging.config
import sys


def configure_logging() -> None:
    """Apply the root logging configuration (called once at startup)."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(levelname)-5.5s [%(name)s] %(filename)s:%(lineno)d - %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "standard",
                }
            },
            "root": {"level": "INFO", "handlers": ["console"]},
        }
    )


def get_logger(name: str = __name__) -> logging.Logger:
    """Get a logger under the root configuration."""
    return logging.getLogger(name)