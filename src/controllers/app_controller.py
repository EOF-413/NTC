"""Main application controller."""


class AppController:
    """Initializes services, delegates work to feature controllers and UI."""

    def __init__(
        self,
        ui,
        blacklist_service,
        firewall_service,
        notification_service,
        monitoring_service,
        traffic_service,
        persistence_service,
    ):
        self.ui = ui
        self.blacklist_service = blacklist_service
        self.firewall_service = firewall_service
        self.notification_service = notification_service
        self.monitoring_service = monitoring_service
        self.traffic_service = traffic_service
        self.persistence_service = persistence_service

    def start(self):
        """Initialize application state."""
        self.persistence_service.load_settings()
        self.blacklist_service.load_rules()
        self.ui.bind_actions(self)

    def stop(self):
        """Stop monitoring and persist final state."""
        self.persistence_service.save_settings()
        self.blacklist_service.save_rules()

    def refresh_data(self):
        """Trigger a refresh cycle."""
        data = self.monitoring_service.collect()
        self.ui.update_dashboard(data)
