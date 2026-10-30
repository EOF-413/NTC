"""Blacklist controller."""


class BlacklistController:
    """CRUD operations for blacklist rules."""

    def __init__(self, service):
        self.service = service

    def add_rule(self, rule_type, value):
        return self.service.add_rule(rule_type=rule_type, value=value)

    def remove_rule(self, rule_id):
        return self.service.remove_rule(rule_id)

    def list_rules(self):
        return self.service.list_rules()
