# src/ntc/services/monitor_service.py
"""Мониторинг сетевой активности через psutil в фоновом QThread."""
import threading
import time

import psutil
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ntc.models.connection_info import ConnectionInfo
from ntc.utils.logger import setup_logger

logger = setup_logger("monitor")


class MonitorWorker(QObject):
    """Цикл опроса psutil (в отдельном QThread)."""

    metrics_ready = pyqtSignal(list)   # list[ConnectionInfo]
    network_metrics_ready = pyqtSignal(float, float)
    error_occurred = pyqtSignal(str)

    def __init__(self, interval: float = 1.5) -> None:
        super().__init__()
        self._interval = interval
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()
        self._prev_network: tuple[int, int, float] | None = None

    def force_poll(self) -> None:
        """Триггер форс-опроса (прерывает паузу)."""
        self._wake_event.set()

    def stop(self) -> None:
        """Останавливает цикл."""
        self._stop_event.set()
        self._wake_event.set()

    def run(self) -> None:
        """Основной цикл (вызывается из QThread.started)."""
        while not self._stop_event.is_set():
            self._wake_event.clear()
            try:
                self._poll()
            except Exception as exc:
                logger.exception("Ошибка опроса psutil: %s", exc)
                self.error_occurred.emit(str(exc))
            self._wake_event.wait(self._interval)

    def _poll(self) -> None:
        now = time.monotonic()
        net_io = psutil.net_io_counters()
        if net_io is not None:
            sent, recv = int(net_io.bytes_sent), int(net_io.bytes_recv)
            prev = self._prev_network
            if prev is None:
                sent_speed = recv_speed = 0.0
            else:
                dt = max(now - prev[2], 0.001)
                sent_speed = max((sent - prev[0]) / dt, 0.0)
                recv_speed = max((recv - prev[1]) / dt, 0.0)
            self._prev_network = (sent, recv, now)
            self.network_metrics_ready.emit(sent_speed, recv_speed)

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
                remotes = [f"{c.raddr.ip}:{c.raddr.port}" for c in conns if c.raddr]
                results.append(
                    ConnectionInfo(
                        name=proc.name(), pid=pid,
                        sent=None, recv=None,
                        connections=len(conns),
                        remote=remotes[0] if remotes else "-",
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                logger.debug("Процесс %d недоступен — пропуск", pid)
                continue

        results.sort(key=lambda c: c.connections, reverse=True)
        self.metrics_ready.emit(results)


class MonitorService(QObject):
    """Публичный фасад над фоновым QThread."""

    metrics_ready = pyqtSignal(list)
    network_metrics_ready = pyqtSignal(float, float)
    error_occurred = pyqtSignal(str)

    def __init__(self, interval: float = 1.5) -> None:
        super().__init__()
        self._thread = QThread()
        self._worker = MonitorWorker(interval)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.metrics_ready.connect(self.metrics_ready)
        self._worker.network_metrics_ready.connect(self.network_metrics_ready)
        self._worker.error_occurred.connect(self.error_occurred)

    def start(self) -> None:
        """Запускает QThread."""
        self._thread.start()

    def stop(self) -> None:
        """Останавливает воркер и поток."""
        self._worker.stop()
        self._thread.quit()
        self._thread.wait()

    def force_poll(self) -> None:
        """Триггерит форс-опрос."""
        self._worker.force_poll()
