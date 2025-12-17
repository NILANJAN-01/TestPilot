from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                                QFrame, QGridLayout, QMessageBox, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from .base_view import BaseView
from core.context import get_context
from utils import get_icon

class RemoteControlView(BaseView):
    """
    User interface for interactive device mirroring.
    Integrates with RemoteControlService to launch scrcpy with optimized AAOS settings.
    Handles dynamic state transitions (Mirroring vs Idle).
    """
    def __init__(self):
        super().__init__("Remote Control")
        self.ctx = get_context()
        self.device_manager = self.ctx.get_service("device_manager")
        self.remote_svc = self.ctx.get_service("remote_control")
        
        self.is_active = False
        self._build_ui()
        
        # Connect Service Signals
        self.remote_svc.error_occurred.connect(lambda msg: self.device_manager.notification.emit(msg, "error"))
        self.remote_svc.status_updated.connect(lambda msg: self.device_manager.notification.emit(msg, "info"))
        self.remote_svc.session_started.connect(self._on_session_started)
        self.remote_svc.session_ended.connect(self._on_session_ended)

    def _build_ui(self):
        layout = self.content_layout
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Header Section
        header = QLabel("Device Mirroring & Remote Control")
        header.setStyleSheet("font-size: 26px; font-weight: bold; color: #40E0D0;")
        layout.addWidget(header)

        desc = QLabel("Experience high-performance, low-latency device control powered by scrcpy.\nMirror the display and control the interface with your mouse and keyboard.")
        desc.setStyleSheet("color: #AAA; font-size: 14px; line-height: 1.5;")
        layout.addWidget(desc)

        # Main Action Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #1E1E1E;
                border: 1px solid #333;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)

        self.icon_lbl = QLabel()
        self.icon_lbl.setPixmap(get_icon("fa5s.desktop", color="#40E0D0").pixmap(64, 64))
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.icon_lbl)

        self.btn_action = QPushButton(" Launch Remote Session")
        self.btn_action.setIcon(get_icon("fa5s.play", color="#121212"))
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #40E0D0;
                color: #121212;
                font-weight: bold;
                font-size: 18px;
                padding: 20px;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #45F5E2; }
            QPushButton:pressed { background-color: #38C8B8; }
        """)
        self.btn_action.clicked.connect(self._on_action_clicked)
        card_layout.addWidget(self.btn_action)

        layout.addWidget(card)

        # Settings Grid
        settings_grid = QGridLayout()
        settings_grid.setSpacing(15)
        
        self._add_setting(settings_grid, "Screen Always On", "fa5s.eye", 0, self._toggle_stay_awake)
        self._add_setting(settings_grid, "Toggle Power", "fa5s.power-off", 1, self._toggle_power)
        
        layout.addLayout(settings_grid)
        layout.addStretch()

    def _add_setting(self, grid, text, icon, col, callback):
        btn = QPushButton(f" {text}")
        btn.setIcon(get_icon(icon, color="#BBB"))
        btn.setStyleSheet("""
            QPushButton {
                background: #252525;
                color: #DDD;
                border: 1px solid #333;
                padding: 12px;
                border-radius: 6px;
                text-align: left;
            }
            QPushButton:hover { border-color: #40E0D0; color: white; }
        """)
        btn.clicked.connect(callback)
        grid.addWidget(btn, 0, col)

    def _on_action_clicked(self):
        if self.is_active:
            self.remote_svc.stop_mirroring()
            self._on_session_ended() # Visual update fallback
        else:
            self._start_remote()

    def _start_remote(self):
        serial = self.device_manager.get_first_device()
        if not serial:
            self.device_manager.notification.emit("No device connected!", "error")
            return
        
        self.remote_svc.start_mirroring(serial)

    def _on_session_started(self):
        self.is_active = True
        self.btn_action.setText(" Stop Remote Session")
        self.btn_action.setIcon(get_icon("fa5s.stop", color="#FFFFFF"))
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-weight: bold;
                font-size: 18px;
                padding: 20px;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        self.icon_lbl.setPixmap(get_icon("fa5s.desktop", color="#E74C3C").pixmap(64, 64))

    def _on_session_ended(self):
        self.is_active = False
        self.btn_action.setText(" Launch Remote Session")
        self.btn_action.setIcon(get_icon("fa5s.play", color="#121212"))
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #40E0D0;
                color: #121212;
                font-weight: bold;
                font-size: 18px;
                padding: 20px;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #45F5E2; }
        """)
        self.icon_lbl.setPixmap(get_icon("fa5s.desktop", color="#40E0D0").pixmap(64, 64))

    def _toggle_stay_awake(self):
        serial = self.device_manager.get_first_device()
        if serial:
            self.device_manager.adb.shell(serial, "svc power stayon true")
            self.device_manager.notification.emit("Stay Awake: Always On", "info")

    def _toggle_power(self):
        serial = self.device_manager.get_first_device()
        if serial:
            self.device_manager.adb.shell(serial, "input keyevent 26")
            self.device_manager.notification.emit("Power Key Pressed", "info")

from PySide6.QtCore import Qt
