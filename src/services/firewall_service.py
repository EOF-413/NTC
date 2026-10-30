"""Firewall service."""


class FirewallService:
    """Applies blacklist rules at the platform layer."""

    def __init__(self, blacklist_service):
        self.blacklist_service = blacklist_service

    def apply_rule(self, rule):
        return {"status": "applied", "rule": rule}

    def remove_rule(self, rule):
        return {"status": "removed", "rule": rule}
