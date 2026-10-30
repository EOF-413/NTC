"""Notification manager for OS-level notifications."""


class NotificationManager:
    """Handles OS notifications and toast-like messages."""

    def __init__(self):
        self.enabled = True

    def notify(self, title, message):
        return {"title": title, "message": message, "status": "queued"}
