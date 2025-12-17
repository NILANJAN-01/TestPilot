from PySide6.QtCore import QRunnable, Slot, QObject, Signal

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object) # The data returned by run

class Worker(QRunnable):
    """
    Worker thread for running heavy tasks.
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            # Emit error
            import traceback
            traceback.print_exc()
            self.signals.error.emit((e, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
