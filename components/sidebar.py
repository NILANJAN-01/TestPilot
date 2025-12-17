from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, QSize
import qtawesome as qta
from utils import get_icon

class Sidebar(QWidget):
    # Signal emiting the index of the selected page
    page_selected = Signal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(5)

        # Navigation Buttons
        self.btn_info = self._create_btn("Device Info", "fa5s.info-circle", 0)
        self.btn_controls = self._create_btn("Device Controls", "fa5s.sliders-h", 1)
        self.btn_remote = self._create_btn("Remote Control", "fa5s.desktop", 2)
        self.btn_tools = self._create_btn("Device Tool", "fa5s.toolbox", 3)
        self.btn_automation = self._create_btn("Test Automation", "fa5s.robot", 4)
        self.btn_stability = self._create_btn("System Stability Check", "fa5s.vial", 5)

        layout.addWidget(self.btn_info)
        layout.addWidget(self.btn_controls)
        layout.addWidget(self.btn_remote)
        layout.addWidget(self.btn_tools)
        layout.addWidget(self.btn_automation)
        layout.addWidget(self.btn_stability)

        layout.addStretch()

        # Version/Footer
        # version_label = QPushButton("v0.1.0") ... (Optional)

        # Set default selection
        self.btn_info.setChecked(True)
    
    def _create_btn(self, text, icon_name, index):
        btn = QPushButton(text)
        btn.setObjectName("SidebarButton")
        btn.setCheckable(True)
        btn.setProperty("icon_name", icon_name) # Store for valid retrieval
        btn.setIcon(get_icon(icon_name, color="#888888"))
        btn.setIconSize(QSize(20, 20))
        # Pass button explicitely to avoid sender() issues with lambda
        btn.clicked.connect(lambda checked=False, b=btn, i=index: self._on_btn_clicked(b, i))
        return btn
    def _on_btn_clicked(self, clicked_btn, index):
        # Uncheck all buttons
        buttons = [self.btn_info, self.btn_controls, self.btn_remote, 
                   self.btn_tools, self.btn_automation, self.btn_stability]
        for btn in buttons:
            btn.setChecked(False)
            # Restore original grey icon
            original_icon = btn.property("icon_name")
            btn.setIcon(get_icon(original_icon, color="#888888")) 
        
        # Check current
        clicked_btn.setChecked(True)
        # Set active color icon
        active_icon = clicked_btn.property("icon_name")
        clicked_btn.setIcon(get_icon(active_icon, color="#40E0D0")) # Neon Turquoise
        
        self.page_selected.emit(index)
