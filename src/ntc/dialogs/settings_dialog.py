# src/ntc/dialogs/settings_dialog.py
"""Диалог настроек."""
from PyQt6.QtWidgets import QDialog

from ntc.models.settings import Settings
from ntc.ui.ui_settings_dialog import Ui_SettingsDialog


class SettingsDialog(QDialog, Ui_SettingsDialog):
    """Тема, нотификации, mute-приложения."""

    def __init__(self, settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.dark_check.setChecked(settings.dark_theme)
        self.notify_check.setChecked(settings.notifications_global)
        self.muted_edit.setText(", ".join(settings.muted_apps))

    def get_settings(self) -> Settings:
        """Возвращает настройки из UI."""
        muted = [s.strip() for s in self.muted_edit.text().split(",") if s.strip()]
        return Settings(
            dark_theme=self.dark_check.isChecked(),
            notifications_global=self.notify_check.isChecked(),
            muted_apps=muted,
        )
