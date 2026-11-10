# src/ntc/widgets/traffic_chart.py
"""Кастомный график скоростей upload/download (paintEvent)."""
from collections import deque

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPaintEvent, QPalette, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget

from ntc.ui.ui_traffic_chart import Ui_TrafficChart


class TrafficChart(QWidget, Ui_TrafficChart):
    """График upload/download на кастомном paintEvent."""

    MAX_POINTS = 60
    COLOR_UP = "#3B82F6"
    COLOR_DOWN = "#22C55E"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setMinimumHeight(160)
        self._upload: deque[float] = deque(maxlen=self.MAX_POINTS)
        self._download: deque[float] = deque(maxlen=self.MAX_POINTS)

    def push(self, upload: float, download: float) -> None:
        """Добавляет точку и перерисовывает."""
        self._upload.append(max(upload, 0.0))
        self._download.append(max(download, 0.0))
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self.palette().color(self.backgroundRole()))

        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        # сетка
        painter.setPen(
            QPen(
                self.palette().color(QPalette.ColorRole.Mid),
                1,
                Qt.PenStyle.DotLine,
            )
        )
        for i in range(1, 4):
            y = h * i / 4
            painter.drawLine(0, int(y), w, int(y))

        max_val = max([*self._upload, *self._download, 1024.0])
        self._draw_series(painter, self._upload, QColor(self.COLOR_UP), w, h, max_val)
        self._draw_series(painter, self._download, QColor(self.COLOR_DOWN), w, h, max_val)

    def _draw_series(
        self, painter: QPainter, data: deque[float],
        color: QColor, w: int, h: int, max_val: float,
    ) -> None:
        if len(data) < 2:
            return
        pen = QPen(color, 2)
        painter.setPen(pen)
        step = w / (self.MAX_POINTS - 1)
        pts = [
            QPointF(i * step, h - (v / max_val) * (h - 10) - 5)
            for i, v in enumerate(data)
        ]
        painter.drawPolyline(QPolygonF(pts))
