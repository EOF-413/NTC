# src/ntc/services/blocker_service.py
"""Абстракция блокировки трафика (pydivert / netsh / iptables)."""
import subprocess
import sys

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ntc.services.database_service import DatabaseService
from ntc.utils.admin_check import is_admin
from ntc.utils.logger import setup_logger

logger = setup_logger("blocker")


class _PydivertWorker(QObject):
    """Перехват пакетов через pydivert (Windows)."""

    blocked = pyqtSignal(str, str, int)   # process, ip, port
    error_occurred = pyqtSignal(str)

    def __init__(self, db: DatabaseService) -> None:
        super().__init__()
        self._db = db
        self._running = True

    def stop(self) -> None:
        """Останавливает цикл перехвата."""
        self._running = False

    def run(self) -> None:
        """Основной цикл pydivert."""
        try:
            import pydivert  # type: ignore
        except ImportError as exc:
            logger.error("pydivert недоступен: %s", exc)
            self.error_occurred.emit("pydivert недоступен — блокировка отключена")
            return

        try:
            proc_rules = {
                e.value.lower()
                for e in self._db.list_blacklist()
                if e.type == "process" and e.enabled
            }
            ip_rules = {
                e.value for e in self._db.list_blacklist()
                if e.type == "ip" and e.enabled
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Не удалось прочитать правила: %s", exc)
            self.error_occurred.emit(str(exc))
            return

        try:
            with pydivert.WinDivert(
                "tcp.DstPort != 0 or udp.DstPort != 0"
            ) as w:
                while self._running:
                    try:
                        packet = w.recv()
                    except Exception:  # noqa: BLE001
                        if not self._running:
                            break
                        continue

                    if packet.dst_addr in ip_rules:
                        self.blocked.emit("?", packet.dst_addr, int(packet.dst_port))
                        continue  # не отправляем — пакет отбрасывается

                    # pydivert не даёт pid напрямую; для process-правил
                    # рекомендуется netsh-fallback либо эвристика по порту.
                    try:
                        w.send(packet)
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            logger.exception("Ошибка pydivert: %s", exc)
            self.error_occurred.emit(str(exc))


class BlockerService(QObject):
    """Абстракция блокировки трафика."""

    connection_blocked = pyqtSignal(str, str, int)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(bool)

    def __init__(self, db: DatabaseService) -> None:
        """Создаёт сервис.

        Args:
            db: сервис БД (для чтения правил).
        """
        super().__init__()
        self._db = db
        self._thread: QThread | None = None
        self._worker: _PydivertWorker | None = None
        self._active = False

    @property
    def is_active(self) -> bool:
        """Активна ли блокировка."""
        return self._active

    def can_block(self) -> bool:
        """Есть ли права и поддержка платформы."""
        return is_admin() and sys.platform in ("win32", "linux")

    def start(self) -> bool:
        """Запускает механизм блокировки."""
        if not self.can_block():
            logger.warning("Нет прав/платформа не поддерживает блокировку")
            return False
        if sys.platform == "win32":
            return self._start_windows()
        return self._start_linux()

    def _start_windows(self) -> bool:
        try:
            import pydivert  # type: ignore  # noqa: F401
        except ImportError:
            logger.warning("pydivert недоступен → netsh-fallback")
            return self._start_netsh_fallback()

        self._worker = _PydivertWorker(self._db)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.blocked.connect(self.connection_blocked)
        self._worker.error_occurred.connect(self.error_occurred)
        self._thread.start()
        self._active = True
        self.status_changed.emit(True)
        return True

    def _start_netsh_fallback(self) -> bool:
        rules = self._db.list_blacklist()
        for rule in rules:
            if not rule.enabled or rule.type != "ip":
                continue
            try:
                subprocess.run(  # noqa: S603, S607
                    [
                        "netsh", "advfirewall", "firewall", "add", "rule",
                        f"name=NTC_{rule.id}", "dir=out", "action=block",
                        f"remoteip={rule.value}",
                    ],
                    check=False, capture_output=True,
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("netsh error: %s", exc)
        self._active = True
        self.status_changed.emit(True)
        return True

    def _start_linux(self) -> bool:
        rules = self._db.list_blacklist()
        for rule in rules:
            if not rule.enabled or rule.type != "ip":
                continue
            try:
                subprocess.run(  # noqa: S603, S607
                    ["iptables", "-A", "OUTPUT", "-d", rule.value, "-j", "DROP"],
                    check=False, capture_output=True,
                )
            except FileNotFoundError:
                logger.error("iptables не найден")
                self.error_occurred.emit("iptables не найден")
                return False
        self._active = True
        self.status_changed.emit(True)
        return True

    def stop(self) -> None:
        """Останавливает блокировку."""
        if self._worker is not None:
            self._worker.stop()
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(2000)
            self._thread = None
            self._worker = None
        self._active = False
        self.status_changed.emit(False)

    def reload_rules(self) -> None:
        """Перезапускает блокировку с актуальными правилами."""
        if self._active:
            self.stop()
            self.start()
