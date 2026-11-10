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
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Не удалось прочитать настройки: %s", exc)
            return Settings()
        if not isinstance(data, dict):
            logger.error("Формат настроек должен быть JSON-объектом")
            return Settings()

        dark_theme = data.get("dark_theme", True)
        notifications_global = data.get("notifications_global", True)
        muted_apps = data.get("muted_apps", [])
        if not isinstance(dark_theme, bool):
            logger.warning("Некорректная dark_theme; используется значение по умолчанию")
            dark_theme = True
        if not isinstance(notifications_global, bool):
            logger.warning(
                "Некорректная notifications_global; используется значение по умолчанию"
            )
            notifications_global = True
        if not isinstance(muted_apps, list) or not all(
            isinstance(app, str) for app in muted_apps
        ):
            logger.warning("Некорректный muted_apps; список очищен")
            muted_apps = []

        return Settings(
            dark_theme=dark_theme,
            notifications_global=notifications_global,
            muted_apps=[app.strip() for app in muted_apps if app.strip()],
        )

    def save(self, settings: Settings) -> None:
        """Сохраняет настройки в файл."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(asdict(settings), f, ensure_ascii=False, indent=2)
        except OSError as exc:
            logger.error("Не удалось сохранить настройки: %s", exc)
