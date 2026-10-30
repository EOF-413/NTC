"""SQLite storage helper for NTC."""

import sqlite3


class Database:
    """Basic sqlite3 wrapper for settings and rules."""

    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self._initialize()

    def _initialize(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS blacklist_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_type TEXT NOT NULL,
                rule_value TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        self.connection.commit()

    def save_rules(self, rules):
        self.connection.execute("DELETE FROM blacklist_rules")
        for rule in rules:
            self.connection.execute(
                "INSERT INTO blacklist_rules(rule_type, rule_value, enabled) VALUES (?, ?, ?)",
                (rule.get("type"), rule.get("value"), int(rule.get("enabled", True))),
            )
        self.connection.commit()
        return True
