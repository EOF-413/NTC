# src/ntc/services/database_service.py
"""SQLite-слой для чёрного списка и инцидентов."""
import sqlite3
from pathlib import Path

from ntc.models.blacklist_entry import BlacklistEntry
from ntc.models.incident import Incident
from ntc.utils.logger import setup_logger

logger = setup_logger("db")


class DatabaseService:
    """Репозиторий для таблиц blacklist и incidents."""

    def __init__(self, db_path: Path) -> None:
        """Открывает/создаёт БД и инициализирует схему.

        Args:
            db_path: путь к файлу БД.
        """
        self._path = db_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process TEXT NOT NULL,
                    pid INTEGER NOT NULL,
                    remote_ip TEXT NOT NULL,
                    remote_port INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    ts TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def list_blacklist(self) -> list[BlacklistEntry]:
        """Возвращает все записи чёрного списка (новые сверху)."""
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM blacklist ORDER BY id DESC").fetchall()
        return [
            BlacklistEntry(
                id=r["id"], type=r["type"], value=r["value"],
                enabled=bool(r["enabled"]), created_at=r["created_at"],
            )
            for r in rows
        ]

    def add_blacklist(self, entry: BlacklistEntry) -> int:
        """Добавляет запись и возвращает её id."""
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO blacklist(type, value, enabled, created_at) VALUES (?,?,?,?)",
                (entry.type, entry.value, int(entry.enabled), entry.created_at),
            )
            conn.commit()
            return int(cur.lastrowid or 0)

    def update_blacklist(self, entry: BlacklistEntry) -> None:
        """Обновляет запись по id."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE blacklist SET type=?, value=?, enabled=? WHERE id=?",
                (entry.type, entry.value, int(entry.enabled), entry.id),
            )
            conn.commit()

    def delete_blacklist(self, entry_id: int) -> None:
        """Удаляет запись по id."""
        with self._conn() as conn:
            conn.execute("DELETE FROM blacklist WHERE id=?", (entry_id,))
            conn.commit()

    def list_incidents(self, limit: int = 100) -> list[Incident]:
        """Возвращает последние инциденты."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM incidents ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [
            Incident(
                id=r["id"], process=r["process"], pid=r["pid"],
                remote_ip=r["remote_ip"], remote_port=r["remote_port"],
                action=r["action"], ts=r["ts"],
            )
            for r in rows
        ]

    def add_incident(self, incident: Incident) -> int:
        """Сохраняет инцидент."""
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO incidents(process, pid, remote_ip, remote_port, action, ts) "
                "VALUES (?,?,?,?,?,?)",
                (
                    incident.process, incident.pid, incident.remote_ip,
                    incident.remote_port, incident.action, incident.ts,
                ),
            )
            conn.commit()
            return int(cur.lastrowid or 0)
