"""Main UI window stub."""


class MainWindow:
    """Entry point of the presentation layer."""

    def __init__(self):
        self.title = "NTC - Network Traffic Controller"

    def bind_actions(self, controller):
        self.controller = controller

    def update_dashboard(self, data):
        self.data = data

    def show(self):
        return True

    def close(self):
        return True
