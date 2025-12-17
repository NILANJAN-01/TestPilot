from PySide6.QtCore import QObject, Signal, QThreadPool

class EventBus(QObject):
    """
    Central Event Bus for decoupled communication between components.
    Futuristic & Scalable: Allows modules to talk without direct dependencies.
    """
    # Define generic signals here or use dynamic dispatch
    # For robust typing, we define common signals
    device_connected = Signal(str) # device_id
    device_disconnected = Signal(str)
    log_message = Signal(str, str) # level, message
    command_requested = Signal(str, dict) # command_name, params

    def __init__(self):
        super().__init__()

class AppContext(QObject):
    """
    Singleton-like container for global application state and services.
    Ensures scalability by providing a single source of truth.
    """
    def __init__(self):
        super().__init__()
        self.event_bus = EventBus()
        self.thread_pool = QThreadPool.globalInstance()
        self.active_windows = []
        self.services = {}

    def register_service(self, name, service):
        self.services[name] = service

    def get_service(self, name):
        return self.services.get(name)

# Global Instance
_app_context = AppContext()

def get_context():
    return _app_context
