import os
import sys
import subprocess
import shutil
import threading
from PySide6.QtCore import QObject, Signal

class RemoteControlService(QObject):
    """
    Service for managing desktop mirroring and remote interaction via scrcpy.
    Provides automatic discovery, cross-platform installation, and session management.
    """
    error_occurred = Signal(str)
    status_updated = Signal(str)
    session_started = Signal()
    session_ended = Signal()
    
    def __init__(self, adb_path="adb"):
        """
        Initialize the remote control service.
        :param adb_path: Path to the adb executable used for handshaking.
        """
        super().__init__()
        self.adb_path = adb_path
        self.scrcpy_path = self._find_scrcpy()
        self.process = None
        self.is_installing = False

    def _find_scrcpy(self):
        """
        Intelligently find scrcpy across Windows, Mac, and Linux.
        Checks system PATH, platform-specific install roots, and package manager paths (winget/snap).
        """
        # 1. System PATH
        path = shutil.which("scrcpy")
        if path: return path
        
        # 2. Platform-Specific Search
        if sys.platform == "win32":
            # Check Winget portable path pattern (Dynamic folder names)
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            winget_base = os.path.join(local_app_data, r"Microsoft\WinGet\Packages")
            if os.path.exists(winget_base):
                for folder in os.listdir(winget_base):
                    if "Genymobile.scrcpy" in folder:
                        pkg_dir = os.path.join(winget_base, folder)
                        for root, _, files in os.walk(pkg_dir):
                            if "scrcpy.exe" in files:
                                return os.path.join(root, "scrcpy.exe")
            # Common install locations
            for p in [r"C:\Program Files\scrcpy\scrcpy.exe", r"C:\scrcpy\scrcpy.exe"]:
                if os.path.exists(p): return p
        else:
            # Unix-like common paths (Homebrew, Snaps, Apt)
            for p in ["/usr/local/bin/scrcpy", "/usr/bin/scrcpy", "/opt/homebrew/bin/scrcpy", "/snap/bin/scrcpy"]:
                if os.path.exists(p): return p
        
        return None

    def start_mirroring(self, serial):
        """
        Start a new mirroring session for the given device serial.
        If scrcpy is missing, it triggers the automatic background installer.
        """
        if self.is_installing:
            self.status_updated.emit("Installation is already in progress...")
            return

        # Always re-check in case it was installed manually since boot
        self.scrcpy_path = self._find_scrcpy()
        
        if not self.scrcpy_path:
            self.status_updated.emit("scrcpy not found. Starting automatic setup...")
            threading.Thread(target=self._auto_install_and_run, args=(serial,), daemon=True).start()
            return

        self._launch_scrcpy(serial)

    def _launch_scrcpy(self, serial):
        """
        Fork a scrcpy process with specific optimizations for AAOS (1024m limit, 4M bitrate).
        Includes permission fixes for Windows 'Access Denied' errors.
        """
        def run():
            try:
                self.status_updated.emit("Handshaking with device...")
                
                # Check device responsiveness before spawning
                adb_bin = shutil.which(self.adb_path) or self.adb_path
                res = subprocess.run([adb_bin, "-s", serial, "shell", "echo", "1"], capture_output=True, timeout=5)
                if res.returncode != 0:
                    self.error_occurred.emit(f"Device {serial} is not responding to ADB.")
                    return

                cmd = [self.scrcpy_path, "-s", serial, "--window-title", f"TestPilot Remote: {serial}"]
                cmd.extend(["-m", "1024", "-b", "4M", "--max-fps", "30", "--always-on-top"])
                
                # Inherit environment and bypass permission issues by passing host ADB path
                env = os.environ.copy()
                env["ADB"] = adb_bin
                scrcpy_dir = os.path.dirname(self.scrcpy_path)

                print(f"[RemoteSvc] Launching: {' '.join(cmd)}")
                self.process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True,
                    env=env,
                    cwd=scrcpy_dir
                )
                
                # Real-time success detection from scrcpy logs
                for line in self.process.stdout:
                    msg = line.strip()
                    print(f"[scrcpy] {msg}")
                    if "CONNECTED" in msg.upper():
                        self.status_updated.emit("Mirroring active.")
                        self.session_started.emit()
                    if "ERROR:" in msg.upper() or "FATAL:" in msg.upper():
                        self.error_occurred.emit(f"scrcpy error: {msg}")

                self.process.wait()
                self.session_ended.emit()
                if self.process.returncode != 0 and self.process.returncode != -1:
                    self.error_occurred.emit(f"Session ended (Code: {self.process.returncode})")
                    
            except Exception as e:
                self.error_occurred.emit(f"Mirroring failed: {str(e)}")

        threading.Thread(target=run, daemon=True).start()

    def _auto_install_and_run(self, serial):
        """
        Cross-platform background installer. 
        Supports winget (Win), homebrew (Mac), and apt/snap (Linux).
        """
        self.is_installing = True
        success = False
        platform = sys.platform
        
        try:
            if platform == "win32":
                self.status_updated.emit("Windows: Installing via winget...")
                cmd = ["winget", "install", "Genymobile.scrcpy", "--silent", "--accept-package-agreements", "--accept-source-agreements"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                success = res.returncode == 0 or "already installed" in res.stdout
            elif platform == "darwin":
                self.status_updated.emit("MacOS: Installing via Homebrew...")
                if not shutil.which("brew"):
                    self.error_occurred.emit("Homebrew not found. Please install manually.")
                    return
                res = subprocess.run(["brew", "install", "scrcpy"], capture_output=True)
                success = res.returncode == 0
            elif platform == "linux":
                self.status_updated.emit("Linux: Attempting apt/snap install...")
                cmd = "sudo apt-get update && sudo apt-get install -y scrcpy || sudo snap install scrcpy"
                res = subprocess.run(cmd, shell=True, capture_output=True)
                success = res.returncode == 0
            
            if success:
                self.scrcpy_path = self._find_scrcpy()
                if self.scrcpy_path:
                    self.status_updated.emit("Success! Starting mirroring...")
                    self._launch_scrcpy(serial)
                else:
                    self.error_occurred.emit("Installation finished but path refresh failed.")
            else:
                self.error_occurred.emit("Auto-install failed. Please install scrcpy manually.")
                
        except Exception as e:
            self.error_occurred.emit(f"Installer error: {str(e)}")
        finally:
            self.is_installing = False

    def stop_mirroring(self):
        """Terminate the active mirroring session."""
        if self.process:
            self.process.terminate()
            self.process = None
