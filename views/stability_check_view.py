from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QListWidget, QListWidgetItem, QSpinBox, 
                                QTextEdit, QFrame, QScrollArea, QSplitter)
from PySide6.QtCore import Qt
from .base_view import BaseView
from core.context import get_context
from utils import get_icon

class StabilityCheckView(BaseView):
    def __init__(self):
        super().__init__("System Stability Check")
        self.ctx = get_context()
        self.device_manager = self.ctx.get_service("device_manager")
        self.stability_svc = self.ctx.get_service("stability")
        
        self.is_active = False
        self._build_ui()
        self._connect_signals()

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_apps()

    def _build_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QLabel("System Stability Check")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #40E0D0;")
        layout.addWidget(header)

        desc = QLabel("Ensure system reliability by launching applications in a stress loop while monitoring for ANRs and Crashes.")
        desc.setStyleSheet("color: #AAA; font-size: 13px;")
        layout.addWidget(desc)

        # Main Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # --- Left Panel: App Selection & Launch Config ---
        left_panel = QFrame()
        left_panel.setStyleSheet("background: #1A1A1A; border-radius: 10px; border: 1px solid #333;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)

        app_lbl = QLabel("Select Applications to Loop:")
        app_lbl.setStyleSheet("color: #EEE; font-weight: bold; border: none;")
        left_layout.addWidget(app_lbl)

        self.app_list = QListWidget()
        self.app_list.setStyleSheet("""
            QListWidget { background: #111; border: 1px solid #444; border-radius: 4px; color: #DDD; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #222; }
            QListWidget::item:selected { background: #40E0D033; color: #40E0D0; }
        """)
        left_layout.addWidget(self.app_list)

        btn_refresh = QPushButton(" Refresh App List")
        btn_refresh.setIcon(get_icon("fa5s.sync", "#EEE"))
        btn_refresh.setStyleSheet("background: #333; color: white; padding: 8px; border: none; border-radius: 4px;")
        btn_refresh.clicked.connect(self._refresh_apps)
        left_layout.addWidget(btn_refresh)

        # Loop Config
        config_row = QHBoxLayout()
        config_row.addWidget(QLabel("Loop Count:"))
        self.loop_count = QSpinBox()
        self.loop_count.setRange(1, 1000)
        self.loop_count.setValue(5)
        self.loop_count.setStyleSheet("background: #222; color: white; padding: 5px; border: 1px solid #444;")
        config_row.addWidget(self.loop_count)
        left_layout.addLayout(config_row)

        self.btn_run = QPushButton(" Start Stability Run")
        self.btn_run.setIcon(get_icon("fa5s.play", "#121212"))
        self.btn_run.setStyleSheet("""
            QPushButton { 
                background: #40E0D0; color: #121212; font-weight: bold; padding: 15px; border-radius: 6px; 
            }
            QPushButton:hover { background: #45F5E2; }
        """)
        self.btn_run.clicked.connect(self._toggle_test)
        left_layout.addWidget(self.btn_run)

        splitter.addWidget(left_panel)

        # --- Right Panel: Logs & Monitoring ---
        right_panel = QFrame()
        right_panel.setStyleSheet("background: #1A1A1A; border-radius: 10px; border: 1px solid #333;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)

        log_lbl = QLabel("Live Execution Monitoring:")
        log_lbl.setStyleSheet("color: #EEE; font-weight: bold; border: none;")
        right_layout.addWidget(log_lbl)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background: #000; color: #00FF00; font-family: 'Consolas'; font-size: 12px; border: 1px solid #333;")
        right_layout.addWidget(self.log_output)

        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter)

        self.content_layout.addWidget(container)

    def _connect_signals(self):
        self.stability_svc.status_updated.connect(self._add_log)
        self.stability_svc.issue_detected.connect(self._on_issue_detected)
        self.stability_svc.finished.connect(self._on_finished)

    def _refresh_apps(self):
        serial = self.device_manager.get_first_device()
        if not serial:
            self._add_log("No device connected. Cannot refresh apps.")
            return

        self.app_list.clear()
        apps = self.stability_svc.get_apps(serial)
        for app in apps:
            item = QListWidgetItem(app)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.app_list.addItem(item)
        
        self._add_log(f"Found {len(apps)} launchable activities.")

    def _toggle_test(self):
        if self.stability_svc.is_running:
            self.stability_svc.stop_test()
            return

        serial = self.device_manager.get_first_device()
        if not serial:
            self._add_log("[ERROR] No device selected.")
            return

        selected_apps = []
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_apps.append(item.text())

        if not selected_apps:
            self._add_log("[ERROR] Select at least one app to test.")
            return

        loops = self.loop_count.value()
        self.log_output.clear()
        self.btn_run.setText(" Stop Stability Run")
        self.btn_run.setStyleSheet("background: #E74C3C; color: white; font-weight: bold; padding: 15px; border-radius: 6px;")
        
        self.stability_svc.start_test(serial, selected_apps, loops)

    def _add_log(self, msg):
        self.log_output.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _on_issue_detected(self, crash_type, details):
        self._add_log(f"!!! {crash_type} DETECTED !!!")
        self._add_log(details)
        # Scroll to bottom
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def _on_finished(self):
        self.btn_run.setText(" Start Stability Run")
        self.btn_run.setStyleSheet("background: #40E0D0; color: #121212; font-weight: bold; padding: 15px; border-radius: 6px;")

import time
