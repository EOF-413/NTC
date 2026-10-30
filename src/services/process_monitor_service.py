"""Process monitor service."""


class ProcessMonitorService:
    """Collects network and process metrics from the system."""

    def __init__(self):
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def collect(self):
        return {
            "processes": [],
            "connections": [],
            "timestamp": None,
        }
