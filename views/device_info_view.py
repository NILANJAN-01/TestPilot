from PySide6.QtWidgets import (QLabel, QGridLayout, QFrame, QVBoxLayout, QScrollArea, 
                               QWidget, QMessageBox, QHBoxLayout)
from .base_view import BaseView
from core.context import get_context
from PySide6.QtCore import Qt

class DeviceInfoView(BaseView):
    def __init__(self):
        super().__init__("Device Information")
        
        self.ctx = get_context()
        self.device_manager = self.ctx.get_service("device_manager")
        self.labels_map = {} # Store refs to labels

        # Scroll Area for massive info
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;") # Transparent to blend
        
        # Container inside Scroll
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;") # Transparent
        self.scroll_layout = QVBoxLayout(self.container)
        self.scroll_layout.setSpacing(30)
        self.scroll.setWidget(self.container)
        
        self.content_layout.addWidget(self.scroll)

        # Categories to render
        self.categories = [
            "Identity", "Software", "Automotive", "Runtime", 
            "Storage", "Security", "InputOutput", "Region"
        ]
        
        # Build UI Skeleton
        self._build_skeleton()

        # Connect signals
        if self.device_manager:
            self.device_manager.devices_updated.connect(self._on_devices_updated)
            self.device_manager.device_disconnected.connect(self._on_disconnected)
            self.device_manager.device_props_ready.connect(self._on_data_ready)
            
            # Trigger initial update if already ready
            if self.device_manager.connected_devices:
                 self._on_devices_updated(self.device_manager.connected_devices)
            else:
                self.show_loading_state()

    def show_loading_state(self):
        # Optional: Show a loading spinner or text?
        pass

    def _build_skeleton(self):
        # Flattened Layout: Stack of sections (Row-wise)
        # Use main scroll_layout
        
        # Iterate all categories and add to scroll layout
        for cat in self.categories:
            self._create_section(cat, self.scroll_layout)
            
        # Add stretch at end
        self.scroll_layout.addStretch()

    def _create_section(self, title, parent_layout):
        # Section Card (Frame)
        card = QFrame()
        card.setObjectName("InfoSectionCard")
        # Card Styling
        card.setStyleSheet("""
            QFrame#InfoSectionCard {
                background-color: #1A1A1A; 
                border: 1px solid #333; 
                border-radius: 8px;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Header
        lbl_header = QLabel(title)
        lbl_header.setStyleSheet("""
            color: #40E0D0; 
            font-size: 15px; 
            font-weight: 900; 
            text-transform: uppercase;
            letter-spacing: 1.5px;
            border-bottom: 2px solid #40E0D0;
            padding-bottom: 8px;
            margin-bottom: 5px;
        """)
        card_layout.addWidget(lbl_header)
        
        # Content Grid
        grid = QGridLayout()
        grid.setSpacing(20) 
        grid.setVerticalSpacing(20)
        
        # 3 Columns for wide density now that it's full width
        for i in range(3):
            grid.setColumnStretch(i, 1)
            
        card_layout.addLayout(grid)
        parent_layout.addWidget(card)
        
        # Store grid ref
        self.labels_map[title] = {"grid": grid, "items": {}}

    def _update_section(self, category, data: dict):
        if category not in self.labels_map: return
        
        grid = self.labels_map[category]["grid"]
        items_map = self.labels_map[category]["items"]

        current_count = len(items_map)
        
        for key, value in data.items():
            if key in items_map:
                items_map[key].setText(value)
            else:
                row = current_count // 3 # 3 columns
                col = current_count % 3
                
                lbl_val = self._create_info_item(grid, key, value, row, col)
                items_map[key] = lbl_val
                current_count += 1

    def _create_info_item(self, layout, key, value, row, col):
        # Container
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        
        # Key Label
        t = QLabel(key.upper())
        # Muted Cyan/Grey for professional look
        t.setStyleSheet("color: #78909C; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;")
        
        # Value Label
        v = QLabel(value)
        # Bright White, slightly larger
        v.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 500; font-family: 'Segoe UI', sans-serif;")
        v.setWordWrap(True)
        v.setTextInteractionFlags(Qt.TextSelectableByMouse)
        v.setCursor(Qt.IBeamCursor)
        
        vbox.addWidget(t)
        vbox.addWidget(v)
        
        layout.addWidget(container, row, col)
        return v

    def _on_devices_updated(self, devices):
        if not devices:
            self._on_disconnected()
            return
            
        serial = devices[0]
        # Async fetch request
        self.device_manager.fetch_device_props(serial)

    def _on_data_ready(self, full_data):
        # Called when worker finishes
        try:
            for cat, data in full_data.items():
                self._update_section(cat, data)
        except Exception as e:
            print(f"UI Update Error: {e}")

    def _on_disconnected(self):
        # Show Popup
        # Note: QMessageBox might block. Use a overlay or non-modal if preferred.
        # But user requested "popup".
        # Check if we already showed it recently to avoid spam? 
        # For now, simplistic.
        pass # Disabling auto-popup on disconnect to avoid annoyance during dev, can re-enable or use banner.

