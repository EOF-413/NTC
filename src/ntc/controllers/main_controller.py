# src/ntc/controllers/main_controller.py
"""Главный контроллер — склейка View/Model/Services."""
from pathlib import Path

from PyQt6.QtCore import QObject

from ntc.controllers.traffic_table_model import TrafficTableModel
from ntc.models.incident import Incident
from ntc.services.blocker_service import BlockerService
from ntc.services.database_service import DatabaseService
from ntc.services.monitor_service import MonitorService
from ntc.services.settings_service import SettingsService
from ntc.utils.admin_check import is_admin
from ntc.utils.logger import setup_logger

logger = setup_logger("main_ctrl")


class MainController(QObject):
    """Связывает главное окно и сервисы через сигналы."""

    def __init__(self, window, base_dir: Path) -> None:
        """Создаёт контроллер.

        Args:
            window: экземпляр MainWindow.
            base_dir: каталог для ntc.db и settings.json (src/).
        """
        super().__init__(window)  # parent = window, чтобы жил вместе с окном
        self._window = window
        self._base = base_dir

        self._db = DatabaseService(base_dir / "ntc.db")
        self._settings_svc = SettingsService(base_dir / "settings.json")
        self._settings = self._settings_svc.load()

        self._monitor = MonitorService(interval=1.5)
        self._blocker = BlockerService(self._db)

        self._model = TrafficTableModel()
        window.set_table_model(self._model)

        self._wire()
        self._start_monitoring()
        self._try_blocking()

    # ----- wiring -----
    def _wire(self) -> None:
        self._window.refresh_requested.connect(self._on_refresh)
        self._window.clear_requested.connect(self._on_clear)
        self._window.blacklist_requested.connect(self._on_blacklist)
        self._window.settings_requested.connect(self._on_settings)
        self._window.closing.connect(self.shutdown)

        self._monitor.metrics_ready.connect(self._on_metrics)
        self._monitor.error_occurred.connect(self._on_error)

        self._blocker.connection_blocked.connect(self._on_blocked)
        self._blocker.error_occurred.connect(self._on_error)

    def _start_monitoring(self) -> None:
        self._monitor.start()
        self._window.set_status("Мониторинг запущен")
        self._window.set_privilege(is_admin())

    def _try_blocking(self) -> None:
        if not self._blocker.can_block():
            self._window.disable_blocking_buttons()
            return
        ok = self._blocker.start()
        self._window.set_blocking_active(ok)

    # ----- slots -----
    def _on_refresh(self) -> None:
        self._monitor.force_poll()

    def _on_clear(self) -> None:
        self._model.clear()
        self._window.set_status("Статистика сброшена")

    def _on_metrics(self, rows: list) -> None:
        self._model.update_rows(rows)
        total_sent = sum(r.sent for r in rows)
        total_recv = sum(r.recv for r in rows)
        self._window.update_total(total_sent + total_recv)
        self._window.update_chart(total_sent, total_recv)

    def _on_blocked(self, process: str, ip: str, port: int) -> None:
        if not self._settings.notifications_global:
            return
        if process.lower() in {m.lower() for m in self._settings.muted_apps}:
            return
        self._window.show_toast(process, ip, port)
        try:
            self._db.add_incident(
                Incident(process=process, pid=0, remote_ip=ip,
                         remote_port=port, action="blocked")
            )
            logger.info("Инцидент: %s → %s:%d", process, ip, port)
        except Exception as exc:  # noqa: BLE001
            logger.error("Не удалось сохранить инцидент: %s", exc)

    def _on_error(self, message: str) -> None:
        logger.error("Сервисная ошибка: %s", message)
        self._window.show_toast("Ошибка", message, 0)

    def _on_blacklist(self) -> None:
        from ntc.controllers.blacklist_controller import BlacklistController

        BlacklistController(self._db, self._blocker, self._window).open()

    def _on_settings(self) -> None:
        from ntc.controllers.settings_controller import SettingsController

        sc = SettingsController(self._settings_svc, self._settings, self._window)
        self._settings = sc.open()

    # ----- lifecycle -----
    def shutdown(self) -> None:
        """Останавливает сервисы перед закрытием окна."""
        try:
            self._monitor.stop()
            self._blocker.stop()
        except Exception as exc:  # noqa: BLE001
            logger.error("Ошибка остановки: %s", exc)
