"""Domain models for the NTC application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class ProcessRecord:
    pid: int
    name: str
    executable_path: Optional[str] = None
    state: str = "active"
    connections: List["NetworkConnectionRecord"] = field(default_factory=list)


@dataclass
class NetworkConnectionRecord:
    local_address: str
    local_port: int
    remote_address: str
    remote_port: int
    protocol: str
    status: str
    bytes_sent: int = 0
    bytes_received: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BlacklistRule:
    rule_id: Optional[int] = None
    rule_type: str = "process"
    rule_value: str = ""
    enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class TrafficStat:
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    active_connections: int = 0
    process_name: Optional[str] = None
    speed_bytes_per_sec: float = 0.0


@dataclass
class IncidentLog:
    timestamp: datetime = field(default_factory=datetime.utcnow)
    process_name: str = ""
    pid: int = 0
    target_ip: str = ""
    target_port: int = 0
    rule_type: str = ""
    action: str = "blocked"
