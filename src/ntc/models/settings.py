# src/ntc/models/settings.py
"""Пользовательские настройки."""
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Настройки приложения (сериализуются в settings.json)."""

    dark_theme: bool = True
    notifications_global: bool = True
    muted_apps: list[str] = field(default_factory=list)
