# src/ntc/models/connection_info.py
"""Метрики подключения процесса."""
from dataclasses import dataclass


@dataclass
class ConnectionInfo:
    """Строка таблицы монитора: имя, pid, скорости, соединения, remote."""

    name: str
    pid: int
    sent: float | None
    recv: float | None
    connections: int
    remote: str
