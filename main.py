import sys
import traceback
from PySide6.QtWidgets import QApplication
from core.context import get_context
from core.window_manager import WindowManager
from ui_main_window import MainWindow
from services.device_manager import DeviceManager

from core.config import APP_NAME, VERSION

def main():
    print(f"Initializing {APP_NAME} {VERSION} Core...")
    try:
        app = QApplication(sys.argv)
        
        # Initialize Context & Services
        ctx = get_context()
        ctx.register_service("device_manager", DeviceManager())
    
        from services.device_tool_service import DeviceToolService
        ctx.register_service("tool_service", DeviceToolService())
        
        from services.automation_service import AutomationService
        ctx.register_service("automation", AutomationService())

        from services.remote_control_service import RemoteControlService
        ctx.register_service("remote_control", RemoteControlService())
        
        from services.stability_service import StabilityService
        ctx.register_service("stability", StabilityService(ctx.get_service("device_manager").adb))
        
        # Window Manager handling the UI scaling
        wm = WindowManager(MainWindow)
        
        print("Launching Main Window...")
        main_win = wm.new_window()
        
        # Crash Handling / Exception Hook
        sys.excepthook = handle_exception
        
        exit_code = app.exec()
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"CRITICAL BOOT FAILURE: {e}")
        traceback.print_exc()

def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global crash handler to ensure user sees errors instead of silent crashes.
    Futuristic: Log to cloud or local analytics.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    print("Uncaught Exception:", exc_value)
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    # In a real app, show a dialog here so the user knows what happened.

if __name__ == "__main__":
    main()
