"""Главное окно приложения."""
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QMenu, QSystemTrayIcon

from ntc.ui.ui_main_window import Ui_MainWindow
from ntc.widgets.toast import Toast


class MainWindow(QMainWindow, Ui_MainWindow):
    """QMainWindow + Ui_MainWindow + системный трей."""

    refresh_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    blacklist_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    closing = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self._load_css()
        self._setup_tray()
        self._wire_signals()

    def _load_css(self) -> None:
        path = Path(__file__).parent.parent / "styles" / "css" / "windows" / "main_window.css"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _setup_tray(self) -> None:
        self._tray = QSystemTrayIcon(self)
        self._tray.setToolTip("Network Traffic Controller")
        menu = QMenu()
        act_show = QAction("Показать", self)
        act_hide = QAction("Скрыть", self)
        act_quit = QAction("Выход", self)
        act_show.triggered.connect(self.showNormal)
        act_hide.triggered.connect(self.hide)
        act_quit.triggered.connect(self.close)
        menu.addAction(act_show)
        menu.addAction(act_hide)
        menu.addSeparator()
        menu.addAction(act_quit)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _wire_signals(self) -> None:
        self.btn_refresh.clicked.connect(self.refresh_requested)
        self.btn_clear.clicked.connect(self.clear_requested)
        self.btn_blacklist.clicked.connect(self.blacklist_requested)
        self.btn_settings.clicked.connect(self.settings_requested)

    def set_table_model(self, model) -> None:
        """Устанавливает табличную модель."""
        self.table_view.setModel(model)

    def update_chart(self, upload: float, download: float) -> None:
        """Пушит точку в график."""
        self.traffic_chart.push(upload, download)

    def update_total(self, total: float) -> None:
        """Обновляет счётчик в статус-баре."""
        self.lbl_total.setText(f"Всего: {total:.0f} Б/с")

    def set_status(self, message: str) -> None:
        """Сообщение в статус-бар."""
        self.statusbar.showMessage(message, 3000)

    def set_privilege(self, is_admin: bool) -> None:
        """Индикатор прав."""
        self.lbl_privilege.setText("Админ" if is_admin else "Мониторинг")

    def disable_blocking_buttons(self) -> None:
        """Без прав кнопка чёрного списка выключена."""
        self.btn_blacklist.setEnabled(False)

    def set_blocking_active(self, active: bool) -> None:
        """Индикатор активной блокировки."""
        self.lbl_privilege.setText("Блокировка" if active else "Мониторинг")

    def show_toast(self, process: str, ip: str, port: int) -> None:
        """Показывает toast-уведомление."""
        body = f"-> {ip}:{port}\n{datetime.now().strftime('%H:%M:%S')}"
        toast = Toast(f"Заблокировано: {process}", body)
        toast.show()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()

    def closeEvent(self, event) -> None:  # noqa: N802
        self.closing.emit()
        self._tray.hide()
        super().closeEvent(event)
