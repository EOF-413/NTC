# src/ntc/services/settings_service.py
"""Чтение/запись settings.json."""
import json
from dataclasses import asdict
from pathlib import Path

from ntc.models.settings import Settings
from ntc.utils.logger import setup_logger

logger = setup_logger("settings")


class SettingsService:
    """Загружает и сохраняет пользовательские настройки."""

    def __init__(self, path: Path) -> None:
        """Создаёт сервис.

        Args:
            path: путь к settings.json.
        """
        self._path = path

    def load(self) -> Settings:
        """Читает настройки; при ошибке возвращает дефолтные."""
        if not self._path.exists():
            return Settings()
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Не удалось прочитать настройки: %s", exc)
            return Settings()
        return Settings(
            dark_theme=bool(data.get("dark_theme", True)),
            notifications_global=bool(data.get("notifications_global", True)),
            muted_apps=list(data.get("muted_apps", [])),
        )

    def save(self, settings: Settings) -> None:
        """Сохраняет настройки в файл."""
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(asdict(settings), f, ensure_ascii=False, indent=2)
        except OSError as exc:
            logger.error("Не удалось сохранить настройки: %s", exc)
