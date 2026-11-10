# src/ntc/services/monitor_service.py
"""Мониторинг сетевой активности через psutil в фоновом QThread."""
import time

import psutil
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ntc.models.connection_info import ConnectionInfo
from ntc.utils.logger import setup_logger

logger = setup_logger("monitor")


class MonitorWorker(QObject):
    """Цикл опроса psutil (в отдельном QThread)."""

    metrics_ready = pyqtSignal(list)   # list[ConnectionInfo]
    error_occurred = pyqtSignal(str)

    def __init__(self, interval: float = 1.5) -> None:
        super().__init__()
        self._interval = interval
        self._running = True
        self._force = False
        self._prev: dict[int, tuple[int, int, float]] = {}

    def force_poll(self) -> None:
        """Триггер форс-опроса (прерывает паузу)."""
        self._force = True

    def stop(self) -> None:
        """Останавливает цикл."""
        self._running = False

    def run(self) -> None:
        """Основной цикл (вызывается из QThread.started)."""
        while self._running:
            try:
                self._poll()
            except Exception as exc:  # noqa: BLE001
                logger.exception("Ошибка опроса psutil: %s", exc)
                self.error_occurred.emit(str(exc))

            # разбиваем паузу на 100 мс, чтобы force_poll срабатывал быстро
            steps = max(int(self._interval / 0.1), 1)
            for _ in range(steps):
                if not self._running or self._force:
                    break
                time.sleep(0.1)
            self._force = False

    def _poll(self) -> None:
        now = time.monotonic()
        pid_to_conns: dict[int, list] = {}
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.pid is None:
                    continue
                pid_to_conns.setdefault(conn.pid, []).append(conn)
        except (psutil.AccessDenied, OSError) as exc:
            logger.warning("net_connections: %s", exc)
            return

        results: list[ConnectionInfo] = []
        for pid, conns in pid_to_conns.items():
            try:
                proc = psutil.Process(pid)
                io = proc.io_counters()
                sent, recv = int(io.write_bytes), int(io.read_bytes)
                prev = self._prev.get(pid)
                if prev is not None:
                    dt = max(now - prev[2], 0.001)
                    sent_speed = max((sent - prev[0]) / dt, 0.0)
                    recv_speed = max((recv - prev[1]) / dt, 0.0)
                else:
                    sent_speed = recv_speed = 0.0
                self._prev[pid] = (sent, recv, now)

                remotes = [f"{c.raddr.ip}:{c.raddr.port}" for c in conns if c.raddr]
                results.append(
                    ConnectionInfo(
                        name=proc.name(), pid=pid,
                        sent=sent_speed, recv=recv_speed,
                        connections=len(conns),
                        remote=remotes[0] if remotes else "-",
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                logger.debug("Процесс %d недоступен — пропуск", pid)
                continue

        results.sort(key=lambda c: c.sent + c.recv, reverse=True)
        self.metrics_ready.emit(results)


class MonitorService(QObject):
    """Публичный фасад над фоновым QThread."""

    metrics_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, interval: float = 1.5) -> None:
        super().__init__()
        self._thread = QThread()
        self._worker = MonitorWorker(interval)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.metrics_ready.connect(self.metrics_ready)
        self._worker.error_occurred.connect(self.error_occurred)

    def start(self) -> None:
        """Запускает QThread."""
        self._thread.start()

    def stop(self) -> None:
        """Останавливает воркер и поток."""
        self._worker.stop()
        self._thread.quit()
        self._thread.wait(2000)

    def force_poll(self) -> None:
        """Триггерит форс-опрос."""
        self._worker.force_poll()
