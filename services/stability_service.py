import time
import threading
from PySide6.QtCore import QObject, Signal
import os

class StabilityService(QObject):
    """
    Service for stress-testing application stability (System Stability Check).
    Executes a loop of app launches, focus verifications, and real-time crash monitoring.
    """
    status_updated = Signal(str) 
    progress_updated = Signal(int, int) # loop_index, total_loops
    iteration_started = Signal(str) # activity_name
    issue_detected = Signal(str, str) # type (ANR/CRASH), details
    finished = Signal()

    def __init__(self, adb):
        """
        :param adb: Initialized AdbWrapper instance.
        """
        super().__init__()
        self.adb = adb
        self.is_running = False
        self._stop_event = threading.Event()

    def start_test(self, serial, apps, loops):
        """
        Initiate the stability test loop in a background thread.
        :param serial: Target device serial.
        :param apps: List of activity strings (pkg/act) to test.
        :param loops: Total repetitions.
        """
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        thread = threading.Thread(
            target=self._run_loop, 
            args=(serial, apps, loops), 
            daemon=True
        )
        thread.start()

    def stop_test(self):
        """Request a graceful stop of the active test loop."""
        self._stop_event.set()
        self.is_running = False
        self.status_updated.emit("Stability test stopping...")

    def _run_loop(self, serial, apps, loops):
        """
        Internal loop Runner. 
        Iterates through apps, cleans logs, launches, and performs focus verification.
        """
        try:
            for loop in range(1, loops + 1):
                if self._stop_event.is_set():
                    break
                
                self.progress_updated.emit(loop, loops)
                self.status_updated.emit(f"Starting Loop {loop}/{loops}")
                
                for app in apps:
                    if self._stop_event.is_set():
                        break
                    
                    self.iteration_started.emit(app)
                    self.status_updated.emit(f"Launching {app}...")
                    
                    # Fresh logcat for this iteration
                    self.adb.shell(serial, "logcat -c")
                    
                    # Trigger launch
                    self.adb.shell(serial, f"am start -n {app}")
                    
                    # Dwell time for the app to initialize
                    time.sleep(3)
                    
                    # Verify focus
                    resumed = self.adb.get_resumed_activity(serial)
                    if app in resumed:
                        self.status_updated.emit(f"Verified: {app} is in focus.")
                    else:
                        self.status_updated.emit(f"Warning: Unexpected focus (Current: {resumed})")
                    
                    # Check for failures
                    self._check_logs(serial, app)
                    
                    time.sleep(2)
            
            self.status_updated.emit("Stability test completed.")
        except Exception as e:
            self.status_updated.emit(f"Test Error: {str(e)}")
        finally:
            self.is_running = False
            self.finished.emit()

    def _check_logs(self, serial, app):
        """
        Heuristic check for Fatal Exceptions or ANRs in logcat/dumpsys.
        """
        pkg = app.split('/')[0]
        # Query for high-priority errors in the main/crash buffers
        logs = self.adb.shell_output(serial, f"logcat -d *:E | grep {pkg}")
        
        if "FATAL EXCEPTION" in logs.upper():
            self.issue_detected.emit("CRASH", f"Fatal detected in {pkg}:\n{logs[:1000]}")
        
        # Poll for ANR states via process state dump
        anr_check = self.adb.shell_output(serial, "dumpsys activity processes | grep 'ANR in'")
        if pkg in anr_check:
            self.issue_detected.emit("ANR", f"ANR condition confirmed for {pkg}!")

    def get_apps(self, serial):
        """Fetch list of all launchable activities via ADB."""
        return self.adb.get_launchable_activities(serial)
