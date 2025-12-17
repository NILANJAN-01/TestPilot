from services.adb_wrapper import AdbWrapper
from core.adb_constants import AdbCommands
import time

class DeviceController:
    """
    Orchestrator for hardware and software control commands via ADB.
    Provides abstract methods for common interactions like volume control, 
    connectivity toggles, and application lifecycle management.
    """
    def __init__(self, adb_wrapper: AdbWrapper):
        """
        :param adb_wrapper: Shared AdbWrapper instance.
        """
        self.adb = adb_wrapper

    def _exec(self, serial, cmd):
        """Internal helper for standard shell execution."""
        if not serial: return
        self.adb.shell(serial, cmd)

    # --- Media Execution ---
    def media_play_pause(self, serial): self._exec(serial, AdbCommands.MEDIA_PLAY_PAUSE)
    def media_next(self, serial): self._exec(serial, AdbCommands.MEDIA_NEXT)
    def media_prev(self, serial): self._exec(serial, AdbCommands.MEDIA_PREV)
    def media_stop(self, serial): self._exec(serial, AdbCommands.MEDIA_STOP)
    def volume_up(self, serial): self._exec(serial, AdbCommands.VOLUME_UP)
    def volume_down(self, serial): self._exec(serial, AdbCommands.VOLUME_DOWN)
    
    # --- Connectivity Toggles ---
    def set_wifi(self, serial, enable: bool):
        """Enable or disable WiFi radio."""
        cmd = AdbCommands.WIFI_ENABLE if enable else AdbCommands.WIFI_DISABLE
        self._exec(serial, cmd)

    def is_wifi_on(self, serial):
        """Query state of WiFi radio."""
        out, _, _ = self.adb.shell(serial, AdbCommands.WIFI_STATUS)
        return "1" in out

    def connect_wifi(self, serial, ssid, password):
        """Attempts to connect to a specific SSID with WPA2 security."""
        net_type = "wpa2" if password else "open"
        cmd = f'{AdbCommands.WIFI_CONNECT} "{ssid}" {net_type} "{password}"'
        self._exec(serial, cmd)
    
    def scan_wifi(self, serial):
        """Triggers a background WiFi scan."""
        self._exec(serial, AdbCommands.WIFI_SCAN)
        
    def get_wifi_networks(self, serial):
        """Parses scan results into a list of network identifiers."""
        out, _, _ = self.adb.shell(serial, AdbCommands.WIFI_LIST)
        networks = []
        lines = out.split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) > 3:
                networks.append(line.strip())
        return networks

    def set_bt(self, serial, enable: bool):
        """Enable or disable Bluetooth radio."""
        cmd = AdbCommands.BT_ENABLE if enable else AdbCommands.BT_DISABLE
        self._exec(serial, cmd)

    def is_bt_on(self, serial):
        """Query state of Bluetooth radio."""
        out, _, _ = self.adb.shell(serial, AdbCommands.BT_STATUS)
        return "1" in out

    # --- Application Lifecycle Management ---
    def launch_home(self, serial):
        """Force navigation back to the Launcher Home."""
        self._exec(serial, AdbCommands.LAUNCH_HOME)
        
    def force_stop(self, serial, pkg):
        """Kill a target package immediately."""
        self.adb.shell(serial, f"{AdbCommands.FORCE_STOP} {pkg}")
        
    def clear_data(self, serial, pkg):
        """Wipe application data for the target package."""
        self.adb.shell(serial, f"{AdbCommands.CLEAR_DATA} {pkg}")

    # --- Power & System ---
    def power_btn(self, serial): 
        """Simulate a physical power button press."""
        self._exec(serial, AdbCommands.POWER_BTN)
        
    def reboot(self, serial): 
        """Trigger a full system reboot."""
        self.adb.reboot(serial)
    
    # --- Automotive Specific Controls ---
    def ignition(self, serial, on: bool):
        """Simulate Vehicle Ignition state (CAR_POWER_STATE change)."""
        cmd = AdbCommands.IGNITION_ON if on else AdbCommands.IGNITION_OFF
        self._exec(serial, cmd)
