"""Toast-Notifications — kleine Popups unten rechts."""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, pyqtSignal
)
from PyQt6.QtGui import QColor
from src.ui.theme import Colors


class Toast(QFrame):
    """Ein einzelner Toast (unten rechts)."""
    closed = pyqtSignal()

    TYPES = {
        "success": {"icon": "✅", "color": "#10b981"},
        "error":   {"icon": "❌", "color": "#ef4444"},
        "warning": {"icon": "⚠️", "color": "#f59e0b"},
        "info":    {"icon": "ℹ️", "color": "#6366f1"},
    }

    def __init__(self, message: str, toast_type: str = "info",
                 duration: int = 4000, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        info = self.TYPES.get(toast_type, self.TYPES["info"])
        color = info["color"]
        icon = info["icon"]

        # ─── Style ───
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_ELEVATED};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-left: 4px solid {color};
                border-radius: 10px;
            }}
            QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)

        self.setFixedWidth(360)
        self.setMinimumHeight(70)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 12, 12)
        layout.setSpacing(12)

        # Icon
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20px;")
        icon_lbl.setFixedWidth(28)
        layout.addWidget(icon_lbl)

        # Text
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
            "font-weight: 500;"
        )
        layout.addWidget(msg_lbl, 1)

        # Close-Button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_MUTED};
                border: none;
                font-size: 18px;
                font-weight: 400;
                padding: 0;
            }}
            QPushButton:hover {{
                color: {Colors.TEXT_PRIMARY};
                background-color: {Colors.BG_OVERLAY};
                border-radius: 12px;
            }}
        """)
        close_btn.clicked.connect(self._close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)

        # ─── Animation ───
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity)

        self._fade_in = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_in.setDuration(250)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)

        # Auto-Close
        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.timeout.connect(self._close)
        self._close_timer.start(duration)

    def show_at(self, x: int, y: int):
        """Zeigt Toast an bestimmter Position."""
        self.move(x, y)
        self.show()
        self._fade_in.start()

    def _close(self):
        """Schließt den Toast."""
        try:
            self._close_timer.stop()
        except Exception:
            pass

        # Fade-Out
        self._fade_out = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_out.setDuration(200)
        self._fade_out.setStartValue(self._opacity.opacity())
        self._fade_out.setEndValue(0.0)
        self._fade_out.finished.connect(self._really_close)
        self._fade_out.start()

    def _really_close(self):
        self.closed.emit()
        self.close()
        self.deleteLater()


class ToastManager:
    """Verwaltet mehrere Toasts unten rechts."""
    _instance = None
    _toasts = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._toasts = []
        return cls._instance

    def show(self, message: str, toast_type: str = "info",
             duration: int = 4000, parent=None):
        """Zeigt neuen Toast."""
        toast = Toast(message, toast_type, duration, parent)
        toast.closed.connect(lambda: self._remove_toast(toast))
        self._toasts.append(toast)
        self._reposition()
        return toast

    def success(self, message: str, duration: int = 3000):
        return self.show(message, "success", duration)

    def error(self, message: str, duration: int = 5000):
        return self.show(message, "error", duration)

    def warning(self, message: str, duration: int = 4000):
        return self.show(message, "warning", duration)

    def info(self, message: str, duration: int = 3000):
        return self.show(message, "info", duration)

    def _remove_toast(self, toast):
        if toast in self._toasts:
            self._toasts.remove(toast)
        self._reposition()

    def _reposition(self):
        """Positioniert alle Toasts neu (unten rechts)."""
        from PyQt6.QtWidgets import QApplication

        screen = QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()

        margin_right = 20
        margin_bottom = 60
        spacing = 10

        # Von unten nach oben stapeln
        y = geo.bottom() - margin_bottom
        for toast in reversed(self._toasts):
            h = toast.sizeHint().height()
            y -= h
            x = geo.right() - toast.width() - margin_right
            if not toast.isVisible():
                toast.show_at(x, y)
            else:
                toast.move(x, y)
            y -= spacing


# Globale Instanz
toast = ToastManager()