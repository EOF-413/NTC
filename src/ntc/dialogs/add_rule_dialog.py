# src/ntc/dialogs/add_rule_dialog.py
"""Диалог добавления правила."""
from pathlib import Path

from PyQt6.QtWidgets import QDialog

from ntc.ui.ui_add_rule_dialog import Ui_AddRuleDialog


class AddRuleDialog(QDialog, Ui_AddRuleDialog):
    """Простой диалог: тип + значение."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._load_css()

    def _load_css(self) -> None:
        path = Path(__file__).parent.parent / "styles" / "css" / "dialogs" / "add_rule_dialog.css"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def get_data(self) -> tuple[str, str]:
        """Возвращает (type, value)."""
        return self.type_combo.currentData(), self.value_edit.text().strip()
