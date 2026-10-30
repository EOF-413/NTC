"""Monitoring controller."""


class MonitoringController:
    """Coordinates collection and analysis of network data."""

    def __init__(self, monitor_service, traffic_service):
        self.monitor_service = monitor_service
        self.traffic_service = traffic_service

    def poll(self):
        snapshot = self.monitor_service.collect()
        return self.traffic_service.analyze(snapshot)
