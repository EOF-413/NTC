# src/ntc/dialogs/blacklist_dialog.py
"""Диалог управления чёрным списком."""
from pathlib import Path

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtWidgets import QDialog, QMessageBox

from ntc.dialogs.add_rule_dialog import AddRuleDialog
from ntc.models.blacklist_entry import BlacklistEntry
from ntc.services.database_service import DatabaseService
from ntc.ui.ui_blacklist_dialog import Ui_BlacklistDialog


class _BlacklistTableModel(QAbstractTableModel):
    HEADERS = ["ID", "Тип", "Значение", "Активно"]

    def __init__(self, entries: list[BlacklistEntry]) -> None:
        super().__init__()
        self._entries = entries

    def refresh(self, entries: list[BlacklistEntry]) -> None:
        """Заменяет данные."""
        self.beginResetModel()
        self._entries = entries
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._entries)

    def columnCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None
        return self.HEADERS[section]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        e = self._entries[index.row()]
        col = index.column()
        if col == 0:
            return e.id
        if col == 1:
            return "Процесс" if e.type == "process" else "IP"
        if col == 2:
            return e.value
        if col == 3:
            return "✓" if e.enabled else "✗"
        return None

    def get_entry(self, row: int) -> BlacklistEntry | None:
        return self._entries[row] if 0 <= row < len(self._entries) else None


class BlacklistDialog(QDialog, Ui_BlacklistDialog):
    """Список правил: добавление / удаление."""

    def __init__(self, db: DatabaseService, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._db = db
        self._model = _BlacklistTableModel(db.list_blacklist())
        self.table_view.setModel(self._model)
        self._load_css()

        self.btn_add.clicked.connect(self._on_add)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_close.clicked.connect(self.accept)

    def _load_css(self) -> None:
        path = Path(__file__).parent.parent / "styles" / "css" / "dialogs" / "blacklist_dialog.css"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _on_add(self) -> None:
        dlg = AddRuleDialog(self)
        if not dlg.exec():
            return
        rule_type, value = dlg.get_data()
        if not value:
            return
        try:
            self._db.add_blacklist(BlacklistEntry(type=rule_type, value=value))
            self._model.refresh(self._db.list_blacklist())
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Ошибка БД", str(exc))

    def _on_delete(self) -> None:
        idx = self.table_view.currentIndex()
        if not idx.isValid():
            return
        entry = self._model.get_entry(idx.row())
        if entry is None or entry.id is None:
            return
        try:
            self._db.delete_blacklist(entry.id)
            self._model.refresh(self._db.list_blacklist())
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Ошибка БД", str(exc))
