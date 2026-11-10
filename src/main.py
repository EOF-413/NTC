# src/main.py
"""Точка входа Network Traffic Controller."""
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from ntc.controllers.main_controller import MainController
from ntc.utils.logger import setup_logger
from ntc.windows.main_window import MainWindow

logger = setup_logger("main")


def main() -> int:
    """Запускает приложение. Возвращает код выхода."""
    base_dir = Path(__file__).resolve().parent  # src/
    app = QApplication(sys.argv)
    app.setApplicationName("NTC")
    app.setOrganizationName("NTC")
    app.setQuitOnLastWindowClosed(False)  # живём в трее

    app_css = base_dir / "ntc" / "styles" / "css" / "app.css"
    if app_css.exists():
        with open(app_css, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    MainController(window, base_dir)  # controller — QObject-child окна
    window.show()

    logger.info("NTC запущен. База: %s", base_dir / "ntc.db")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
