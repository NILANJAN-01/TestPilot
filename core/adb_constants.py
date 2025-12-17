class AdbCommands:
    # Identity
    SERIAL = "getprop ro.serialno"
    MODEL = "getprop ro.product.model"
    MANUFACTURER = "getprop ro.product.manufacturer"
    BOARD = "getprop ro.board.platform"
    ABI = "getprop ro.product.cpu.abi"
    HARDWARE_REV = "getprop ro.boot.hardware.revision"
    
    # Software
    ANDROID_VER = "getprop ro.build.version.release"
    SDK_LEVEL = "getprop ro.build.version.sdk"
    BUILD_FINGERPRINT = "getprop ro.build.fingerprint"
    BUILD_ID = "getprop ro.build.id"
    KERNEL = "uname -r"
    SECURITY_PATCH = "getprop ro.build.version.security_patch"
    
    # Runtime
    BOOT_COMPLETED = "getprop sys.boot_completed"
    UPTIME = "uptime -p"
    
    # Security
    SELINUX = "getenforce"
    DEBUGGABLE = "getprop ro.debuggable"
    VERIFIED_BOOT = "getprop ro.boot.verifiedbootstate"
    
    # IO
    DISPLAY_SIZE = "wm size"
    DISPLAY_DENSITY = "wm density"
    
    # Region
    TIMEZONE = "getprop persist.sys.timezone"
    LOCALE = "getprop persist.sys.locale"
    SYSTEM_TIME = "date" # Full date string

    # Automotive
    CAR_CHARACTERISTICS = "getprop ro.build.characteristics" # check for 'automotive'
    VHAL_CHECK = "lshal | grep -i IVehicle" # Check existence
    
    # Storage
    DF_DATA = "df -h /data"

    # Media
    MEDIA_PLAY_PAUSE = "input keyevent 85"
    MEDIA_STOP = "input keyevent 86"
    MEDIA_NEXT = "input keyevent 87"
    MEDIA_PREV = "input keyevent 88"
    MEDIA_FF = "input keyevent 90"
    MEDIA_REWIND = "input keyevent 89"
    VOLUME_UP = "input keyevent 24"
    VOLUME_DOWN = "input keyevent 25"
    MUTE = "input keyevent 164"
    
    # Connectivity
    WIFI_ENABLE = "cmd wifi set-wifi-enabled enabled"
    WIFI_DISABLE = "cmd wifi set-wifi-enabled disabled"
    WIFI_STATUS = "settings get global wifi_on" # 0 or 1
    WIFI_SCAN = "cmd wifi start-scan"
    WIFI_LIST = "cmd wifi list-scan-results"
    WIFI_CONNECT = "cmd wifi connect-network" # <ssid> <type> <password>
    
    
    BT_ENABLE = "cmd bluetooth_manager enable"
    BT_DISABLE = "cmd bluetooth_manager disable"
    BT_STATUS = "settings get global bluetooth_on"
    
    # App Lifecycle
    LAUNCH_HOME = "input keyevent 3"
    FORCE_STOP = "am force-stop" 
    CLEAR_DATA = "pm clear"
    
    # Tools: Capture
    SCREENCAP = "screencap -p" # > /sdcard/s.png
    SCREENRECORD = "screenrecord" # options: --time-limit --size --bit-rate
    
    # Tools: Logging
    LOGCAT = "logcat" 
    LOGCAT_CLEAR = "logcat -c"
    
    # Tools: Performance
    DUMPSYS_CPU = "dumpsys cpuinfo"
    DUMPSYS_MEM = "dumpsys meminfo"
    # PROC_STAT = "cat /proc/stat" # Lighter weight for live graphs

    
    # Power
    POWER_BTN = "input keyevent 26"
    SLEEP = "input keyevent 223"
    WAKE = "input keyevent 224"
    REBOOT = "reboot"
    SOFT_REBOOT = "setprop ctl.restart zygote"
    
    # Auto Specific (Mock IDs for POC)
    IGNITION_ON = "cmd car_service inject-vhal-event 0x11400400 4" 
    IGNITION_OFF = "cmd car_service inject-vhal-event 0x11400400 1"

    @staticmethod
    def get_all_props_command():
        # Optimization: Fetch all props at once and parse? 
        # Or Just batch common ones.
        return "getprop"
