"""System-Tray-Icon."""
from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QApplication
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt

from src.core.config import APP_NAME
from src.ui.theme import Colors
from src.ui.icons import icon as get_icon


def create_tray_icon(parent_window) -> QSystemTrayIcon:
    """Erstellt ein Tray-Icon mit Kontextmenü."""

    # Icon generieren (Blitz)
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Kreis
    painter.setBrush(QColor(Colors.ACCENT))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 60, 60)

    # Blitz
    painter.setPen(QColor("white"))
    font = QFont("Segoe UI", 32)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "⚡")
    painter.end()

    tray_icon = QIcon(pixmap)
    app_icon = QApplication.instance().windowIcon()
    if not app_icon.isNull():
        tray_icon = app_icon

    tray = QSystemTrayIcon(tray_icon, parent_window)
    tray.setToolTip(f"{APP_NAME} - läuft im Hintergrund")

    # Menü
    menu = QMenu()

    show_action = menu.addAction("Fenster anzeigen")
    show_action.triggered.connect(lambda: _show_window(parent_window))

    menu.addSeparator()

    refresh_action = menu.addAction("Aktualisieren")
    refresh_action.triggered.connect(lambda: _refresh(parent_window))

    quit_action = menu.addAction("Beenden")
    quit_action.triggered.connect(QApplication.instance().quit)

    tray.setContextMenu(menu)

    # Doppelklick → Fenster zeigen
    tray.activated.connect(
        lambda reason: _show_window(parent_window)
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
    )

    return tray


def _show_window(window):
    window.showNormal()
    window.activateWindow()
    window.raise_()


def _refresh(window):
    """Triggert Refresh auf der aktuellen Seite."""
    try:
        current = window.stack.currentWidget()
        if hasattr(current, "refresh"):
            current.refresh()
    except Exception:
        pass