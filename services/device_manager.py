from core.context import get_context
from PySide6.QtCore import QObject, Signal, QTimer
from services.adb_wrapper import AdbWrapper

class BaseService(QObject):
    """
    Base class for all application services.
    Provides shared access to the global Context and Event Bus.
    """
    def __init__(self):
        super().__init__()
        self.ctx = get_context()
        self.bus = self.ctx.event_bus

from services.device_info_gatherer import DeviceInfoGatherer
from services.device_controller import DeviceController
from core.worker import Worker
from PySide6.QtCore import QThreadPool

class DeviceManager(BaseService):
    """
    The central intelligence for Android device management.
    Lifecycle:
    1. Polling: Uses QTimer to monitor connected hardware via ADB.
    2. Eventing: Emits signals for connection, disconnection, and property updates.
    3. Delegation: Uses Gatherer for deep-info and Controller for shell actions.
    4. Threading: Offloads persistent tasks to QThreadPool using Worker instances.
    """
    devices_updated = Signal(list) 
    device_disconnected = Signal() 
    device_props_ready = Signal(dict)
    notification = Signal(str, str) # message, type (info, warn, error)

    def __init__(self):
        """
        Initialize the manager and start the auto-polling cycle (3s intervals).
        """
        super().__init__()
        self.adb = AdbWrapper()
        self.gatherer = DeviceInfoGatherer(self.adb)
        self.controller = DeviceController(self.adb)
        self.connected_devices = []
        self.thread_pool = QThreadPool()
        
        # Auto-poll for devices
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.scan_devices)
        self.timer.start(3000)
        
        self.scan_devices()

    def scan_devices(self):
        """
        Poll ADB for a fresh device list. 
        Detects changes and alerts the UI via signals/notifications.
        """
        current_devices = self.adb.get_devices()
        
        if not current_devices:
            if self.connected_devices:
                self.device_disconnected.emit()
                self.notification.emit("No ADB devices connected!", "error")
            self.connected_devices = []
            return

        if current_devices != self.connected_devices:
            self.connected_devices = current_devices
            self.devices_updated.emit(self.connected_devices)
            
            # Check screen state on new connection to alert user
            serial = self.connected_devices[0]
            if not self.adb.is_screen_on(serial):
                self.notification.emit(f"Device [{serial}] screen is OFF. Please turn on the display.", "warn")

    def get_first_device(self):
        """Helper to get the serial of the primary (first listed) device."""
        if self.connected_devices:
            return self.connected_devices[0]
        return None

    def reboot_device(self, serial=None):
        """
        Trigger a device reboot in a background thread.
        """
        target = serial or self.get_first_device()
        if target:
            worker = Worker(self.adb.reboot, target)
            self.thread_pool.start(worker)
        else:
            self.device_disconnected.emit()

    def fetch_device_props(self, serial=None):
        """
        Launch an asynchronous background gathering task for full system properties (build, manufacturer, etc).
        Returns results via device_props_ready signal.
        """
        target = serial or self.get_first_device()
        if not target: 
            return
        
        worker = Worker(self.gatherer.gather_full_info, target)
        worker.signals.result.connect(self._on_props_fetched)
        self.thread_pool.start(worker)

    def _on_props_fetched(self, result):
        """Slot for handling async property results."""
        if result:
            self.device_props_ready.emit(result)

    def get_device_props(self, serial=None):
        """
        (Blocking) Synchronous fetch of device info. 
        Use fetch_device_props for UI-safe calls.
        """
        target = serial or self.get_first_device()
        if not target: 
            return {}
        return self.gatherer.gather_full_info(target)
