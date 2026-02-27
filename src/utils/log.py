# src/utils/log.py
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "historymosaic.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Ensure logs directory exists
LOG_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------
# Logger setup
# ---------------------------------------------------
def _build_logger() -> logging.Logger:
    logger = logging.getLogger("historymosaic")

    if logger.handlers:
        return logger  # Already configured — avoid duplicate handlers

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Rotating file handler — 5 MB per file, keep 3 backups
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = _build_logger()


# ---------------------------------------------------
# Public API — maintains backward compatibility
# ---------------------------------------------------
def log_info(message: str) -> None:
    logger.info(message)


def log_warning(message: str) -> None:
    logger.warning(message)


def log_error(message: str) -> None:
    logger.error(message)


def log_debug(message: str) -> None:
    logger.debug(message)
