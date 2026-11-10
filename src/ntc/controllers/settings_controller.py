# src/ntc/controllers/settings_controller.py
"""Контроллер диалога настроек."""
from PyQt6.QtWidgets import QWidget

from ntc.models.settings import Settings
from ntc.services.settings_service import SettingsService


class SettingsController:
    """Связывает диалог настроек и сервис настроек."""

    def __init__(
        self, svc: SettingsService, settings: Settings, parent: QWidget
    ) -> None:
        self._svc = svc
        self._settings = settings
        self._parent = parent

    def open(self) -> Settings:
        """Открывает диалог и сохраняет изменения (если OK)."""
        from ntc.dialogs.settings_dialog import SettingsDialog

        dlg = SettingsDialog(self._settings, self._parent)
        if dlg.exec():
            self._settings = dlg.get_settings()
            self._svc.save(self._settings)
        return self._settings
