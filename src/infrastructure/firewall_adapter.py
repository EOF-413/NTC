"""Firewall adapter abstraction."""


class FirewallAdapter:
    """Platform-specific firewall implementation entry point."""

    def __init__(self, platform):
        self.platform = platform

    def apply(self, rule):
        return {"platform": self.platform, "result": "queued"}
