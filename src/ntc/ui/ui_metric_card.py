# src/ntc/ui/ui_metric_card.py
"""Ui_MetricCard."""
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class Ui_MetricCard:
    def setupUi(self, widget: QWidget) -> None:
        widget.setObjectName("MetricCard")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        self.name_label = QLabel("—", widget)
        self.name_label.setObjectName("MetricName")
        self.values_label = QLabel("↓ 0 Б/с   ↑ 0 Б/с", widget)
        self.values_label.setObjectName("MetricValues")
        self.status_label = QLabel("○", widget)
        self.status_label.setObjectName("MetricStatus")

        layout.addWidget(self.name_label)
        layout.addWidget(self.values_label)
        layout.addWidget(self.status_label)
