"""Firewall controller."""


class FirewallController:
    """Encapsulates platform-specific firewall actions."""

    def __init__(self, service):
        self.service = service

    def apply_rule(self, rule):
        return self.service.apply_rule(rule)

    def remove_rule(self, rule):
        return self.service.remove_rule(rule)
