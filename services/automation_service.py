import os
import subprocess
import threading
from PySide6.QtCore import QObject, Signal, QThread
import robot

class AutomationWorker(QThread):
    finished = Signal(str, str) # Report path, output directory

    def __init__(self, serial, test_file, output_dir):
        super().__init__()
        self.serial = serial
        self.test_file = test_file
        self.output_dir = output_dir

    def run(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Run robot
        # We pass the serial as a variable to the test suite
        robot.run(
            self.test_file,
            outputdir=self.output_dir,
            variable=[f"SERIAL:{self.serial}"],
            loglevel="INFO"
        )
        
        report_path = os.path.join(self.output_dir, "report.html")
        self.finished.emit(report_path, self.output_dir)

class AutomationService(QObject):
    automation_finished = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.current_worker = None

    def run_tmx_test(self, serial, test_name):
        # Map friendly name to file
        suites = {
            "TMX_FULL: System Health Check (15 Tests)": "system_health.robot",
            "TMX_UI: Core Interaction & Navigation": "ui_interaction.robot",
            "TMX_CORE: Basic Boot & Services": "system_health.robot", # Could use tags later
        }
        
        filename = suites.get(test_name, "system_health.robot")
        test_file = os.path.join(os.getcwd(), "automation", "tests", filename)
        output_dir = os.path.join(os.getcwd(), "automation", "reports", f"run_{int(time.time())}")
        
        self.current_worker = AutomationWorker(serial, test_file, output_dir)
        self.current_worker.finished.connect(self._on_finished)
        self.current_worker.start()

    def _on_finished(self, report_path, output_dir):
        self.automation_finished.emit(report_path, output_dir)
        self.current_worker = None

import time
