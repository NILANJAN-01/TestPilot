from services.adb_wrapper import AdbWrapper
from core.adb_constants import AdbCommands
import re

class DeviceInfoGatherer:
    """
    Highly granular information engine for extracting device metadata.
    Categorizes results into Identity, Software, Automotive, Runtime, etc.
    Designed for AAOS (Android Automotive OS) but backwards compatible with standard Android.
    """
    def __init__(self, adb_wrapper: AdbWrapper):
        """
        :param adb_wrapper: Shared AdbWrapper instance for shell communication.
        """
        self.adb = adb_wrapper

    def gather_full_info(self, serial):
        """
        Executes a series of ADB shell commands (getprop, wm, dumpsys) 
        to build a comprehensive report of the target device.
        :param serial: Device serial number.
        :return: Nested dictionary of device properties.
        """
        if not serial: return None

        info = {
            "Identity": {},
            "Software": {},
            "Automotive": {},
            "Runtime": {},
            "Storage": {},
            "Security": {},
            "InputOutput": {},
            "Region": {}
        }

        # Identity Category
        info["Identity"]["Serial"] = self._get(serial, AdbCommands.SERIAL)
        info["Identity"]["Model"] = self._get(serial, AdbCommands.MODEL)
        info["Identity"]["Manufacturer"] = self._get(serial, AdbCommands.MANUFACTURER)
        info["Identity"]["Board/SoC"] = self._get(serial, AdbCommands.BOARD)
        info["Identity"]["ABI"] = self._get(serial, AdbCommands.ABI)
        info["Identity"]["Hardware Rev"] = self._get(serial, AdbCommands.HARDWARE_REV)

        # Software Category
        info["Software"]["Android Ver"] = self._get(serial, AdbCommands.ANDROID_VER)
        info["Software"]["SDK Level"] = self._get(serial, AdbCommands.SDK_LEVEL)
        info["Software"]["Build ID"] = self._get(serial, AdbCommands.BUILD_ID)
        info["Software"]["Kernel"] = self._get(serial, AdbCommands.KERNEL)
        info["Software"]["Security Patch"] = self._get(serial, AdbCommands.SECURITY_PATCH)
        
        # Runtime Category (Uptime, Memory)
        info["Runtime"]["Boot Completed"] = "Yes" if self._get(serial, AdbCommands.BOOT_COMPLETED) == "1" else "No"
        uptime = self._get(serial, AdbCommands.UPTIME)
        info["Runtime"]["Uptime"] = uptime if uptime else "Unknown"
        
        mem_out = self._get(serial, "cat /proc/meminfo | grep MemTotal") 
        info["Runtime"]["Total Memory"] = mem_out.replace("MemTotal:", "").strip()

        # Automotive Category (AAOS Specifics)
        characteristics = self._get(serial, AdbCommands.CAR_CHARACTERISTICS)
        is_automotive = "automotive" in characteristics
        info["Automotive"]["Is Automotive?"] = "Yes" if is_automotive else "No"
        
        if is_automotive:
            # Check for Vehicle HAL (VHAL) presence
            vhal = self._get(serial, "lshal | grep -m 1 IVehicle")
            if "android.hardware.automotive.vehicle" in vhal:
                info["Automotive"]["VHAL State"] = "Running"
            else:
                info["Automotive"]["VHAL State"] = "Unknown/Hidden"
        else:
            info["Automotive"]["Note"] = "Not an AAOS Build"

        # Storage Category (Data partition analysis)
        df_out = self._get(serial, AdbCommands.DF_DATA)
        try:
            lines = df_out.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    info["Storage"]["User Data Total"] = parts[1]
                    info["Storage"]["User Data Free"] = parts[3]
                    info["Storage"]["Usage"] = parts[4]
        except:
            info["Storage"]["Status"] = "Unable to read /data"

        # Security Category
        info["Security"]["SELinux"] = self._get(serial, AdbCommands.SELINUX)
        info["Security"]["Rooted"] = "Yes" if "root" in self._get(serial, "whoami") else "No"
        info["Security"]["Debuggable"] = "Yes" if self._get(serial, AdbCommands.DEBUGGABLE) == "1" else "No"

        # Region & Global Category
        info["Region"]["Timezone"] = self._get(serial, AdbCommands.TIMEZONE)
        info["Region"]["Locale"] = self._get(serial, AdbCommands.LOCALE)
        info["Region"]["Device Time"] = self._get(serial, AdbCommands.SYSTEM_TIME)
        
        # Display & IO Category
        info["InputOutput"]["Resolution"] = self._get(serial, AdbCommands.DISPLAY_SIZE).replace("Physical size: ", "")
        info["InputOutput"]["Density"] = self._get(serial, AdbCommands.DISPLAY_DENSITY).replace("Physical density: ", "")

        return info

    def _get(self, serial, cmd):
        # cmd is like "getprop xxx" or "wm size"
        # wrapper.shell takes (serial, command_string)
        # Extract command parts if needed? No, shell takes string.
        out, _, _ = self.adb.shell(serial, cmd)
        return out.strip()
