# src/ntc/models/incident.py
"""Сущность инцидента блокировки."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Incident:
    """Зафиксированный инцидент блокировки."""

    id: int | None = None
    process: str = ""
    pid: int = 0
    remote_ip: str = ""
    remote_port: int = 0
    action: str = "blocked"
    ts: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
