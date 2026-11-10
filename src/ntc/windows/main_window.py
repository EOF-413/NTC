"""Главное окно приложения."""
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal
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
    exit_requested = pyqtSignal()
    closing = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self._toasts: set[QObject] = set()
        self._allow_exit = False
        self._setup_tray()
        self._wire_signals()

    def _setup_tray(self) -> None:
        self._tray = QSystemTrayIcon(self)
        self._tray.setToolTip("Network Traffic Controller")
        menu = QMenu()
        act_show = QAction("Показать", self)
        act_hide = QAction("Скрыть", self)
        act_quit = QAction("Выход", self)
        act_show.triggered.connect(self.showNormal)
        act_hide.triggered.connect(self.hide)
        act_quit.triggered.connect(self.exit_requested)
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
        self.lbl_total.setText(f"Сеть: {total:.0f} Б/с")

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
        toast = Toast(f"Заблокировано: {process}", body, self)
        self._toasts.add(toast)
        toast.destroyed.connect(self._on_toast_destroyed)
        toast.show()

    def _on_toast_destroyed(self, toast: QObject | None = None) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)

    def exit_app(self) -> None:
        """Закрывает окно и завершает приложение из команды выхода в трее."""
        self._allow_exit = True
        self.close()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()

    def closeEvent(self, event) -> None:  # noqa: N802
        if not self._allow_exit:
            self.hide()
            event.ignore()
            return
        self.closing.emit()
        self._tray.hide()
        super().closeEvent(event)
