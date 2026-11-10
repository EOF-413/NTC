# src/ntc/utils/logger.py
"""Настройка логирования с ротацией файла."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_INITIALIZED = False


def setup_logger(name: str = "ntc") -> logging.Logger:
    """Возвращает именованный логгер с файловым и консольным обработчиком.

    Args:
        name: имя логгера.

    Returns:
        Настроенный logger.
    """
    global _INITIALIZED  # noqa: PLW0603

    logger = logging.getLogger(name)
    if _INITIALIZED:
        return logger

    logger.setLevel(logging.DEBUG)

    # src/ntc/utils/logger.py -> src/ -> logs/
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    fh = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    _INITIALIZED = True
    return logger
