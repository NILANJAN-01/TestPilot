from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QTabWidget, QPlainTextEdit, QLineEdit, 
                               QComboBox, QSplitter, QProgressBar, QGroupBox, 
                               QCheckBox, QMessageBox, QFileDialog, QScrollArea)
from PySide6.QtCore import Qt, SLOT
from PySide6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QPixmap
from .base_view import BaseView
from core.context import get_context
from utils import get_icon
from utils import get_icon
import re
import time
import os

class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        
        # Formats
        err_fmt = QTextCharFormat(); err_fmt.setForeground(QColor("#FF5555")); self.rules.append((r" E ", err_fmt))
        warn_fmt = QTextCharFormat(); warn_fmt.setForeground(QColor("#FFB86C")); self.rules.append((r" W ", warn_fmt))
        info_fmt = QTextCharFormat(); info_fmt.setForeground(QColor("#8BE9FD")); self.rules.append((r" I ", info_fmt))
        debug_fmt = QTextCharFormat(); debug_fmt.setForeground(QColor("#50FA7B")); self.rules.append((r" D ", debug_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

class DeviceToolView(BaseView):
    def __init__(self):
        super().__init__("Device Tools")
        self.ctx = get_context()
        self.device_manager = self.ctx.get_service("device_manager")
        self.tool_service = self.ctx.get_service("tool_service")
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333; }
            QTabBar::tab { background: #222; color: #888; padding: 10px; min-width: 100px; }
            QTabBar::tab:selected { background: #333; color: #40E0D0; border-bottom: 2px solid #40E0D0; }
        """)
        
        self._build_logcat_tab()
        self._build_capture_tab()
        self._build_monitor_tab()
        
        self.content_layout.addWidget(self.tabs)
        
        # Connect Signals
        # Connect Signals
        self.tool_service.log_received.connect(self._on_log_line)
        self.tool_service.screenshot_saved.connect(self._on_screenshot_saved)
        self.tool_service.recording_saved.connect(self._on_recording_saved)
        self.tool_service.fault_detected.connect(self._on_fault_detected)
        self.tool_service.anr_detected.connect(self._on_anr_detected)
        self.tool_service.services_updated.connect(self._on_services_updated)

    def _build_logcat_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tools Bar
        toolbar = QHBoxLayout()
        
        # Start/Stop
        self.btn_logs = QPushButton("Start Logs")
        self.btn_logs.setCheckable(True)
        self.btn_logs.toggled.connect(self._toggle_logs)
        self.btn_logs.setStyleSheet("background: #222; color: #EEE; padding: 6px; border: 1px solid #444;")
        toolbar.addWidget(self.btn_logs)
        
        # Clear
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self._clear_logs)
        btn_clear.setStyleSheet("background: #222; padding: 6px; border: 1px solid #444; color: #EEE;")
        toolbar.addWidget(btn_clear)
        
        # Save
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._save_logs)
        btn_save.setStyleSheet("background: #222; padding: 6px; border: 1px solid #444; color: #EEE;")
        toolbar.addWidget(btn_save)

        # Level Filter
        self.cb_level = QComboBox()
        self.cb_level.addItems(["Verbose", "Debug", "Info", "Warn", "Error", "Fatal"])
        self.cb_level.setCurrentIndex(0) 
        self.cb_level.setStyleSheet("background: #111; color: #EEE; border: 1px solid #444; padding: 4px;")
        toolbar.addWidget(self.cb_level)

        # Text Filter
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("Filter (Regex/Tag/PID)...")
        self.txt_filter.setStyleSheet("background: #111; color: #FFF; padding: 6px; border: 1px solid #444;")
        toolbar.addWidget(self.txt_filter)
        
        layout.addLayout(toolbar)
        
        # Viewer
        self.log_viewer = QPlainTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("background-color: #0F0F0F; color: #DDD; font-family: Consolas, monospace; font-size: 12px;")
        self.highlighter = LogHighlighter(self.log_viewer.document())
        layout.addWidget(self.log_viewer)
        
        self.tabs.addTab(tab, "Live Logcat")

    def _build_capture_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- Screenshot Section ---
        gb_ss = QGroupBox("Screenshot Tools (Visual Evidence)")
        gb_ss.setStyleSheet("QGroupBox { border: 1px solid #333; margin-top: 10px; font-weight: bold; color: #40E0D0; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        vbox_ss = QVBoxLayout(gb_ss)
        
        h_ss = QHBoxLayout()
        btn_ss = QPushButton("Take Screenshot")
        btn_ss.setIcon(get_icon("fa5s.camera", "#FFF"))
        btn_ss.clicked.connect(self._take_screenshot)
        btn_ss.setStyleSheet("background: #222; padding: 8px; border: 1px solid #444; color: white;")
        h_ss.addWidget(btn_ss)
        
        btn_burst = QPushButton("Burst (5x)")
        btn_burst.setIcon(get_icon("fa5s.images", "#FFF"))
        btn_burst.clicked.connect(self._take_burst_screenshot)
        btn_burst.setStyleSheet("background: #222; padding: 8px; border: 1px solid #444; color: white;")
        h_ss.addWidget(btn_burst)
        
        # Preview Label
        self.lbl_preview = QLabel("No Preview")
        self.lbl_preview.setFixedSize(320, 180) # 16:9 ratio
        self.lbl_preview.setStyleSheet("background: #111; border: 1px dashed #444; color: #666;")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        h_ss.addWidget(self.lbl_preview)

        # Clear Preview
        btn_clear_prev = QPushButton("X")
        btn_clear_prev.setFixedSize(24, 24)
        btn_clear_prev.setStyleSheet("background: #444; color: #FFF; border: none; border-radius: 12px;")
        btn_clear_prev.clicked.connect(lambda: self.lbl_preview.setText("No Preview") or self.lbl_preview.setPixmap(QPixmap()))
        h_ss.addWidget(btn_clear_prev)
        
        vbox_ss.addLayout(h_ss)
        layout.addWidget(gb_ss)
        
        # --- Recording Section ---
        gb_rec = QGroupBox("Screen Recording Tools")
        gb_rec.setStyleSheet("QGroupBox { border: 1px solid #333; margin-top: 10px; font-weight: bold; color: #40E0D0; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        vbox_rec = QVBoxLayout(gb_rec)
        
        # Controls (Resolution, Bitrate)
        h_rec_opts = QHBoxLayout()
        h_rec_opts.addWidget(QLabel("Bitrate:"))
        self.cb_bitrate = QComboBox()
        self.cb_bitrate.addItems(["4 Mbps", "8 Mbps", "16 Mbps"])
        h_rec_opts.addWidget(self.cb_bitrate)
        
        h_rec_opts.addWidget(QLabel("Time Limit (s):"))
        self.txt_time = QLineEdit("180")
        self.txt_time.setFixedWidth(50)
        h_rec_opts.addWidget(self.txt_time)
        vbox_rec.addLayout(h_rec_opts)
        
        self.btn_rec = QPushButton("Start Recording")
        self.btn_rec.setCheckable(True)
        self.btn_rec.clicked.connect(self._toggle_recording)
        self.btn_rec.setStyleSheet("background: #222; padding: 10px; border: 1px solid #444; color: #FFF;")
        self.btn_rec.setIcon(get_icon("fa5s.video", "#FFF"))
        vbox_rec.addWidget(self.btn_rec)
        
        layout.addWidget(gb_rec)
        layout.addStretch()
        
        self.tabs.addTab(tab, "Capture")

    def _build_monitor_tab(self):
        tab = QWidget()
        outer_layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #121212; }")
        container = QWidget()
        container.setStyleSheet("background: #121212;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        gb_style = """
            QGroupBox { 
                border: 1px solid #333; 
                border-radius: 8px; 
                margin-top: 15px; 
                padding-top: 10px;
                font-weight: bold; 
                background: #1A1A1A;
            } 
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 15px; 
                padding: 0 10px; 
            }
        """

        # --- Global Controls ---
        h_ctrl = QHBoxLayout()
        self.btn_mon = QPushButton("Start/Stop Global Monitoring")
        self.btn_mon.setCheckable(True)
        self.btn_mon.toggled.connect(self._toggle_monitoring)
        self.btn_mon.setStyleSheet("QPushButton { background: #222; color: #40E0D0; border: 1px solid #40E0D0; padding: 12px; font-weight: bold; border-radius: 6px; } QPushButton:checked { background: #40E0D0; color: #121212; }")
        h_ctrl.addWidget(self.btn_mon)
        layout.addLayout(h_ctrl)

        # --- Section 1: CPU and Process Monitoring ---
        self.gb_cpu = QGroupBox("1. CPU and Process Monitoring")
        self.gb_cpu.setStyleSheet(gb_style + "QGroupBox { color: #40E0D0; }")
        v_cpu = QVBoxLayout(self.gb_cpu)
        
        ctrl_cpu = QHBoxLayout()
        self.chk_print_perf = QCheckBox("Print to Console")
        self.chk_record_stats = QCheckBox("Auto-Dump (perf_monitor_dump.txt)")
        btn_save_perf = QPushButton("Save Snapshot")
        btn_save_perf.clicked.connect(self._save_perf_snapshot)
        btn_save_perf.setStyleSheet("background: #333; padding: 5px; border-radius: 4px;")
        
        ctrl_cpu.addWidget(self.chk_print_perf)
        ctrl_cpu.addWidget(self.chk_record_stats)
        ctrl_cpu.addStretch()
        ctrl_cpu.addWidget(btn_save_perf)
        v_cpu.addLayout(ctrl_cpu)

        self.lbl_stats = QLabel("Monitoring Stopped...")
        self.lbl_stats.setStyleSheet("font-family: Consolas; font-size: 13px; color: #EEE; background: #000; padding: 8px; border-radius: 4px;")
        v_cpu.addWidget(self.lbl_stats)
        
        self.lbl_proc = QLabel("Waiting for data...")
        self.lbl_proc.setStyleSheet("font-family: Consolas; font-size: 12px; color: #BBB; background: #000; padding: 8px; border-radius: 4px;")
        self.lbl_proc.setMinimumHeight(120)
        v_cpu.addWidget(self.lbl_proc)
        layout.addWidget(self.gb_cpu)

        # --- Section 2: Android Service Monitoring ---
        self.gb_serv = QGroupBox("2. Android Service Monitoring")
        self.gb_serv.setStyleSheet(gb_style + "QGroupBox { color: #8BE9FD; }")
        v_serv = QVBoxLayout(self.gb_serv)
        
        ctrl_serv = QHBoxLayout()
        self.chk_print_services = QCheckBox("Print to Console")
        self.chk_record_services = QCheckBox("Auto-Dump (services_dump.txt)")
        btn_save_serv = QPushButton("Save Snapshot")
        btn_save_serv.clicked.connect(self._save_services_snapshot)
        btn_save_serv.setStyleSheet("background: #333; padding: 5px; border-radius: 4px;")
        
        ctrl_serv.addWidget(self.chk_print_services)
        ctrl_serv.addWidget(self.chk_record_services)
        ctrl_serv.addStretch()
        ctrl_serv.addWidget(btn_save_serv)
        v_serv.addLayout(ctrl_serv)

        self.lbl_serv = QLabel("Waiting for data...")
        self.lbl_serv.setStyleSheet("font-family: Consolas; font-size: 11px; color: #BBB; background: #000; padding: 8px; border-radius: 4px;")
        self.lbl_serv.setWordWrap(True)
        v_serv.addWidget(self.lbl_serv)
        layout.addWidget(self.gb_serv)

        # --- Section 3: ANR and Crash Monitoring ---
        self.gb_fault = QGroupBox("3. ANR and Crash Monitoring")
        self.gb_fault.setStyleSheet(gb_style + "QGroupBox { color: #FF5555; }")
        v_fault = QVBoxLayout(self.gb_fault)
        
        self.chk_crash = QCheckBox("Auto-capture on Crash (FATAL)")
        self.chk_crash.toggled.connect(self._toggle_fault_mon)
        self.chk_anr = QCheckBox("Auto-capture on ANR")
        self.chk_anr.toggled.connect(self._toggle_fault_mon)
        self.chk_log_anr = QCheckBox("Log ANR/Crash to Console")
        self.chk_log_anr.setChecked(True)
        
        v_fault.addWidget(self.chk_crash)
        v_fault.addWidget(self.chk_anr)
        v_fault.addWidget(self.chk_log_anr)
        
        btn_save_fault_log = QPushButton("Save Current Buffer as Fault Log")
        btn_save_fault_log.clicked.connect(self._save_fault_report)
        btn_save_fault_log.setStyleSheet("background: #400; padding: 8px; border-radius: 4px; color: white;")
        v_fault.addWidget(btn_save_fault_log)
        
        layout.addWidget(self.gb_fault)
        layout.addStretch()

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)
        self.tabs.addTab(tab, "Monitoring")
        
    def _toggle_fault_mon(self):
        # Enable fault logic in service
        any_checked = self.chk_crash.isChecked() or self.chk_anr.isChecked()
        self.tool_service.fault_monitoring = any_checked
        
    def _toggle_monitoring(self, checked):
        serial = self.device_manager.get_first_device()
        if not serial: return
        
        if checked:
            # Ask for save file if they want to dump?
            # For now, just start. We can add a "Record to File" button if needed, 
            # OR just auto-save if a checkbox is checked. 
            self.tool_service.start_monitoring(serial)
            self.tool_service.perf_stats_updated.connect(self._on_perf_stats)
        else:
            self.tool_service.stop_monitoring()
            self.lbl_stats.setText("Monitoring Stopped.")
            try:
                self.tool_service.perf_stats_updated.disconnect(self._on_perf_stats)
            except: pass

    def _on_perf_stats(self, stats):
        try:
            # System Stats (Thermal & Memory)
            therm = stats.get('thermal', "Unknown")
            mem_raw = stats.get('mem', "")
            sys_txt = f"Thermal: {therm}\nMemory Raw: {mem_raw[:80]}..."
            self.lbl_stats.setText(sys_txt)
            
            # 2. Process Stats (CPU Top)
            cpu_raw = stats.get('cpu_raw', "")
            # top output: "Tasks: ... Mem: ... swap: ... PID USER PR NI VIRT RES ..."
            # We want lines starting from PID
            lines = cpu_raw.splitlines()
            proc_txt = "Top Processes:\n"
            count = 0
            for l in lines:
                l = l.strip()
                if not l: continue
                if "PID" in l: 
                    proc_txt += l + "\n"
                    continue
                # If it looks like a process line (starts with digit)
                if l[0].isdigit():
                    proc_txt += l + "\n"
                    count += 1
                if count > 8: break
            
            self.lbl_proc.setText(proc_txt)
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Print to Console
            if self.chk_print_perf.isChecked():
                print(f"[{timestamp}] Perf Stats: Thermal={therm} | CPU Summary: {stats.get('cpu_summary')}")

            # Auto-Dump to File
            if self.chk_record_stats.isChecked():
                dump_file = os.path.join(os.getcwd(), "perf_monitor_dump.txt")
                with open(dump_file, "a", encoding="utf-8") as f:
                    f.write(f"--- {timestamp} ---\n")
                    f.write(f"Thermal: {therm}\nMemory Raw: {mem_raw}\n")
                    f.write(f"CPU Raw:\n{cpu_raw}\n\n")

        except Exception as e:
            print(f"Stats Error: {e}")

    def _save_perf_snapshot(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Perf Snapshot", f"perf_snapshot_{int(time.time())}.txt", "Text Files (*.txt)")
        if path:
            content = f"Snapshot Time: {time.ctime()}\n"
            content += f"System Stats:\n{self.lbl_stats.text()}\n\n"
            content += f"Process List:\n{self.lbl_proc.text()}\n"
            with open(path, "w") as f:
                f.write(content)
            QMessageBox.information(self, "Saved", f"Perf snapshot saved to {path}")

    def _on_services_updated(self, services):
        try:
            summary = ", ".join(services[:15]) + ("..." if len(services) > 15 else "")
            self.lbl_serv.setText(f"Running Services ({len(services)}):\n{summary}")
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            if self.chk_print_services.isChecked():
                print(f"[{timestamp}] Services Count: {len(services)} | Sample: {summary[:50]}...")

            if self.chk_record_services.isChecked():
                dump_file = os.path.join(os.getcwd(), f"services_dump.txt")
                with open(dump_file, "a") as f:
                    f.write(f"--- {timestamp} ---\n")
                    f.write("\n".join(services) + "\n\n")
                
        except Exception as e:
            print(f"Services UI Error: {e}")

    def _save_services_snapshot(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Services Snapshot", f"services_snapshot_{int(time.time())}.txt", "Text Files (*.txt)")
        if path:
            # We don't have the full list in the label, but we can potentially wait for next update or just use what we have.
            # Ideally we'd store the last full list.
            with open(path, "w") as f:
                f.write(f"Services Snapshot: {time.ctime()}\n")
                f.write(self.lbl_serv.text())
            QMessageBox.information(self, "Saved", f"Services snapshot saved to {path}")

    def _save_fault_report(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Fault Report", f"full_log_report_{int(time.time())}.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w") as f:
                f.write(f"Fault Report Generated: {time.ctime()}\n\n")
                f.write(self.log_viewer.toPlainText())
            QMessageBox.information(self, "Saved", f"Full log report saved to {path}")

    def _on_anr_detected(self, details):
        if self.chk_log_anr.isChecked():
            print(f"!!! ANR DETECTED !!!\n{details}")
        
        # Trigger Auto-Capture if checked
        if self.chk_anr.isChecked():
            print("Auto-capturing ANR fault...")
            timestamp = int(time.time())
            anr_path = os.path.join(os.getcwd(), f"anr_log_{timestamp}.txt")
            with open(anr_path, "w") as f:
                f.write(f"ANR DETECTED\nDetails: {details}\n\nBuffer Snapshot:\n")
                f.write(self.log_viewer.toPlainText())
            
            serial = self.device_manager.get_first_device()
            if serial:
                ss_path = os.path.join(os.getcwd(), f"anr_screenshot_{timestamp}.png")
                self.tool_service.take_screenshot(serial, ss_path)
            
            self.log_viewer.appendPlainText(f"\n!!! ANR CAPTURED: Saved to {anr_path} !!!\n")

    def _toggle_recording(self, checked):
        serial = self.device_manager.get_first_device()
        if not serial: return
        
        if checked:
            self.btn_rec.setText("Stop Recording")
            self.btn_rec.setStyleSheet("background: #500; color: #FFF; border: 1px solid #F00;")
            # Parse Options
            br_map = {"4 Mbps": "4000000", "8 Mbps": "8000000", "16 Mbps": "16000000"}
            br = br_map.get(self.cb_bitrate.currentText(), "4000000")
            tl = self.txt_time.text()
            opts = f"--bit-rate {br} --time-limit {tl}"
            self.tool_service.start_recording(serial, opts)
        else:
            self.btn_rec.setText("Start Recording")
            self.btn_rec.setStyleSheet("background: #222; color: #FFF; border: 1px solid #444;")
            # Save
            # Save Dialog or Default?
            # User wants to save to any folder.
            path, _ = QFileDialog.getSaveFileName(self, "Save Screen Record", f"rec_{int(time.time())}.mp4", "MP4 Video (*.mp4)")
            if not path:
                path = os.path.join(os.getcwd(), f"rec_{int(time.time())}.mp4") # Fallback
                
            self.tool_service.stop_recording(serial, path)
            # Message will be shown in _on_recording_saved

    def _on_recording_saved(self, path):
         QMessageBox.information(self, "Recording Saved", f"Saved to {path}")

    def _take_screenshot(self):
        serial = self.device_manager.get_first_device()
        if not serial: return
        
        # User requested "option to save the screen short to any location"
        # Since this is a "One-click capture", popping a dialog every time destroys the "One-click" experience.
        # Better approach: Default to a folder, but allow "Save As" if right-clicked? 
        # OR: Just use a standard "Capture" folder?
        # User said: "here there is no option to save the screen short to any location... there should be a option"
        # I will use QFileDialog for now as it's the most flexible interpretation.
        
        path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", f"ss_{int(time.time())}.png", "Images (*.png)")
        if not path:
             return # Cancelled
             
        self.tool_service.take_screenshot(serial, path)
        
    def _take_burst_screenshot(self):
        serial = self.device_manager.get_first_device()
        if not serial: return
        
        # Burst saves to a directory
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory for Burst")
        if not dir_path: return
        
        for i in range(5):
            path = os.path.join(dir_path, f"ss_burst_{int(time.time())}_{i}.png")
            self.tool_service.take_screenshot(serial, path)
            time.sleep(0.2)

    def _on_screenshot_saved(self, path):
        # Show in Preview
        from PySide6.QtGui import QPixmap
        pix = QPixmap(path)
        if not pix.isNull():
            self.lbl_preview.setPixmap(pix.scaled(self.lbl_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # If this was an auto-capture (we might want to flag it or notify), for now just show preview if tab is open?
        # Maybe add a small notification?
        pass

    def _save_logs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Logs", f"logcat_{int(time.time())}.txt", "Text Files (*.txt)")
        if path:
            self.tool_service.save_logs(self.log_viewer.toPlainText(), path)
            QMessageBox.information(self, "Logs Saved", f"Saved to {path}")

    # --- Logic ---
    def _toggle_logs(self, checked):
        serial = self.device_manager.get_first_device()
        if not serial: 
            self.btn_logs.setChecked(False)
            return
            
        if checked:
            self.btn_logs.setText("Stop Logs")
            self.btn_logs.setStyleSheet("background: #400; color: #FFF; padding: 6px; border: 1px solid #F00;")
            self.tool_service.start_logcat(serial)
        else:
            self.btn_logs.setText("Start Logs")
            self.btn_logs.setStyleSheet("background: #222; color: #EEE; padding: 6px; border: 1px solid #444;")
            self.tool_service.stop_logcat()

    def _on_log_line(self, line):
        # 1. Level Filter
        # Format typical: "MM-DD HH:MM:SS.ms L/Tag(PID): Msg" or just "L/Tag"
        # We look for " V ", " D ", " I ", " W ", " E ", " F " usually, or "/D ", "/E " etc.
        # But 'adb logcat -v time' gives: "12-18 00:01:54.434 D/Tag ( 123): Msg"
        # So we look for " D/", " I/" etc.
        
        levels = ["V", "D", "I", "W", "E", "F"]
        selected_idx = self.cb_level.currentIndex()
        if selected_idx > 0:
            # Check line level
            is_pass = False
            for i in range(selected_idx, len(levels)):
                if f" {levels[i]}/" in line or f" {levels[i]} " in line:
                    is_pass = True
                    break
            if not is_pass:
                # Fallback for different formats? 
                # If we can't detect level, we might let it show or hide. 
                # Let's hide if we are strict, or show if uncertain.
                # Assuming standard format:
                pass 
                return

        # 2. Text/Regex Filter
        flt = self.txt_filter.text()
        if flt:
            try:
                if not re.search(flt, line, re.IGNORECASE):
                    return
            except:
                # invalid regex, treat as substring
                if flt.lower() not in line.lower():
                    return
            
        self.log_viewer.appendPlainText(line.strip())
        
    def _clear_logs(self):
        self.log_viewer.clear()
        serial = self.device_manager.get_first_device()
        if serial:
            self.tool_service.clear_logcat(serial)

    # --- Fault Automation ---
    def _on_fault_detected(self, f_type, details):
        if self.chk_log_anr.isChecked():
            print(f"!!! FAULT DETECTED: {f_type} !!!\n{details}")
        
        # 1. Save Logs
        log_path = os.path.join(os.getcwd(), f"crash_log_{int(time.time())}.txt")
        self.tool_service.save_logs(self.log_viewer.toPlainText(), log_path)
        
        # 2. Take Screenshot
        # We need a unique name
        serial = self.device_manager.get_first_device()
        if serial:
            ss_path = os.path.join(os.getcwd(), f"crash_ss_{int(time.time())}.png")
            self.tool_service.take_screenshot(serial, ss_path)
            
        # Optional: Notify user
        self.log_viewer.appendPlainText(f"\n!!! AUTO-CAPTURED FAULT: {f_type} !!!\nSaved to {log_path}\n")
