# src/ntc/widgets/metric_card.py
"""Карточка метрики процесса."""
from pathlib import Path

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ntc.ui.ui_metric_card import Ui_MetricCard


class MetricCard(QWidget, Ui_MetricCard):
    """Карточка: имя процесса + sent/recv + статус-индикатор."""

    def __init__(self, name: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._load_css()
        self.update_values(name, 0.0, 0.0, active=False)

    def _load_css(self) -> None:
        path = Path(__file__).parent.parent / "styles" / "css" / "widgets" / "metric_card.css"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def update_values(
        self, name: str, sent: float, recv: float, *, active: bool = True
    ) -> None:
        """Обновляет данные карточки.

        Args:
            name: имя процесса.
            sent: скорость отдачи, Б/с.
            recv: скорость приёма, Б/с.
            active: индикатор активности.
        """
        self.name_label.setText(name or "—")
        self.values_label.setText(f"↓ {recv:.0f} Б/с   ↑ {sent:.0f} Б/с")
        self.status_label.setText("●" if active else "○")
        self.status_label.setProperty("active", "true" if active else "false")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
