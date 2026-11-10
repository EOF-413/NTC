# src/ntc/models/blacklist_entry.py
"""Сущность записи чёрного списка."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BlacklistEntry:
    """Запись чёрного списка (процесс или IP)."""

    id: int | None = None
    type: str = "process"  # "process" | "ip"
    value: str = ""
    enabled: bool = True
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
