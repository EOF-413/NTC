"""Main application bootstrap and lifecycle management."""

from controllers.app_controller import AppController
from infrastructure.database import Database
from services.blacklist_service import BlacklistService
from services.firewall_service import FirewallService
from services.notification_service import NotificationService
from services.persistence_service import PersistenceService
from services.process_monitor_service import ProcessMonitorService
from services.traffic_analyzer_service import TrafficAnalyzerService
from ui.main_window import MainWindow


class Application:
    """Coordinates core services and the user interface."""

    def __init__(self):
        self.database = Database("ntc.db")
        self.persistence_service = PersistenceService(self.database)
        self.blacklist_service = BlacklistService(self.persistence_service)
        self.firewall_service = FirewallService(self.blacklist_service)
        self.notification_service = NotificationService()
        self.process_monitor_service = ProcessMonitorService()
        self.traffic_analyzer_service = TrafficAnalyzerService()
        self.main_window = MainWindow()
        self.controller = AppController(
            ui=self.main_window,
            blacklist_service=self.blacklist_service,
            firewall_service=self.firewall_service,
            notification_service=self.notification_service,
            monitoring_service=self.process_monitor_service,
            traffic_service=self.traffic_analyzer_service,
            persistence_service=self.persistence_service,
        )

    def run(self):
        """Start the application lifecycle."""
        self.controller.start()
        self.main_window.show()

    def stop(self):
        """Stop monitors and close resources."""
        self.controller.stop()
        self.main_window.close()
