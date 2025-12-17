import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QSize
from components import Sidebar, TitleBar
from views import DeviceInfoView, DeviceControlsView, DeviceToolView, AutomationView, RemoteControlView, StabilityCheckView

from core.context import get_context

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ctx = get_context() # Access scalable context
        self.setWindowTitle("TestPilot")
        self.resize(1200, 800)
        
        # Frameless Window Setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        # self.setAttribute(Qt.WA_TranslucentBackground) # Removed as it causes rendering issues on some systems

        # Central Widget & Main Layout
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        central_widget.setStyleSheet("background-color: #121212;") # Force solid background
        self.setCentralWidget(central_widget)
        
        # Main Layout (Vertical: TitleBar + ContentBody)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Custom Title Bar
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        # 2. Content Body (Horizontal: Sidebar + PageArea)
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        body_layout.addWidget(self.sidebar)

        # Stacked Pages
        self.pages = QStackedWidget()
        self.pages.addWidget(DeviceInfoView())       # Index 0
        self.pages.addWidget(DeviceControlsView())   # Index 1
        self.pages.addWidget(RemoteControlView())    # Index 2
        self.pages.addWidget(DeviceToolView())       # Index 3
        self.pages.addWidget(AutomationView())       # Index 4
        self.pages.addWidget(StabilityCheckView())   # Index 5
        
        body_layout.addWidget(self.pages)
        main_layout.addWidget(body_widget)

        # Toast System
        from components.toast import Toast
        self.toast = Toast(self)
        
        # Connect Signals
        self.sidebar.page_selected.connect(self.pages.setCurrentIndex)
        
        device_manager = self.ctx.get_service("device_manager")
        device_manager.notification.connect(self.toast.show_message)
        
        # Load Stylesheet
        self._load_stylesheet()

    def _load_stylesheet(self):
        try:
            with open("styles/main.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Warning: styles/main.qss not found!")
