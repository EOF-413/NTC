"""Traffic analyzer service."""


class TrafficAnalyzerService:
    """Transforms raw service data into dashboard metrics."""

    def __init__(self):
        self.history = []

    def analyze(self, snapshot):
        return {
            "total_connections": len(snapshot.get("connections", [])),
            "process_count": len(snapshot.get("processes", [])),
            "traffic": 0,
        }
