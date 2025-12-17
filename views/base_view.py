from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt

class BaseView(QWidget):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("ContentArea")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QLabel(title)
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        layout.addSpacing(20)
        
        # Content Container
        self.content_area = QFrame()
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.content_area)
        
        self.content_layout = QVBoxLayout(self.content_area)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)
