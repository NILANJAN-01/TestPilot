from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QPushButton, QLabel, QFrame, QScrollArea, 
                               QLineEdit, QListWidget, QComboBox, QCheckBox, 
                               QInputDialog, QDialog, QDialogButtonBox, QFormLayout)
from PySide6.QtCore import Qt, QSize
from .base_view import BaseView
from core.context import get_context
from utils import get_icon
from core.worker import Worker

class DeviceControlsView(BaseView):
    def __init__(self):
        super().__init__("Device Controls")
        
        self.ctx = get_context()
        self.device_manager = self.ctx.get_service("device_manager")
        
        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll.setWidget(self.container)
        
        self.content_layout.addWidget(self.scroll)

        # Build Sections directly into main_layout (Row-wise stack)
        self._build_media_section()
        self._build_connectivity_section()
        self._build_app_section()
        self._build_power_section()
        self._build_input_section()
        self._build_auto_section() 
        
        # Add stretch to bottom to push items up if window is tall
        self.main_layout.addStretch()
        
        # Initial State Update
        if self.device_manager and self.device_manager.connected_devices:
            self._update_toggles_state()
            
    def _create_section_frame(self, title, layout):
        frame = QFrame()
        frame.setObjectName("ControlSection")
        frame.setStyleSheet("""
            QFrame#ControlSection {
                background-color: #1A1A1A;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(15, 15, 15, 15)
        
        lbl = QLabel(title)
        lbl.setStyleSheet("""
            color: #40E0D0; 
            font-size: 14px; 
            font-weight: 800; 
            text-transform: uppercase;
            border-bottom: 2px solid #40E0D0;
            padding-bottom: 5px;
            margin-bottom: 10px;
        """)
        vbox.addWidget(lbl)
        
        layout.addWidget(frame)
        return vbox

    # ... (Keep Helper Methods _add_btn, _add_grid_btn, _add_toggle) 
    def _add_btn(self, layout, text, icon, col_span=1, callback=None):
        btn = QPushButton(text)
        btn.setIcon(get_icon(icon, color="#FFFFFF"))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #EEE;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                text-align: left;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #333;
                border: 1px solid #40E0D0;
                color: #FFF;
            }
            QPushButton:pressed {
                background-color: #40E0D0;
                color: #000;
            }
        """)
        if callback:
            btn.clicked.connect(callback)
            
        layout.addWidget(btn)
        return btn

    def _add_grid_btn(self, grid, text, icon, row, col, cb):
        btn = QPushButton(text)
        btn.setIcon(get_icon(icon, color="#FFF"))
        if cb:
            btn.clicked.connect(cb)
        
        btn.setStyleSheet("""
            QPushButton {
                background-color: #252525; border: 1px solid #333; 
                color: #DDD; padding: 10px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #333; border-color: #40E0D0; }
        """)
        grid.addWidget(btn, row, col)
        return btn

    def _add_toggle(self, layout, label, callback=None):
        toggle = QCheckBox(label)
        toggle.setStyleSheet("""
            QCheckBox { spacing: 10px; color: #DDD; font-size: 14px; }
            QCheckBox::indicator { width: 40px; height: 20px; border-radius: 10px; background: #444; }
            QCheckBox::indicator:checked { background: #40E0D0; }
        """)
        if callback:
            toggle.clicked.connect(callback)
        layout.addWidget(toggle)
        return toggle

    # --- Sections ---

    def _build_media_section(self):
        # Use main_layout instead of col
        layout = self._create_section_frame("Media & Audio", self.main_layout)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        # Make grid columns stretch equally
        for i in range(4): # Play, Stop, Prev, Next
            grid.setColumnStretch(i, 1)
            
        layout.addLayout(grid)
        
        # Row 1: Play/Pause, Stop
        self._add_grid_btn(grid, "Play/Pause", "fa5s.play", 0, 0, self._media_play_pause)
        self._add_grid_btn(grid, "Stop", "fa5s.stop", 0, 1, self._media_stop)
        
        # Row 2: Prev, Next
        self._add_grid_btn(grid, "Prev", "fa5s.step-backward", 0, 2, self._media_prev)
        self._add_grid_btn(grid, "Next", "fa5s.step-forward", 0, 3, self._media_next)
        
        # Row 3: Vol Up, Down, Mute
        self._add_grid_btn(grid, "Vol Up", "fa5s.volume-up", 1, 0, self._vol_up)
        self._add_grid_btn(grid, "Vol Down", "fa5s.volume-down", 1, 1, self._vol_down)
        self._add_grid_btn(grid, "Mute", "fa5s.volume-mute", 1, 2, self._mute)


    def _build_connectivity_section(self):
        layout = self._create_section_frame("Connectivity", self.main_layout)
        
        # Grid for Wifi/BT side-by-side or stacked? 
        # User said "row wise", so let's stack them but make them utilize width.
        
        # Wi-Fi Row
        wifi_row = QHBoxLayout()
        self.wifi_toggle = self._add_toggle(wifi_row, "Wi-Fi", self._toggle_wifi)
        
        btn_scan = QPushButton("Scan")
        btn_scan.setFixedWidth(100)
        btn_scan.setIcon(get_icon("fa5s.sync", "#FFF"))
        btn_scan.clicked.connect(self._scan_wifi)
        btn_scan.setStyleSheet("background-color: #333; color: white; border: 1px solid #555;")
        wifi_row.addWidget(btn_scan)
        wifi_row.addStretch()
        layout.addLayout(wifi_row)
        
        # Wi-Fi List
        self.wifi_list = QListWidget()
        self.wifi_list.setFixedHeight(150)
        self.wifi_list.setStyleSheet("background: #111; border: 1px solid #333; color: #BBB;")
        layout.addWidget(self.wifi_list)
        
        btn_connect = QPushButton("Connect Selected SSID")
        btn_connect.setStyleSheet("background: #222; color: #40E0D0; border: 1px solid #40E0D0; padding: 6px; font-weight: bold;")
        btn_connect.clicked.connect(self._connect_selected_wifi)
        layout.addWidget(btn_connect)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 10px;")
        layout.addWidget(line)

        # Bluetooth Row
        bt_row = QHBoxLayout()
        self.bt_toggle = self._add_toggle(bt_row, "Bluetooth", self._toggle_bt)
        bt_row.addStretch()
        layout.addLayout(bt_row)
        
        self.bt_list = QListWidget()
        self.bt_list.setFixedHeight(80)
        self.bt_list.setStyleSheet("background: #111; border: 1px solid #333; color: #BBB;")
        self.bt_list.addItem("Scan not fully supported via raw ADB")
        layout.addWidget(self.bt_list)

    def _build_app_section(self):
        layout = self._create_section_frame("App Lifecycle", self.main_layout)
        
        input_row = QHBoxLayout()
        self.pkg_input = QLineEdit()
        self.pkg_input.setPlaceholderText("com.example.package")
        self.pkg_input.setStyleSheet("background: #111; color: white; padding: 8px; border: 1px solid #444; border-radius: 4px;")
        input_row.addWidget(self.pkg_input)
        layout.addLayout(input_row)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        for i in range(4): grid.setColumnStretch(i, 1)
        layout.addLayout(grid)
        
        self._add_grid_btn(grid, "Launch Home", "fa5s.home", 0, 0, self._launch_home)
        self._add_grid_btn(grid, "Force Stop", "fa5s.stop-circle", 0, 1, self._force_stop)
        self._add_grid_btn(grid, "Clear Data", "fa5s.trash-alt", 0, 2, self._clear_data)
        self._add_grid_btn(grid, "Kill All BG", "fa5s.skull", 0, 3, lambda: None)

    def _build_power_section(self):
        layout = self._create_section_frame("Power & System", self.main_layout)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        for i in range(4): grid.setColumnStretch(i, 1)
        layout.addLayout(grid)
        
        self._add_grid_btn(grid, "Screen On/Off", "fa5s.power-off", 0, 0, self._power_btn)
        self._add_grid_btn(grid, "Reboot", "fa5s.sync-alt", 0, 1, self._reboot)
        self._add_grid_btn(grid, "Sleep", "fa5s.moon", 0, 2, lambda: self._input_key(223))
        self._add_grid_btn(grid, "Wake", "fa5s.sun", 0, 3, lambda: self._input_key(224))

    def _build_display_section(self):
        layout = self._create_section_frame("Display & Mirroring", self.main_layout)
        
        info = QLabel("Mirror and control your device via high-performance scrcpy.")
        info.setStyleSheet("color: #888; font-size: 11px; margin-bottom: 5px;")
        layout.addWidget(info)

        grid = QGridLayout()
        grid.setSpacing(10)
        for i in range(2): grid.setColumnStretch(i, 1)
        layout.addLayout(grid)
        
        btn_mirror = self._add_grid_btn(grid, "Start Remote Control", "fa5s.desktop", 0, 0, self._start_remote)
        btn_mirror.setStyleSheet("background: #40E0D022; border: 1px solid #40E0D0; color: #40E0D0; padding: 15px; font-weight: bold;")
        
        self._add_grid_btn(grid, "Screen Always On", "fa5s.eye", 0, 1, self._toggle_stay_awake)

    def _start_remote(self):
        serial = self._get_serial()
        if not serial: return
        
        remote_svc = self.ctx.get_service("remote_control")
        remote_svc.start_mirroring(serial)

    def _toggle_stay_awake(self):
        # adb shell svc power stayon true
        self._run_async(lambda s: self.device_manager.adb.shell(s, "svc power stayon true"))
        self.ctx.get_service("device_manager").notification.emit("Device 'Stay Awake' enabled.", "info")

    def _build_auto_section(self):
        # Empty for now
        pass

    def _build_input_section(self):
        layout = self._create_section_frame("Input Simulation", self.main_layout)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        for i in range(4): grid.setColumnStretch(i, 1)
        layout.addLayout(grid)
        
        self._add_grid_btn(grid, "Tap Center", "fa5s.fingerprint", 0, 0, lambda: None)
        self._add_grid_btn(grid, "Swipe Left", "fa5s.arrow-left", 0, 1, lambda: None)
        self._add_grid_btn(grid, "Swipe Right", "fa5s.arrow-right", 0, 2, lambda: None)
        self._add_grid_btn(grid, "Back", "fa5s.arrow-left", 0, 3, lambda: self._input_key(4))

    # --- Actions ---
    def _get_serial(self):
        return self.device_manager.get_first_device()

    def _run_async(self, func, *args):
        serial = self._get_serial()
        if not serial: return
        
        worker = Worker(func, serial, *args)
        self.device_manager.thread_pool.start(worker)

    # Media
    def _media_play_pause(self): self._run_async(self.device_manager.controller.media_play_pause)
    def _media_stop(self): self._run_async(self.device_manager.controller.media_stop)
    def _media_next(self): self._run_async(self.device_manager.controller.media_next)
    def _media_prev(self): self._run_async(self.device_manager.controller.media_prev)
    def _vol_up(self): self._run_async(self.device_manager.controller.volume_up)
    def _vol_down(self): self._run_async(self.device_manager.controller.volume_down)
    def _mute(self): self._run_async(lambda s: self.device_manager.controller._exec(s, "input keyevent 164"))

    # Connectivity
    def _toggle_wifi(self):
        state = self.wifi_toggle.isChecked()
        self._run_async(self.device_manager.controller.set_wifi, state)
        
    def _toggle_bt(self):
        state = self.bt_toggle.isChecked()
        self._run_async(self.device_manager.controller.set_bt, state)

    def _scan_wifi(self):
        serial = self._get_serial()
        if not serial: return
        self.wifi_list.clear()
        self.wifi_list.addItem("Scanning...")
        
        def job(s):
            self.device_manager.controller.scan_wifi(s)
            import time; time.sleep(2) 
            return self.device_manager.controller.get_wifi_networks(s)
            
        worker = Worker(job, serial)
        worker.signals.result.connect(self._on_wifi_results)
        self.device_manager.thread_pool.start(worker)

    def _on_wifi_results(self, networks):
        self.wifi_list.clear()
        for net in networks:
            self.wifi_list.addItem(net)

    def _connect_selected_wifi(self):
        item = self.wifi_list.currentItem()
        if not item: return
        
        raw_text = item.text()
        ssid_guess = ""
        parts = raw_text.split()
        if len(parts) > 1 and ":" not in parts[-1] and "[" not in parts[-1]:
             ssid_guess = parts[-1] 

        dialog = QDialog(self)
        dialog.setWindowTitle("Connect Wi-Fi")
        form = QFormLayout(dialog)
        
        txt_ssid = QLineEdit(ssid_guess)
        txt_pass = QLineEdit()
        txt_pass.setEchoMode(QLineEdit.Password)
        
        form.addRow("SSID:", txt_ssid)
        form.addRow("Password:", txt_pass)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        form.addRow(btns)
        
        if dialog.exec() == QDialog.Accepted:
            ssid = txt_ssid.text()
            pwd = txt_pass.text()
            if ssid:
                self._run_async(self.device_manager.controller.connect_wifi, ssid, pwd)

    def _update_toggles_state(self):
        serial = self._get_serial()
        if not serial: return
        
        def check_state(s):
            return {
                "wifi": self.device_manager.controller.is_wifi_on(s),
                "bt": self.device_manager.controller.is_bt_on(s)
            }
            
        worker = Worker(check_state, serial)
        worker.signals.result.connect(self._on_state_checked)
        self.device_manager.thread_pool.start(worker)

    def _on_state_checked(self, states):
        self.wifi_toggle.blockSignals(True)
        self.wifi_toggle.setChecked(states["wifi"])
        self.wifi_toggle.blockSignals(False)
        
        self.bt_toggle.blockSignals(True)
        self.bt_toggle.setChecked(states["bt"])
        self.bt_toggle.blockSignals(False)

    # App
    def _launch_home(self): self._run_async(self.device_manager.controller.launch_home)
    def _force_stop(self): self._run_async(self.device_manager.controller.force_stop, self.pkg_input.text())
    def _clear_data(self): self._run_async(self.device_manager.controller.clear_data, self.pkg_input.text())

    # Power
    def _power_btn(self): self._run_async(self.device_manager.controller.power_btn)
    def _reboot(self): self._run_async(self.device_manager.controller.reboot)
    def _input_key(self, code): self._run_async(lambda s: self.device_manager.controller._exec(s, f"input keyevent {code}"))
