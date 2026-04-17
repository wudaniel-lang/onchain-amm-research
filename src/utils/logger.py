from __future__ import annotations

import logging
from pathlib import Path

from src.config.loader import LoggingConfig


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logger(name: str, config: LoggingConfig) -> logging.Logger:
    """Create and configure a project logger.

    This function avoids duplicated handlers when called repeatedly.

    Args:
        name: Logger name, typically __name__.
        config: Logging configuration.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.level.upper(), logging.INFO))
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if config.log_to_file:
        log_dir = Path(config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_path = log_dir / config.log_filename

        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger