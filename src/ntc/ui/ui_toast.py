# src/ntc/ui/ui_toast.py
"""Ui_Toast."""
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class Ui_Toast:
    def setupUi(self, widget: QWidget) -> None:
        widget.setObjectName("Toast")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        self.title_label = QLabel("", widget)
        self.title_label.setObjectName("ToastTitle")
        self.body_label = QLabel("", widget)
        self.body_label.setObjectName("ToastBody")
        self.body_label.setWordWrap(True)

        layout.addWidget(self.title_label)
        layout.addWidget(self.body_label)
