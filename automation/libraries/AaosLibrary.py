import os
import time
import subprocess
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

class AaosLibrary:
    """Robot Framework library for AAOS Test Automation."""
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, adb_path="adb"):
        self.adb_path = adb_path
        self._serial = None

    def set_device_serial(self, serial):
        self._serial = serial

    def _run_adb(self, cmd_list):
        full_cmd = [self.adb_path]
        if self._serial:
            full_cmd.extend(["-s", self._serial])
        full_cmd.extend(cmd_list)
        try:
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"ADB Command failed: {e}")
            return ""

    def launch_app(self, package_name):
        """Launches the specified app package."""
        logger.info(f"Launching app: {package_name}")
        self._run_adb(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
        time.sleep(2)

    def click_text(self, text):
        """Finds the coordinates of a text using uiautomator dump and clicks it."""
        logger.info(f"Clicking on text: {text}")
        dump = self._run_adb(["shell", "uiautomator", "dump", "/sdcard/view.xml"])
        if "Dumped to" not in dump:
            # Fallback for some systems
            self._run_adb(["shell", "uiautomator", "dump", "--compressed", "/sdcard/view.xml"])
        
        xml_content = self._run_adb(["shell", "cat", "/sdcard/view.xml"])
        
        # Simple regex/parsing for bounds="[x1,y1][x2,y2]"
        import re
        pattern = f'text="{text}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"'
        match = re.search(pattern, xml_content)
        
        if match:
            x1, y1, x2, y2 = map(int, match.groups())
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            self._run_adb(["shell", "input", "tap", str(cx), str(cy)])
            return True
        else:
            logger.warn(f"Text '{text}' not found on screen")
            return False

    def check_system_property(self, prop_name):
        """Returns the value of a system property."""
        val = self._run_adb(["shell", "getprop", prop_name])
        logger.info(f"Property {prop_name}: {val}")
        return val

    def get_service_status(self, service_name):
        """Checks if a service is running using dumpsys."""
        out = self._run_adb(["shell", "dumpsys", service_name])
        if "Service not found" in out:
            return "NOT_FOUND"
        return "RUNNING"

    def take_screenshot_on_failure(self, filename=None):
        """Captures a screenshot and embeds it in the Robot report."""
        if not self._serial: return
        
        # Determine unique filename based on test name
        test_name = BuiltIn().get_variable_value("${TEST NAME}", "failure").replace(" ", "_")
        if not filename:
            filename = f"screenshot_{test_name}_{int(time.time())}.png"
            
        out_dir = BuiltIn().get_variable_value("${OUTPUT DIR}", ".")
        local_path = os.path.join(out_dir, filename)
        
        self._run_adb(["shell", "screencap", "-p", "/sdcard/ss.png"])
        self._run_adb(["pull", "/sdcard/ss.png", local_path])
        
        # Embed in Robot report
        logger.info(f'<b>Failure Screenshot:</b><br><a href="{filename}"><img src="{filename}" width="600px"></a>', html=True)

    def dump_logs(self, filename=None):
        """Dumps logcat to a file and links it in the report."""
        test_name = BuiltIn().get_variable_value("${TEST NAME}", "failure").replace(" ", "_")
        if not filename:
            filename = f"logs_{test_name}_{int(time.time())}.txt"

        out_dir = BuiltIn().get_variable_value("${OUTPUT DIR}", ".")
        local_path = os.path.join(out_dir, filename)
        
        logs = self._run_adb(["logcat", "-d"])
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(logs)
        
        logger.info(f'<a href="{filename}" target="_blank">View/Download Failure Logcat (TXT)</a>', html=True)

    def swipe(self, x1, y1, x2, y2, duration=300):
        """Swipes from point A to point B."""
        logger.info(f"Swiping from ({x1}, {y1}) to ({x2}, {y2})")
        self._run_adb(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

    def input_text_into_ui(self, text):
        """Inputs text using adb shell input text."""
        # Replace spaces with %s for adb
        processed_text = text.replace(" ", "%s")
        logger.info(f"Inputting text: {text}")
        self._run_adb(["shell", "input", "text", processed_text])

    def press_key(self, keycode):
        """Presses a system key (e.g. HOME, BACK, APP_SWITCH)."""
        logger.info(f"Pressing key: {keycode}")
        self._run_adb(["shell", "input", "keyevent", keycode])

    def wait_until_text_exists(self, text, timeout=10):
        """Waits until a specific text appears on screen."""
        logger.info(f"Waiting for text: {text}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.verify_text_exists(text):
                return True
            time.sleep(1)
        raise Exception(f"Timeout waiting for text: {text}")

    def verify_text_exists(self, text):
        """Returns True if text is found in uiautomator dump."""
        self._run_adb(["shell", "uiautomator", "dump", "/sdcard/view.xml"])
        xml_content = self._run_adb(["shell", "cat", "/sdcard/view.xml"])
        return f'text="{text}"' in xml_content or f'content-desc="{text}"' in xml_content
