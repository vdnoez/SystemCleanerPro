"""Glassmorphism-Widgets."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient
from src.ui.theme import Colors, FONT_MONO


class Card(QFrame):
    """Glass-Card mit viel Padding."""
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(26, 24, 26, 24)
        self.layout.setSpacing(14)

        if title:
            lbl = QLabel(title.upper())
            lbl.setObjectName("CardTitle")
            self.layout.addWidget(lbl)

    def add(self, widget):
        self.layout.addWidget(widget)
        return widget

    def add_widget_direct(self, layout):
        self.layout.addLayout(layout)

    def add_spacing(self, px: int = 8):
        self.layout.addSpacing(px)


class MetricCard(Card):
    """Metric mit Gradient-Text."""
    def __init__(self, title: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")

        header = QHBoxLayout()
        header.setSpacing(10)
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 20px;")
            header.addWidget(icon_lbl)
        title_lbl = QLabel(title.upper())
        title_lbl.setObjectName("CardTitle")
        header.addWidget(title_lbl)
        header.addStretch()
        self.layout.addLayout(header)

        self.value_lbl = QLabel("--")
        self.value_lbl.setObjectName("CardValue")
        self.layout.addWidget(self.value_lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self.layout.addWidget(self.bar)

        self.detail_lbl = QLabel("")
        self.detail_lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
        )
        self.layout.addWidget(self.detail_lbl)

    def set_value(self, value: float, detail: str = ""):
        self.value_lbl.setText(f"{value:.1f}%")
        self.bar.setValue(int(value))
        if detail:
            self.detail_lbl.setText(detail)

        if value >= 85:
            self.bar.setObjectName("Danger")
        elif value >= 65:
            self.bar.setObjectName("Warning")
        else:
            self.bar.setObjectName("Success")
        self.bar.style().unpolish(self.bar)
        self.bar.style().polish(self.bar)

    def set_text(self, text: str, detail: str = ""):
        self.value_lbl.setText(text)
        if detail:
            self.detail_lbl.setText(detail)


class CircularProgress(QWidget):
    """Runder Fortschritt mit Gradient."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self._value = 0
        self._target = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)

    def set_value(self, value: int):
        self._target = max(0, min(100, value))

    def _animate(self):
        if self._value != self._target:
            diff = self._target - self._value
            self._value += max(1, abs(diff) // 8) * (1 if diff > 0 else -1)
            if abs(self._target - self._value) < 2:
                self._value = self._target
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(14, 14, -14, -14)

        # Hintergrund
        pen = QPen(QColor(Colors.BORDER_LIGHT), 14)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Gradient-Farbe für Ring
        color = QColor(Colors.SUCCESS if self._value >= 70
                       else Colors.WARNING if self._value >= 40
                       else Colors.DANGER)
        pen.setColor(color)
        painter.setPen(pen)
        span = int(-self._value / 100 * 360 * 16)
        painter.drawArc(rect, 90 * 16, span)

        # Zahl
        painter.setPen(QColor(Colors.TEXT_PRIMARY))
        font = QFont(FONT_MONO, 34)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(self._value))


class PageHeader(QWidget):
    """Großer Header mit Gradient-Look."""
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(8)

        t = QLabel(title)
        t.setObjectName("PageTitle")
        layout.addWidget(t)

        if subtitle:
            s = QLabel(subtitle)
            s.setObjectName("PageSubtitle")
            layout.addWidget(s)