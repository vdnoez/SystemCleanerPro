"""UI-Widgets — mit EmptyState & LoadingState."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QFrame, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from src.ui.theme import Colors


class Card(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 22, 24, 22)
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


class MetricCard(QFrame):
    def __init__(self, title: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(10)

        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 18px;")
            header.addWidget(icon_lbl)

        title_lbl = QLabel(title.upper())
        title_lbl.setObjectName("CardTitle")
        header.addWidget(title_lbl)
        header.addStretch()
        layout.addLayout(header)

        self.value_lbl = QLabel("--")
        self.value_lbl.setObjectName("CardValue")
        layout.addWidget(self.value_lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        layout.addWidget(self.bar)

        self.detail_lbl = QLabel("")
        self.detail_lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
        )
        layout.addWidget(self.detail_lbl)

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

        size = min(self.width(), self.height()) - 30
        x = (self.width() - size) // 2
        y = (self.height() - size) // 2
        rect = QRectF(x, y, size, size)

        pen = QPen(QColor(Colors.BORDER_LIGHT), 12)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        if self._value >= 70:
            color = QColor(Colors.SUCCESS)
        elif self._value >= 40:
            color = QColor(Colors.WARNING)
        else:
            color = QColor(Colors.DANGER)

        glow = QColor(color)
        glow.setAlpha(50)
        pen = QPen(glow, 18)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        span = int(-self._value / 100 * 360 * 16)
        painter.drawArc(rect, 90 * 16, span)

        pen = QPen(color, 12)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, span)

        painter.setPen(QColor(Colors.TEXT_PRIMARY))
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(self._value))


class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)

        t = QLabel(title)
        t.setObjectName("PageTitle")
        layout.addWidget(t)

        if subtitle:
            s = QLabel(subtitle)
            s.setObjectName("PageSubtitle")
            layout.addWidget(s)


class EmptyState(QWidget):
    """Schöne Anzeige wenn Liste leer ist."""
    def __init__(self, icon: str = "📭", title: str = "Keine Daten",
                 message: str = "", action_text: str = "",
                 action_callback=None, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)
        layout.addStretch()

        # Icon
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 48px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        # Titel
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 15px; "
            "font-weight: 700;"
        )
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        # Message
        if message:
            msg_lbl = QLabel(message)
            msg_lbl.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
            )
            msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg_lbl.setWordWrap(True)
            layout.addWidget(msg_lbl)

        # Action-Button
        if action_text and action_callback:
            btn = QPushButton(action_text)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(180)
            btn.clicked.connect(action_callback)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()


class LoadingState(QWidget):
    """Loading-Anzeige während Daten laden."""
    def __init__(self, text: str = "Lädt...", parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(14)
        layout.addStretch()

        icon_lbl = QLabel("⏳")
        icon_lbl.setStyleSheet("font-size: 42px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        text_lbl = QLabel(text)
        text_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
        )
        text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_lbl)

        layout.addStretch()


class StatRow(QWidget):
    """Eine Statistik-Zeile mit Label + Wert."""
    def __init__(self, label: str, value: str,
                 value_color: str = None, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(12)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        layout.addWidget(lbl, 1)

        self.value_lbl = QLabel(value)
        color = value_color or Colors.TEXT_PRIMARY
        self.value_lbl.setStyleSheet(
            f"color: {color}; font-size: 13px; font-weight: 700;"
        )
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.value_lbl)

    def set_value(self, value: str, color: str = None):
        self.value_lbl.setText(value)
        if color:
            self.value_lbl.setStyleSheet(
                f"color: {color}; font-size: 13px; font-weight: 700;"
            )