from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
from utils import get_icon

class TitleBar(QWidget):
    """
    Custom frameless title bar.
    Provides window dragging, min/max/close controls, and global system status triggers.
    """
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setObjectName("TitleBar")
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Icon & Title
        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_icon("fa5s.car", color="#40E0D0").pixmap(24, 24)) 

        from core.config import APP_NAME, VERSION
        self.title_label = QLabel(f"{APP_NAME} {VERSION}")
        self.title_label.setObjectName("TitleLabel")

        # ADB Root Toggle
        self.btn_root = QPushButton(" ADB Root")
        self.btn_root.setCheckable(True)
        self.btn_root.setStyleSheet("QPushButton { background: #222; color: #BBB; border: 1px solid #444; padding: 2px 10px; font-size: 11px; border-radius: 4px; margin-right: 15px; } QPushButton:checked { background: #40E0D033; color: #40E0D0; border-color: #40E0D0; }")
        self.btn_root.toggled.connect(self._toggle_root)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.btn_root)

        # Window Controls
        self.btn_minimize = self._create_control_btn("fa5s.minus", self.parent_window.showMinimized)
        self.btn_maximize = self._create_control_btn("fa5s.window-maximize", self._toggle_maximize)
        self.btn_close = self._create_control_btn("fa5s.times", self.parent_window.close)
        self.btn_close.setObjectName("CloseBtn") # For red hover effect

        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize)
        layout.addWidget(self.btn_close)

    def _create_control_btn(self, icon_name, callback):
        btn = QPushButton()
        btn.setObjectName("WindowControlBtn")
        btn.setIcon(get_icon(icon_name, color="#AAAAAA"))
        btn.setFixedSize(30, 30)
        btn.clicked.connect(callback)
        return btn

    def _toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

    def _toggle_root(self, checked):
        from core.context import get_context
        ctx = get_context()
        dm = ctx.get_service("device_manager")
        adb = dm.adb
        serial = dm.get_first_device()
        
        if not serial:
            dm.notification.emit("Please connect a device before trying to enable root.", "warn")
            self.btn_root.setChecked(False)
            return

        if checked:
            out, err, code = adb.enable_root(serial)
            if "adbd is already running as root" in out or "restarting adbd as root" in out:
                dm.notification.emit(f"Root enabled on {serial}", "info")
            else:
                dm.notification.emit(f"Root Failed: {out} {err}", "error")
                self.btn_root.setChecked(False)

    # Enable window dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent_window.window().windowHandle().startSystemMove()

