# src/ntc/controllers/blacklist_controller.py
"""Контроллер диалога чёрного списка."""
from PyQt6.QtWidgets import QWidget

from ntc.services.blocker_service import BlockerService
from ntc.services.database_service import DatabaseService


class BlacklistController:
    """Связывает диалог чёрного списка и сервисы."""

    def __init__(
        self, db: DatabaseService, blocker: BlockerService, parent: QWidget
    ) -> None:
        self._db = db
        self._blocker = blocker
        self._parent = parent

    def open(self) -> None:
        """Открывает диалог и перезагружает правила блокировки."""
        from ntc.dialogs.blacklist_dialog import BlacklistDialog

        dlg = BlacklistDialog(self._db, self._parent)
        dlg.exec()
        self._blocker.reload_rules()
