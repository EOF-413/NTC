"""Domain and policy helpers."""


class BlacklistPolicy:
    """Policy object that defines rule types and matching logic."""

    allowed_types = {"process", "ip", "domain"}

    @classmethod
    def validate_rule(cls, rule_type, value):
        if rule_type not in cls.allowed_types:
            raise ValueError(f"Unsupported rule type: {rule_type}")
        if not value or not str(value).strip():
            raise ValueError("Rule value cannot be empty")
        return True
