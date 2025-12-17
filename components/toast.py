from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint

class Toast(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setStyleSheet("""
            QLabel {
                background-color: #333333E6;
                color: white;
                padding: 12px 20px;
                border-radius: 12px;
                font-weight: 500;
                font-size: 13px;
                border: 1px solid #444;
            }
        """)
        self.layout.addWidget(self.label)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._fade_out)

    def show_message(self, message, msg_type="info", duration=3000):
        color = "#40E0D0" # info
        if msg_type == "warn": color = "#FFB86C"
        if msg_type == "error": color = "#FF5555"
        
        self.label.setStyleSheet(f"""
            QLabel {{
                background-color: #111111EE;
                color: {color};
                padding: 12px 20px;
                border-radius: 20px;
                font-weight: bold;
                border: 2px solid {color};
            }}
        """)
        self.label.setText(message)
        self.adjustSize()
        
        # Position at bottom center of parent
        parent_rect = self.parentWidget().rect()
        x = (parent_rect.width() - self.width()) // 2
        y = parent_rect.height() - self.height() - 50
        self.move(x, y)
        
        self.opacity_effect.setOpacity(0)
        self.show()
        
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()
        
        self.timer.start(duration)

    def _fade_out(self):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.finished.connect(self.hide)
        self.anim.start()
