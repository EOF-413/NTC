"""Blacklist service."""


class BlacklistService:
    """Controls blacklist rules and validation."""

    def __init__(self, persistence_service):
        self.persistence_service = persistence_service
        self.rules = []

    def load_rules(self):
        self.rules = self.persistence_service.load_blacklist_rules()
        return self.rules

    def save_rules(self):
        return self.persistence_service.save_blacklist_rules(self.rules)

    def add_rule(self, rule_type, value):
        rule = {"id": len(self.rules) + 1, "type": rule_type, "value": value, "enabled": True}
        self.rules.append(rule)
        return rule

    def remove_rule(self, rule_id):
        self.rules = [rule for rule in self.rules if rule.get("id") != rule_id]
        return True

    def list_rules(self):
        return self.rules
