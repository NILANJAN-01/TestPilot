from core.context import get_context
from PySide6.QtWidgets import QMainWindow
# Import MainWindow effectively by deferring import or restructuring to avoid circular dep
# For now, we assume MainWindow is in main.py or will be moved to ui/main_window.py
# To be scalable, we should move MainWindow out of main.py

class WindowManager:
    def __init__(self, window_class):
        self.ctx = get_context()
        self.window_class = window_class

    def new_window(self):
        """
        Spawns a new independent window.
        """
        win = self.window_class()
        win.show()
        self.ctx.active_windows.append(win)
        
        # Cleanup when closed
        # win.destroyed.connect(lambda: self.ctx.active_windows.remove(win))
        return win

    def close_all(self):
        for win in self.ctx.active_windows:
            win.close()
