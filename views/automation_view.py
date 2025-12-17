import os
import time
import shutil
import webbrowser
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QComboBox, QProgressBar, QTextEdit, 
                                QMessageBox, QFileDialog, QScrollArea, QApplication, QMainWindow)
from PySide6.QtCore import Qt
from .base_view import BaseView
from core.context import get_context
from utils import get_icon

class AutomationView(BaseView):
    def __init__(self):
        super().__init__("Test Automation")
        self.ctx = get_context()
        self.device_manager = self.ctx.get_service("device_manager")
        self.automation_service = self.ctx.get_service("automation")
        
        self.current_report = None
        self.current_report_dir = None
        
        self._build_ui()
        
        # Connect Signals
        self.automation_service.automation_finished.connect(self._on_automation_finished)

    def _build_ui(self):
        # Create a scroll area to ensure responsiveness
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #121212; }")
        
        container = QWidget()
        container.setStyleSheet("background: #121212;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(30)

        # --- Header ---
        header = QLabel("Test Automation Hub")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #40E0D0;")
        layout.addWidget(header)

        # --- TMX Execution Section ---
        tmx_section = QWidget()
        tmx_section_layout = QVBoxLayout(tmx_section)
        tmx_section_layout.setContentsMargins(0, 0, 0, 0)
        tmx_section_layout.setSpacing(15)

        tmx_header = QLabel("TMX Automation Suite")
        tmx_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #EEE;")
        tmx_section_layout.addWidget(tmx_header)

        config_box = QWidget()
        config_box.setStyleSheet("background: #1E1E1E; border-radius: 12px; border: 1px solid #333;")
        config_layout = QVBoxLayout(config_box)
        config_layout.setContentsMargins(25, 25, 25, 25)
        config_layout.setSpacing(15)

        tmx_label = QLabel("Select Health Check Suite (TMX):")
        tmx_label.setStyleSheet("color: #AAA; border: none; font-size: 13px;")
        config_layout.addWidget(tmx_label)

        self.cb_tmx = QComboBox()
        self.cb_tmx.addItems([
            "TMX_FULL: System Health Check (15 Tests)",
            "TMX_UI: Core Interaction & Navigation",
            "TMX_CORE: Basic Boot & Services",
            "TMX_CONNECTIVITY: BT & Wifi Health",
            "TMX_MEDIA: Audio & Display Monitor",
            "STABILITY: System Stability Check"
        ])
        self.cb_tmx.setStyleSheet("""
            QComboBox {
                background: #111; 
                color: #FFF; 
                padding: 12px; 
                border: 1px solid #444;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background: #222; selection-background-color: #40E0D0; }
        """)
        config_layout.addWidget(self.cb_tmx)

        self.btn_run = QPushButton(" Run TMX Execution")
        self.btn_run.setIcon(get_icon("fa5s.play", "#121212"))
        self.btn_run.setStyleSheet("""
            QPushButton {
                background-color: #40E0D0;
                color: #121212;
                font-weight: bold;
                font-size: 16px;
                padding: 18px;
                border-radius: 8px;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #45F5E2; }
            QPushButton:pressed { background-color: #38C8B8; }
            QPushButton:disabled { background-color: #333; color: #666; }
        """)
        self.btn_run.clicked.connect(self._run_automation)
        config_layout.addWidget(self.btn_run)
        
        tmx_section_layout.addWidget(config_box)
        layout.addWidget(tmx_section)

        # --- Progress & Results ---
        self.status_lbl = QLabel("Ready for execution.")
        self.status_lbl.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.status_lbl)

        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar { border: 1px solid #333; border-radius: 6px; text-align: center; background: #111; height: 10px; }
            QProgressBar::chunk { background-color: #40E0D0; border-radius: 5px; }
        """)
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)

        # Result Action Bar
        self.results_box = QWidget()
        self.results_box.hide()
        res_layout = QHBoxLayout(self.results_box)
        res_layout.setContentsMargins(0, 0, 0, 0)
        res_layout.setSpacing(15)

        self.btn_view_report = QPushButton(" View Report")
        self.btn_view_report.setIcon(get_icon("fa5s.chart-bar", "#FFF"))
        self.btn_view_report.setStyleSheet("""
            QPushButton { background: #2E7D32; color: white; padding: 15px; border-radius: 6px; font-weight: 600; }
            QPushButton:hover { background: #388E3C; }
        """)
        self.btn_view_report.clicked.connect(self._view_report)
        res_layout.addWidget(self.btn_view_report)

        self.btn_download = QPushButton(" Download (Zip)")
        self.btn_download.setIcon(get_icon("fa5s.download", "#FFF"))
        self.btn_download.setStyleSheet("""
            QPushButton { background: #1976D2; color: white; padding: 15px; border-radius: 6px; font-weight: 600; }
            QPushButton:hover { background: #1E88E5; }
        """)
        self.btn_download.clicked.connect(self._download_report)
        res_layout.addWidget(self.btn_download)
        
        layout.addWidget(self.results_box)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        self.content_layout.addWidget(scroll)

    def _run_automation(self):
        serial = self.device_manager.get_first_device()
        if not serial:
            QMessageBox.warning(self, "No Device", "Please connect a device first.")
            return

        test_suite = self.cb_tmx.currentText()
        if "STABILITY" in test_suite:
             # Find MainWindow and switch sidebar to index 5
             for widget in QApplication.topLevelWidgets():
                 if isinstance(widget, QMainWindow) and hasattr(widget, "sidebar"):
                     widget.sidebar.btn_stability.click()
             return

        self.btn_run.setEnabled(False)
        self.status_lbl.setText(f"Executing {test_suite} on {serial}...")
        self.progress.show()
        self.results_box.hide()
        
        self.automation_service.run_tmx_test(serial, test_suite)

    def _on_automation_finished(self, report_path, output_dir):
        self.current_report = report_path
        self.current_report_dir = output_dir
        
        self.btn_run.setEnabled(True)
        self.progress.hide()
        self.status_lbl.setText("Execution Finished! Report generated.")
        self.results_box.show()
        
        QMessageBox.information(self, "Test Finished", "TMX execution completed successfully.")

    def _view_report(self):
        if self.current_report and os.path.exists(self.current_report):
            webbrowser.open(f"file:///{self.current_report}")
        else:
            QMessageBox.critical(self, "Error", "Report file not found.")

    def _download_report(self):
        if not self.current_report_dir: return
        
        save_path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if save_path:
            zip_name = f"TMX_Report_{int(time.time())}"
            zip_full_path = os.path.join(save_path, zip_name)
            
            try:
                shutil.make_archive(zip_full_path, 'zip', self.current_report_dir)
                QMessageBox.information(self, "Success", f"Report archived and saved to {zip_full_path}.zip")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report: {e}")
