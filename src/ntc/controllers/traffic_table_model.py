# src/ntc/controllers/traffic_table_model.py
"""QAbstractTableModel-адаптер для QTableView."""
from typing import ClassVar

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt

from ntc.models.connection_info import ConnectionInfo


def _fmt_bytes(value: float | None) -> str:
    """Форматирует скорость в человекочитаемый вид."""
    if value is None:
        return "—"
    units = ["Б", "КБ", "МБ", "ГБ"]
    v = float(value)
    i = 0
    while v >= 1024 and i < len(units) - 1:
        v /= 1024
        i += 1
    return f"{v:.1f} {units[i]}/с"


class TrafficTableModel(QAbstractTableModel):
    """Табличная модель монитора трафика."""

    HEADERS: ClassVar[tuple[str, ...]] = (
        "Процесс", "PID", "Отправлено", "Получено", "Соединения", "Удалённый адрес"
    )

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[ConnectionInfo] = []

    def update_rows(self, rows: list[ConnectionInfo]) -> None:
        """Заменяет содержимое таблицы."""
        self.beginResetModel()
        self._rows = list(rows)
        self.endResetModel()

    def clear(self) -> None:
        """Сбрасывает скорости, но оставляет строки."""
        self.beginResetModel()
        self._rows = [
            ConnectionInfo(
                name=r.name, pid=r.pid, sent=None, recv=None,
                connections=r.connections, remote=r.remote,
            )
            for r in self._rows
        ]
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if (
            role == Qt.ItemDataRole.ToolTipRole
            and orientation == Qt.Orientation.Horizontal
            and section in (2, 3)
        ):
            return "psutil предоставляет общий сетевой трафик, но не скорость по процессам"
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)

    def data(
        self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        row = self._rows[index.row()]
        col = index.column()
        if col == 0:
            return row.name
        if col == 1:
            return row.pid
        if col == 2:
            return _fmt_bytes(row.sent)
        if col == 3:
            return _fmt_bytes(row.recv)
        if col == 4:
            return row.connections
        if col == 5:
            return row.remote
        return None
