"""Абстракция блокировки трафика (pydivert / netsh / iptables)."""
import importlib
import ipaddress
import subprocess
import sys
import time
from pathlib import PureWindowsPath

import psutil
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ntc.services.database_service import DatabaseService
from ntc.utils.admin_check import is_admin
from ntc.utils.logger import setup_logger

logger = setup_logger("blocker")

_NETSH_GROUP = "NTC-NetworkTrafficController"
_IPTABLES_CHAIN = "NTC_OUTPUT"


class _PydivertWorker(QObject):
    """Перехват пакетов через pydivert (Windows)."""

    blocked = pyqtSignal(str, str, int, int)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, db: DatabaseService) -> None:
        super().__init__()
        self._db = db
        self._running = True
        self._handle = None

    def stop(self) -> None:
        """Останавливает цикл и разблокирует чтение пакетов."""
        self._running = False
        if self._handle is not None:
            try:
                self._handle.close()
            except Exception as exc:
                logger.warning("Не удалось закрыть WinDivert: %s", exc)

    def run(self) -> None:
        """Основной цикл pydivert."""
        try:
            self._run()
        finally:
            self.finished.emit()

    def _run(self) -> None:
        try:
            import pydivert  # type: ignore
        except ImportError as exc:
            logger.error("pydivert недоступен: %s", exc)
            self.error_occurred.emit("pydivert недоступен — блокировка отключена")
            return

        try:
            entries = self._db.list_blacklist()
            proc_rules = {
                PureWindowsPath(e.value).name.casefold()
                for e in entries if e.type == "process" and e.enabled
            }
            ip_rules = [
                ipaddress.ip_network(e.value, strict=False)
                for e in entries if e.type == "ip" and e.enabled
            ]
        except (OSError, ValueError) as exc:
            logger.exception("Не удалось загрузить правила блокировки: %s", exc)
            self.error_occurred.emit(str(exc))
            return
        except Exception as exc:
            logger.exception("Не удалось прочитать правила: %s", exc)
            self.error_occurred.emit(str(exc))
            return

        endpoint_owners: dict[tuple[str, int], tuple[int, str]] = {}
        refresh_at = 0.0
        try:
            handle = pydivert.WinDivert("tcp.DstPort != 0 or udp.DstPort != 0")
            self._handle = handle
            with handle as divert:
                while self._running:
                    now = time.monotonic()
                    if now >= refresh_at:
                        endpoint_owners = self._read_endpoint_owners()
                        refresh_at = now + 1.0

                    try:
                        packet = divert.recv()
                    except Exception as exc:
                        if self._running:
                            logger.exception("Ошибка получения пакета: %s", exc)
                            self.error_occurred.emit(str(exc))
                        break

                    src_endpoint = (packet.src_addr, int(packet.src_port))
                    dst_endpoint = (packet.dst_addr, int(packet.dst_port))
                    source_owner = endpoint_owners.get(src_endpoint)
                    destination_owner = endpoint_owners.get(dst_endpoint)
                    if source_owner is None and destination_owner is None and proc_rules:
                        endpoint_owners = self._read_endpoint_owners()
                        source_owner = endpoint_owners.get(src_endpoint)
                        destination_owner = endpoint_owners.get(dst_endpoint)
                    owner = source_owner or destination_owner
                    if source_owner is not None:
                        remote_ip, remote_port = packet.dst_addr, int(packet.dst_port)
                    else:
                        remote_ip, remote_port = packet.src_addr, int(packet.src_port)

                    process = owner[1] if owner is not None else "?"
                    process_blocked = process.casefold() in proc_rules
                    try:
                        remote_address = ipaddress.ip_address(remote_ip)
                        ip_blocked = any(
                            remote_address.version == network.version
                            and remote_address in network
                            for network in ip_rules
                        )
                    except ValueError:
                        ip_blocked = False
                    if owner is None:
                        for address in (packet.src_addr, packet.dst_addr):
                            try:
                                parsed = ipaddress.ip_address(address)
                            except ValueError:
                                continue
                            if any(
                                parsed.version == network.version and parsed in network
                                for network in ip_rules
                            ):
                                ip_blocked = True
                                remote_ip = address
                                remote_port = (
                                    int(packet.src_port)
                                    if address == packet.src_addr
                                    else int(packet.dst_port)
                                )
                                break

                    if process_blocked or ip_blocked:
                        self.blocked.emit(
                            process, remote_ip, remote_port, owner[0] if owner else 0
                        )
                        continue

                    try:
                        divert.send(packet)
                    except Exception as exc:
                        logger.exception("Ошибка отправки пакета: %s", exc)
                        self.error_occurred.emit(str(exc))
                        break
        except Exception as exc:
            if self._running:
                logger.exception("Ошибка pydivert: %s", exc)
                self.error_occurred.emit(str(exc))
        finally:
            self._handle = None

    @staticmethod
    def _read_endpoint_owners() -> dict[tuple[str, int], tuple[int, str]]:
        owners: dict[tuple[str, int], tuple[int, str]] = {}
        try:
            connections = psutil.net_connections(kind="inet")
        except (psutil.AccessDenied, OSError) as exc:
            logger.warning("Не удалось сопоставить соединения процессам: %s", exc)
            return owners

        for connection in connections:
            if connection.pid is None or not connection.laddr:
                continue
            try:
                local_address = connection.laddr
                if hasattr(local_address, "ip"):
                    ip, port = local_address.ip, local_address.port
                else:
                    ip, port = local_address[0], local_address[1]
                name = psutil.Process(connection.pid).name()
                owners[(str(ip), int(port))] = (connection.pid, name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
                continue
        return owners


class BlockerService(QObject):
    """Абстракция блокировки трафика."""

    connection_blocked = pyqtSignal(str, str, int, int)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(bool)

    def __init__(self, db: DatabaseService) -> None:
        super().__init__()
        self._db = db
        self._thread: QThread | None = None
        self._worker: _PydivertWorker | None = None
        self._active = False
        self._linux_chain_created = False
        self._using_netsh = False

    @property
    def is_active(self) -> bool:
        """Активна ли блокировка."""
        return self._active

    def can_block(self) -> bool:
        """Есть ли права и поддержка платформы."""
        return is_admin() and sys.platform in ("win32", "linux")

    def start(self) -> bool:
        """Запускает механизм блокировки."""
        if self._active:
            return True
        if not self.can_block():
            logger.warning("Нет прав/платформа не поддерживает блокировку")
            return False
        if self._thread is not None:
            self._thread.wait()
            self._thread = None
            self._worker = None
        if sys.platform == "win32":
            return self._start_windows()
        return self._start_linux()

    def _start_windows(self) -> bool:
        try:
            importlib.import_module("pydivert")
        except ImportError:
            logger.warning("pydivert недоступен → netsh-fallback")
            return self._start_netsh_fallback()

        self._worker = _PydivertWorker(self._db)
        self._thread = QThread(self)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.blocked.connect(self.connection_blocked)
        self._worker.error_occurred.connect(self.error_occurred)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._on_worker_finished)
        self._thread.start()
        self._active = True
        self.status_changed.emit(True)
        return True

    def _start_netsh_fallback(self) -> bool:
        rules = self._db.list_blacklist()
        self._using_netsh = False
        try:
            subprocess.run(
                [
                    "netsh", "advfirewall", "firewall", "delete", "rule",
                    "name=all", f"group={_NETSH_GROUP}",
                ],
                check=False, capture_output=True, text=True,
            )
            for rule in rules:
                if not rule.enabled or rule.type != "ip":
                    continue
                result = subprocess.run(
                    [
                        "netsh", "advfirewall", "firewall", "add", "rule",
                        f"name=NTC_{rule.id}", f"group={_NETSH_GROUP}",
                        "dir=out", "action=block", f"remoteip={rule.value}",
                    ],
                    check=False, capture_output=True, text=True,
                )
                if result.returncode:
                    raise RuntimeError(result.stderr or result.stdout)
                self._using_netsh = True
        except (OSError, RuntimeError) as exc:
            logger.exception("Не удалось применить правила netsh: %s", exc)
            self.error_occurred.emit(f"Не удалось применить правила netsh: {exc}")
            self._delete_netsh_rules(report_error=False)
            self._using_netsh = False
            return False

        if any(rule.enabled and rule.type == "process" for rule in rules):
            self.error_occurred.emit(
                "Блокировка процессов недоступна без pydivert; применяются только IP-правила"
            )
        self._active = True
        self.status_changed.emit(True)
        return True

    def _start_linux(self) -> bool:
        rules = self._db.list_blacklist()
        try:
            created = subprocess.run(
                ["iptables", "-N", _IPTABLES_CHAIN],
                check=False, capture_output=True, text=True,
            )
            if created.returncode:
                exists = subprocess.run(
                    ["iptables", "-S", _IPTABLES_CHAIN],
                    check=False, capture_output=True, text=True,
                )
                if exists.returncode:
                    raise RuntimeError(created.stderr or exists.stderr)
            self._linux_chain_created = True
            self._run_iptables(["-F", _IPTABLES_CHAIN])

            jump = ["-C", "OUTPUT", "-j", _IPTABLES_CHAIN]
            if subprocess.run(
                ["iptables", *jump], check=False, capture_output=True
            ).returncode:
                self._run_iptables(["-I", "OUTPUT", "1", "-j", _IPTABLES_CHAIN])

            for rule in rules:
                if rule.enabled and rule.type == "ip":
                    self._run_iptables(
                        ["-A", _IPTABLES_CHAIN, "-d", rule.value, "-j", "DROP"]
                    )
        except (OSError, RuntimeError) as exc:
            logger.exception("Не удалось применить правила iptables: %s", exc)
            self.error_occurred.emit(f"Не удалось применить правила iptables: {exc}")
            try:
                self._delete_linux_rules()
            except (OSError, RuntimeError) as cleanup_exc:
                logger.exception("Не удалось откатить правила iptables: %s", cleanup_exc)
                self.error_occurred.emit(
                    f"Не удалось откатить правила iptables: {cleanup_exc}"
                )
            return False

        if any(rule.enabled and rule.type == "process" for rule in rules):
            self.error_occurred.emit(
                "Блокировка процессов пока не поддерживается через iptables"
            )
        self._active = True
        self.status_changed.emit(True)
        return True

    @staticmethod
    def _run_iptables(arguments: list[str]) -> None:
        result = subprocess.run(
            ["iptables", *arguments], check=False, capture_output=True, text=True
        )
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)

    def _delete_netsh_rules(self, *, report_error: bool = True) -> None:
        try:
            result = subprocess.run(
                [
                    "netsh", "advfirewall", "firewall", "delete", "rule",
                    "name=all", f"group={_NETSH_GROUP}",
                ],
                check=False, capture_output=True, text=True,
            )
        except OSError as exc:
            logger.error("Не удалось удалить правила netsh: %s", exc)
            if report_error:
                self.error_occurred.emit(f"Не удалось удалить правила netsh: {exc}")
            return
        if result.returncode:
            message = result.stderr or result.stdout
            logger.error("Не удалось удалить правила netsh: %s", message)
            if report_error:
                self.error_occurred.emit(f"Не удалось удалить правила netsh: {message}")

    def _delete_linux_rules(self) -> None:
        if not self._linux_chain_created:
            return
        jump = ["-D", "OUTPUT", "-j", _IPTABLES_CHAIN]
        while subprocess.run(
            ["iptables", *jump], check=False, capture_output=True
        ).returncode == 0:
            pass
        self._run_iptables(["-F", _IPTABLES_CHAIN])
        self._run_iptables(["-X", _IPTABLES_CHAIN])
        self._linux_chain_created = False

    def _on_worker_finished(self) -> None:
        self._active = False
        self.status_changed.emit(False)

    def stop(self) -> None:
        """Останавливает блокировку и удаляет принадлежащие ей правила."""
        if self._worker is not None:
            self._worker.stop()
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
            self._worker = None
        if self._using_netsh:
            self._delete_netsh_rules()
            self._using_netsh = False
        elif sys.platform == "linux":
            try:
                self._delete_linux_rules()
            except (OSError, RuntimeError) as exc:
                logger.exception("Не удалось очистить правила iptables: %s", exc)
                self.error_occurred.emit(f"Не удалось очистить правила iptables: {exc}")
        self._active = False
        self.status_changed.emit(False)

    def reload_rules(self) -> None:
        """Перезапускает блокировку с актуальными правилами."""
        if self._active:
            self.stop()
            self.start()
