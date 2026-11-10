# src/ntc/ui/ui_main_window.py
"""Ui_MainWindow — собирается pyuic6 из main_window.ui."""
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QPushButton, QStatusBar,
    QTableView, QVBoxLayout, QWidget,
)

from ntc.widgets.traffic_chart import TrafficChart


class Ui_MainWindow:
    """Автосгенерированный интерфейс главного окна."""

    def setupUi(self, main_window: QMainWindow) -> None:
        main_window.setObjectName("MainWindow")
        main_window.resize(1100, 720)

        self.centralwidget = QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.root_layout = QVBoxLayout(self.centralwidget)
        self.root_layout.setContentsMargins(12, 12, 12, 12)
        self.root_layout.setSpacing(10)

        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setSpacing(8)

        self.btn_refresh = QPushButton("Обновить", self.centralwidget)
        self.btn_refresh.setObjectName("btn_refresh")
        self.btn_clear = QPushButton("Очистить", self.centralwidget)
        self.btn_clear.setObjectName("btn_clear")
        self.btn_blacklist = QPushButton("Чёрный список", self.centralwidget)
        self.btn_blacklist.setObjectName("btn_blacklist")
        self.btn_settings = QPushButton("Настройки", self.centralwidget)
        self.btn_settings.setObjectName("btn_settings")
        self.lbl_privilege = QLabel("🔒 Мониторинг", self.centralwidget)
        self.lbl_privilege.setObjectName("lbl_privilege")

        self.toolbar_layout.addWidget(self.btn_refresh)
        self.toolbar_layout.addWidget(self.btn_clear)
        self.toolbar_layout.addWidget(self.btn_blacklist)
        self.toolbar_layout.addWidget(self.btn_settings)
        self.toolbar_layout.addStretch()
        self.toolbar_layout.addWidget(self.lbl_privilege)
        self.root_layout.addLayout(self.toolbar_layout)

        self.traffic_chart = TrafficChart(self.centralwidget)
        self.traffic_chart.setObjectName("traffic_chart")
        self.root_layout.addWidget(self.traffic_chart)

        self.table_view = QTableView(self.centralwidget)
        self.table_view.setObjectName("table_view")
        self.table_view.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.table_view.setAlternatingRowColors(False)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.root_layout.addWidget(self.table_view, 1)

        main_window.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        self.lbl_total = QLabel("Сеть: 0 Б/с", main_window)
        self.lbl_total.setObjectName("lbl_total")
        self.statusbar.addPermanentWidget(self.lbl_total)
        main_window.setStatusBar(self.statusbar)

        self.retranslateUi(main_window)

    def retranslateUi(self, main_window: QMainWindow) -> None:  # noqa: N802
        main_window.setWindowTitle("Network Traffic Controller")
