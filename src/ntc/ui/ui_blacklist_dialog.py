# src/ntc/ui/ui_blacklist_dialog.py
"""Ui_BlacklistDialog."""
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QPushButton, QTableView, QVBoxLayout,
)


class Ui_BlacklistDialog:
    def setupUi(self, dialog: QDialog) -> None:
        dialog.setObjectName("BlacklistDialog")
        dialog.resize(640, 420)

        root = QVBoxLayout(dialog)

        self.table_view = QTableView(dialog)
        self.table_view.setObjectName("table_view")
        self.table_view.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        root.addWidget(self.table_view, 1)

        buttons = QHBoxLayout()
        self.btn_add = QPushButton("Добавить", dialog)
        self.btn_delete = QPushButton("Удалить", dialog)
        self.btn_close = QPushButton("Закрыть", dialog)
        buttons.addWidget(self.btn_add)
        buttons.addWidget(self.btn_delete)
        buttons.addStretch()
        buttons.addWidget(self.btn_close)
        root.addLayout(buttons)

        self.retranslateUi(dialog)

    def retranslateUi(self, dialog: QDialog) -> None:  # noqa: N802
        dialog.setWindowTitle("Чёрный список")
