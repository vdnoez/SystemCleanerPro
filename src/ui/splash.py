"""Splash-Screen — passend zum neuen Slate-Design."""
from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont, QLinearGradient

from src.core.config import APP_VERSION, APP_OWNER
from src.ui.theme import Colors, FONT_MONO


class SplashScreen(QSplashScreen):
    finished = pyqtSignal()

    def __init__(self):
        pixmap = QPixmap(560, 340)
        pixmap.fill(QColor(Colors.BG_BASE))
        super().__init__(pixmap)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self._progress = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(25)

    def _tick(self):
        if self._progress < 100:
            self._progress += 1.3
            if self._progress > 100:
                self._progress = 100
            self.repaint()
        else:
            self._timer.stop()
            self.finished.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Gradient-Hintergrund
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(Colors.BG_GRADIENT_1))
        gradient.setColorAt(1, QColor(Colors.BG_GRADIENT_2))
        painter.fillRect(self.rect(), gradient)

        # Rahmen
        pen = painter.pen()
        pen.setColor(QColor(Colors.BORDER))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

        # Blitz
        painter.setPen(QColor(Colors.ACCENT))
        font = QFont(FONT_MONO, 56)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, 40, self.width(), 90,
                         Qt.AlignmentFlag.AlignCenter, "⚡")

        # Titel
        painter.setPen(QColor(Colors.TEXT_PRIMARY))
        font = QFont("Segoe UI Variable Display", 26)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, 145, self.width(), 45,
                         Qt.AlignmentFlag.AlignCenter, "Cleaner Pro")

        # Subtitle
        painter.setPen(QColor(Colors.TEXT_SECONDARY))
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        painter.drawText(0, 195, self.width(), 20,
                         Qt.AlignmentFlag.AlignCenter,
                         "System Diagnostic & Optimizer")

        # Ladebalken
        bar_x = 80
        bar_y = 250
        bar_w = self.width() - 160
        bar_h = 4

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(Colors.BG_OVERLAY))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 2, 2)

        progress_w = int(bar_w * self._progress / 100)
        if progress_w > 0:
            grad = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            grad.setColorAt(0, QColor(Colors.ACCENT))
            grad.setColorAt(1, QColor(Colors.ACCENT_2))
            painter.setBrush(grad)
            painter.drawRoundedRect(bar_x, bar_y, progress_w, bar_h, 2, 2)

        # Prozent
        painter.setPen(QColor(Colors.ACCENT_GLOW))
        font = QFont(FONT_MONO, 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, bar_y - 25, self.width() - 80, 20,
                         Qt.AlignmentFlag.AlignRight,
                         f"{int(self._progress)}%")

        # Footer
        painter.setPen(QColor(Colors.TEXT_MUTED))
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        painter.drawText(0, self.height() - 35, self.width(), 20,
                         Qt.AlignmentFlag.AlignCenter,
                         f"v{APP_VERSION}  ·  {APP_OWNER}")

        painter.end()