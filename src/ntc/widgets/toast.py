# src/ntc/widgets/toast.py
"""Всплывающее уведомление без фокуса."""
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PyQt6.QtWidgets import QWidget

from ntc.ui.ui_toast import Ui_Toast


class Toast(QWidget, Ui_Toast):
    """Toast с автозакрытием, не забирает фокус."""

    WIDTH, HEIGHT, DURATION_MS = 340, 116, 4000

    def __init__(self, title: str, body: str, parent: QWidget | None = None) -> None:
        super().__init__(
            parent,
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint,
        )
        self.setupUi(self)
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.title_label.setText(title)
        self.body_label.setText(body)
        self._place()
        self._animate()

    def _place(self) -> None:
        screen = self.screen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        self.move(geo.right() - self.WIDTH - 20, geo.bottom() - self.HEIGHT - 20)

    def _animate(self) -> None:
        self.setWindowOpacity(0.0)
        self.show()
        self._fade = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade.setDuration(220)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade.start()
        QTimer.singleShot(self.DURATION_MS, self.close)
