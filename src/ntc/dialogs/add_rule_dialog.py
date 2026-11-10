# src/ntc/dialogs/add_rule_dialog.py
"""Диалог добавления правила."""
import ipaddress

from PyQt6.QtWidgets import QDialog, QMessageBox

from ntc.ui.ui_add_rule_dialog import Ui_AddRuleDialog


class AddRuleDialog(QDialog, Ui_AddRuleDialog):
    """Простой диалог: тип + значение."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def get_data(self) -> tuple[str, str]:
        """Возвращает (type, value)."""
        return self.type_combo.currentData(), self.value_edit.text().strip()

    def accept(self) -> None:
        rule_type, value = self.get_data()
        if not value:
            QMessageBox.warning(self, "Некорректное правило", "Укажите значение.")
            return
        if rule_type == "ip":
            try:
                ipaddress.ip_network(value, strict=False)
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Некорректное правило",
                    "Введите IPv4/IPv6-адрес или сеть в формате CIDR.",
                )
                return
        super().accept()
