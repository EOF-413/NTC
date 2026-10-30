"""Notification service."""


class NotificationService:
    """Sends user notifications about blocked traffic."""

    def __init__(self):
        self.enabled = True

    def send(self, message):
        return {"status": "sent", "message": message}
