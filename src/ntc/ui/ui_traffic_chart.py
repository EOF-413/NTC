# src/ntc/ui/ui_traffic_chart.py
"""Ui_TrafficChart — только objectName (виджет полностью кастомный)."""
from PyQt6.QtWidgets import QWidget


class Ui_TrafficChart:
    def setupUi(self, widget: QWidget) -> None:
        widget.setObjectName("TrafficChart")
