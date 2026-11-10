# src/ntc/ui/ui_add_rule_dialog.py
"""Ui_AddRuleDialog."""
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout,
)


class Ui_AddRuleDialog:
    def setupUi(self, dialog: QDialog) -> None:
        dialog.setObjectName("AddRuleDialog")
        dialog.resize(420, 180)

        root = QVBoxLayout(dialog)
        form = QFormLayout()

        self.type_combo = QComboBox(dialog)
        self.type_combo.addItem("Процесс", "process")
        self.type_combo.addItem("IP-адрес", "ip")

        self.value_edit = QLineEdit(dialog)
        self.value_edit.setPlaceholderText("chrome.exe или 8.8.8.8")

        form.addRow("Тип:", self.type_combo)
        form.addRow("Значение:", self.value_edit)
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
        dialog.setWindowTitle("Добавить правило")
