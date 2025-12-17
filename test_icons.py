import qtawesome as qta
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

icons = [
    "fa5s.info-circle",
    "fa5s.sliders-h",
    "fa5s.toolbox",
    "fa5s.robot",
    "fa5s.sync",
    "fa5s.wifi",
    "fa5b.bluetooth",
    "fa5s.camera",
    "fa5s.cog",
    "fa5s.trash"
]

for icon in icons:
    try:
        qta.icon(icon)
        print(f"OK: {icon}")
    except Exception as e:
        print(f"FAIL: {icon} - {e}")
