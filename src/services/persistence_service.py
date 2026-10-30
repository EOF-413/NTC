"""Persistence service."""


class PersistenceService:
    """Persists application settings and blacklist state."""

    def __init__(self, database):
        self.database = database
        self.settings = {}

    def load_settings(self):
        self.settings = {"refresh_interval": 2, "notifications_enabled": True}
        return self.settings

    def save_settings(self):
        return True

    def load_blacklist_rules(self):
        return []

    def save_blacklist_rules(self, rules):
        self.database.save_rules(rules)
        return True
