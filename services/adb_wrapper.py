import subprocess
import shutil

class AdbWrapper:
    """
    A robust wrapper around the Android Debug Bridge (ADB) CLI.
    Handles device communication, activity querying, and shell command execution
    with cross-platform safe encoding (UTF-8).
    """
    def __init__(self, adb_path="adb"):
        """
        Initialize the wrapper.
        :param adb_path: Path to the adb executable. Defaults to 'adb' from PATH.
        """
        self.adb_path = shutil.which(adb_path) or adb_path
    
    def _run(self, args, timeout=10):
        """
        Execution engine for all ADB commands.
        Uses subprocess.run with specific error handling for binary/weird outputs.
        """
        try:
            cmd = [self.adb_path] + args
            
            # Windows specific: suppress console flash and improve stability in GUI
            kwargs = {
                "capture_output": True,
                "text": True,
                "timeout": timeout,
                "encoding": 'utf-8',
                "errors": 'replace'
            }
            if sys.platform == "win32":
                import subprocess
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            result = subprocess.run(cmd, **kwargs)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            return "", str(e), -1

    def get_devices(self):
        """
        Fetch all currently connected Android devices.
        :return: List of serial strings (e.g., ['emulator-5554']).
        """
        out, err, code = self._run(["devices"])
        if code != 0:
            return []
        
        devices = []
        lines = out.split('\n')
        for line in lines[1:]: # Skip header
            if "\tdevice" in line:
                devices.append(line.split("\t")[0])
        return devices

    def pull(self, serial, remote, local):
        """
        Download a file from the device to the local system.
        """
        return self._run(["-s", serial, "pull", remote, local])

    def install(self, serial, apk_path):
        """
        Install an APK onto the target device.
        :param apk_path: Absolute path to the .apk file on host.
        """
        return self._run(["-s", serial, "install", "-r", apk_path], timeout=60)
        
    def shell(self, serial, command):
        """
        Run a command in the device's shell.
        :return: (stdout, stderr, return_code)
        """
        return self._run(["-s", serial, "shell", command])

    def shell_output(self, serial, command):
        """
        Run a shell command and return only the standard output.
        """
        out, _, _ = self.shell(serial, command)
        return out

    def reboot(self, serial):
        """Reboot the target device."""
        return self._run(["-s", serial, "reboot"])

    def enable_root(self, serial):
        """
        Attempts to restart adbd with root permissions.
        Requires a user-debug or rooted build.
        """
        return self._run(["-s", serial, "root"])

    def is_screen_on(self, serial):
        """
        Check if the device screen is currently active/on.
        Useful for automating wake-up sequences.
        """
        out = self.shell_output(serial, "dumpsys display | grep 'mDisplayState' || dumpsys power | grep 'mHoldingDisplay'")
        if "ON" in out.upper() or "TRUE" in out.lower():
            return True
        return False

    def get_launchable_activities(self, serial):
        """
        Extract all launchable application activities from the device.
        Used for populating stability check selection.
        """
        cmd = "cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER"
        out = self.shell_output(serial, cmd)
        
        results = []
        for line in out.splitlines():
            if "/" in line:
                results.append(line.strip())
        return sorted(list(set(results)))

    def get_resumed_activity(self, serial):
        """
        Identify the activity currently in the foreground (resumed).
        Crucial for verifying app launch status.
        """
        cmd = "dumpsys activity activities | grep mResumedActivity"
        out = self.shell_output(serial, cmd)
        if "/" in out:
            parts = out.split()
            for p in parts:
                if "/" in p:
                    # Clean up braces from ActivityRecord format
                    return p.strip("{}")
        return ""
