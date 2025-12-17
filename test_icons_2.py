import qtawesome as qta
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

icons = [
    "fa5s.car",
    "fa5s.minus",
    "fa5s.window-maximize",
    "fa5s.times"
]

for icon in icons:
    try:
        qta.icon(icon)
        print(f"OK: {icon}")
    except Exception as e:
        print(f"FAIL: {icon} - {e}")
