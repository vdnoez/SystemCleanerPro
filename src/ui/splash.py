"""Splash-Screen — Aurora Glassmorphism."""
from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont, QLinearGradient

from src.core.config import APP_VERSION
from src.ui.theme import Colors, FONT_MONO


BOOT_LINES = [
    "> initializing core...",
    "> loading themes...",
    "> mounting modules...",
    "> scanning system...",
    "> connecting services...",
    "> ready.",
]


class SplashScreen(QSplashScreen):
    """Splash mit Aurora-Gradient und Boot-Animation."""
    finished = pyqtSignal()

    def __init__(self):
        pixmap = QPixmap(600, 360)
        pixmap.fill(QColor(Colors.BG_BASE))
        super().__init__(pixmap)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowType.Tool)

        self._progress = 0
        self._visible_lines = 0
        self._cursor_visible = True
        self._dots = 0

        # Progress-Timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(25)

        # Cursor-Blink-Timer
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self._blink)
        self._cursor_timer.start(500)

        # Sicherheits-Timeout: max 6 Sekunden
        self._timeout = QTimer(self)
        self._timeout.setSingleShot(True)
        self._timeout.timeout.connect(self._force_finish)
        self._timeout.start(6000)

    def _blink(self):
        self._cursor_visible = not self._cursor_visible
        self.repaint()

    def _tick(self):
        if self._progress < 100:
            self._progress += 1.3
            if self._progress > 100:
                self._progress = 100
            self._visible_lines = min(
                len(BOOT_LINES),
                int(self._progress / 100 * len(BOOT_LINES)) + 1
            )
            self._dots = (self._dots + 1) % 4
            self.repaint()
        else:
            self._timer.stop()
            self._cursor_timer.stop()
            self._timeout.stop()
            self.finished.emit()

    def _force_finish(self):
        """Sicherheits-Notaus: beendet den Splash nach max. 6s."""
        self._timer.stop()
        self._cursor_timer.stop()
        self.finished.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ─── Gradient-Hintergrund ───
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(Colors.BG_GRADIENT_1))
        gradient.setColorAt(1, QColor(Colors.BG_GRADIENT_2))
        painter.fillRect(self.rect(), gradient)

        # ─── Glow-Effekt hinter Logo ───
        painter.setPen(Qt.PenStyle.NoPen)
        glow = QColor(Colors.ACCENT)
        glow.setAlpha(35)
        painter.setBrush(glow)
        painter.drawEllipse(self.width() // 2 - 160, 30, 320, 320)

        # ─── Neon-Rahmen ───
        pen = painter.pen()
        pen.setColor(QColor(Colors.ACCENT))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(2, 2, self.width() - 4, self.height() - 4)

        # ─── Logo ───
        painter.setPen(QColor(Colors.ACCENT))
        font = QFont(FONT_MONO, 64)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, 25, self.width(), 100,
                         Qt.AlignmentFlag.AlignCenter, "⚡")

        # ─── Titel mit Gradient-Farbe ───
        painter.setPen(QColor(Colors.TEXT_PRIMARY))
        font = QFont("Segoe UI Variable Display", 28)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, 130, self.width(), 45,
                         Qt.AlignmentFlag.AlignCenter, "Cleaner Pro")

        # ─── Subtitle ───
        painter.setPen(QColor(Colors.TEXT_SECONDARY))
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        painter.drawText(0, 180, self.width(), 20,
                         Qt.AlignmentFlag.AlignCenter,
                         "System Diagnostic & Optimizer")

        # ─── Boot-Lines ───
        painter.setPen(QColor(Colors.ACCENT))
        font = QFont(FONT_MONO, 9)
        painter.setFont(font)

        y = 220
        for i in range(self._visible_lines):
            line = BOOT_LINES[i]
            # Letzte Zeile + Cursor
            if i == self._visible_lines - 1 and self._progress < 100:
                painter.drawText(50, y, self.width() - 100, 16, 0, line)
                if self._cursor_visible:
                    fm = painter.fontMetrics()
                    tw = fm.horizontalAdvance(line)
                    painter.fillRect(50 + tw + 4, y - 12, 8, 14,
                                     QColor(Colors.ACCENT))
            else:
                # Fertige Zeilen: grün
                painter.setPen(QColor(Colors.SUCCESS))
                painter.drawText(50, y, self.width() - 100, 16, 0, line)
                painter.setPen(QColor(Colors.ACCENT))
            y += 18

        # ─── Ladebalken ───
        bar_x = 50
        bar_y = self.height() - 70
        bar_w = self.width() - 100
        bar_h = 6

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(Colors.BG_OVERLAY))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)

        progress_w = int(bar_w * self._progress / 100)
        if progress_w > 0:
            grad = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            grad.setColorAt(0, QColor(Colors.ACCENT))
            grad.setColorAt(1, QColor(Colors.ACCENT_2))
            painter.setBrush(grad)
            painter.drawRoundedRect(bar_x, bar_y, progress_w, bar_h, 3, 3)

        # ─── Prozent ───
        painter.setPen(QColor(Colors.ACCENT_GLOW))
        font = QFont(FONT_MONO, 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, bar_y - 22, self.width() - 50, 18,
                         Qt.AlignmentFlag.AlignRight,
                         f"{int(self._progress)}%")

        # ─── Version ───
        painter.setPen(QColor(Colors.TEXT_MUTED))
        font = QFont("Segoe UI", 8)
        painter.setFont(font)
        painter.drawText(0, self.height() - 30, self.width(), 18,
                         Qt.AlignmentFlag.AlignCenter,
                         f"v{APP_VERSION}")

        painter.end()