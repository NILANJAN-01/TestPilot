from core.context import get_context
from services.adb_wrapper import AdbWrapper
from PySide6.QtCore import QObject, Signal, QThread, QRunnable, QThreadPool
import subprocess
import time
import os

class LogcatThread(QThread):
    line_received = Signal(str)
    
    def __init__(self, serial, adb_path):
        super().__init__()
        self.serial = serial
        self.adb_path = adb_path
        self.running = True
        self.process = None
        
    def run(self):
        # adb -s <serial> logcat -v time
        cmd = [self.adb_path, "-s", self.serial, "logcat", "-v", "time"]
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1, # Line buffered
            creationflags=subprocess.CREATE_NO_WINDOW if subprocess.name == 'nt' else 0
        )
        
        while self.running and self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                self.line_received.emit(line)
            else:
                time.sleep(0.1)

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.kill()

class PerformanceThread(QThread):
    stats_received = Signal(dict)
    services_updated = Signal(list)
    
    def __init__(self, serial, adb):
        super().__init__()
        self.serial = serial
        self.adb = adb
        self.running = True
        
    def run(self):
        while self.running:
            try:
                # CPU (using top -n 1 is lighter and standard on Android)
                # Output format varies, simpler to use dumpsys cpuinfo if available, or just parsing /proc/stat
                # limit command execution for responsiveness
                
                # CPU Use top -n 1
                cpu_out = self.adb.shell_output(self.serial, "top -n 1 -m 5 -s cpu")
                # Extract a simple CPU summary (first line after header)
                cpu_summary = "N/A"
                lines = cpu_out.splitlines()
                for line in lines:
                    if line.strip().startswith("CPU") or line.strip().startswith("%CPU"):
                        cpu_summary = line.strip()
                        break
                # Simple Memory
                mem_out = self.adb.shell_output(self.serial, "dumpsys meminfo -c")
                
                # Battery/Thermal
                batt_out = self.adb.shell_output(self.serial, "dumpsys battery")
                
                # Android Services list
                services_out = self.adb.shell_output(self.serial, "service list")
                services_list = [s.strip() for s in services_out.splitlines() if s.strip()]
                
                stats = {
                    "cpu_raw": cpu_out,
                    "cpu_summary": cpu_summary,
                    "mem": self._parse_mem(mem_out),
                    "thermal": self._parse_thermal(batt_out),
                    "services": services_list
                }
                # Emit stats and services
                self.stats_received.emit(stats)
                self.services_updated.emit(services_list)
            except:
                pass
            
            # Sleep 2 seconds
            for _ in range(20):
                if not self.running: break
                time.sleep(0.1)

    def _parse_mem(self, output):
        # Very rough parsing of compact meminfo
        # ...
        return output[:100] # Return raw for now to display

    def _parse_thermal(self, output):
        for line in output.splitlines():
            if "temperature" in line:
                return line.strip()
        return "Unknown"

class DeviceToolService(QObject):
    log_received = Signal(str)
    perf_stats_updated = Signal(dict)
    screenshot_saved = Signal(str)
    recording_saved = Signal(str)
    
    # Fault Detection
    fault_detected = Signal(str, str) # Crash
    anr_detected = Signal(str) # ANR separate
    
    # Services Monitoring
    services_updated = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.ctx = get_context()
        self.adb = AdbWrapper() 
        self.log_thread = None
        self.perf_thread = None
        self.record_process = None
        
        self.fault_monitoring = False
        
    # --- Logging ---
    def start_logcat(self, serial):
        if self.log_thread: return
            
        self.log_thread = LogcatThread(serial, self.adb.adb_path)
        self.log_thread.line_received.connect(self._handle_log_line)
        self.log_thread.start()
        
    def stop_logcat(self):
        if self.log_thread:
            self.log_thread.stop()
            self.log_thread.wait()
            self.log_thread = None

    def clear_logcat(self, serial):
        self.adb.shell(serial, "logcat -c")
        
    def save_logs(self, content, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def _handle_log_line(self, line):
        self.log_received.emit(line)
        
        # Auto-Fault Capture Logic
        if self.fault_monitoring:
            if "FATAL EXCEPTION" in line:
                self.fault_detected.emit("CRASH", line)
            elif "ANR in" in line:
                self.anr_detected.emit(line)

    # --- Performance ---
    def start_monitoring(self, serial):
        if self.perf_thread: return
        self.perf_thread = PerformanceThread(serial, self.adb)
        self.perf_thread.stats_received.connect(self.perf_stats_updated)
        self.perf_thread.services_updated.connect(self.services_updated)
        self.perf_thread.start()
        
    def stop_monitoring(self):
        if self.perf_thread:
            self.perf_thread.running = False
            self.perf_thread.wait()
            self.perf_thread = None

    # --- Capture ---
    # --- Capture ---
    def take_screenshot(self, serial, local_path):
        worker = ScreenshotWorker(self.adb, serial, local_path)
        worker.signals.finished.connect(self.screenshot_saved)
        QThreadPool.globalInstance().start(worker)

class WorkerSignals(QObject):
    finished = Signal(str)

class ScreenshotWorker(QRunnable):
    def __init__(self, adb, serial, path):
        super().__init__()
        self.adb = adb
        self.serial = serial
        self.path = path
        self.signals = WorkerSignals()
        
    def run(self):
        remote = "/sdcard/temp_screenshot.png"
        self.adb.shell(self.serial, f"screencap -p {remote}")
        self.adb.pull(self.serial, remote, self.path)
        self.adb.shell(self.serial, f"rm {remote}")
        self.signals.finished.emit(self.path)

    # Recording
    def start_recording(self, serial, options=""):
        # options e.g. "--time-limit 180 --size 1280x720 --bit-rate 4000000"
        # We run this detached? Or keep track?
        # screenrecord blocks until done or interrupted. Use subprocess.
        cmd = [self.adb.adb_path, "-s", serial, "shell", "screenrecord", "/sdcard/temp_record.mp4"]
        if options:
            cmd.extend(options.split())
            
        # Non-blocking start
        self.record_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if subprocess.name == 'nt' else 0
        )
        
    def stop_recording(self, serial, local_path):
        if self.record_process:
            self.record_process.terminate()
            try:
                self.record_process.wait(timeout=2)
            except:
                self.record_process.kill()
            self.record_process = None
            
            # Use Worker for Pulling to avoid blocking UI
            worker = RecordingPullWorker(self.adb, serial, local_path)
            worker.signals.finished.connect(self.recording_saved)
            QThreadPool.globalInstance().start(worker)

class RecordingPullWorker(QRunnable):
    def __init__(self, adb, serial, path):
        super().__init__()
        self.adb = adb
        self.serial = serial
        self.path = path
        self.signals = WorkerSignals()
        
    def run(self):
        # Wait a sec for file close on device
        time.sleep(1)
        # Pull
        self.adb.pull(self.serial, "/sdcard/temp_record.mp4", self.path)
        self.adb.shell(self.serial, "rm /sdcard/temp_record.mp4")
        self.signals.finished.emit(self.path)
