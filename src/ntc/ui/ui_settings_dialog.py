# src/ntc/ui/ui_settings_dialog.py
"""Ui_SettingsDialog."""
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit,
    QVBoxLayout,
)


class Ui_SettingsDialog:
    def setupUi(self, dialog: QDialog) -> None:
        dialog.setObjectName("SettingsDialog")
        dialog.resize(440, 260)

        root = QVBoxLayout(dialog)
        form = QFormLayout()

        self.dark_check = QCheckBox("Тёмная тема", dialog)
        self.notify_check = QCheckBox("Уведомления глобально", dialog)
        self.muted_edit = QLineEdit(dialog)
        self.muted_edit.setPlaceholderText("chrome.exe, discord.exe")

        form.addRow("Тема:", self.dark_check)
        form.addRow("Уведомления:", self.notify_check)
        form.addRow(QLabel("Mute (через запятую):", dialog))
        form.addRow(self.muted_edit)
        root.addLayout(form)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            dialog,
        )
        self.button_box.accepted.connect(dialog.accept)
        self.button_box.rejected.connect(dialog.reject)
        root.addWidget(self.button_box)

        self.retranslateUi(dialog)

    def retranslateUi(self, dialog: QDialog) -> None:  # noqa: N802
        dialog.setWindowTitle("Настройки")
