import qtawesome as qta
from PySide6.QtGui import QIcon

def get_icon(name, color=None):
    try:
        # qtawesome 1.x logic
        if color:
            return qta.icon(name, color=color)
        else:
            return qta.icon(name)
    except Exception as e:
        print(f"Warning: Failed to load icon '{name}'. Error: {e}")
        try:
            return qta.icon("fa5s.question-circle", color="red")
        except:
            return QIcon()
