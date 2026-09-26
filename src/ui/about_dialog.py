"""About-Dialog."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt

from src.core.config import APP_NAME, APP_VERSION
from src.ui.theme import Colors, get_stylesheet


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Über {APP_NAME}")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(get_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Logo / Titel
        title = QLabel("⚡")
        title.setStyleSheet("font-size: 64px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        app_name = QLabel("Cleaner Pro")
        app_name.setStyleSheet(
            f"font-size: 24px; font-weight: 700; color: {Colors.TEXT_PRIMARY};"
        )
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_name)

        version = QLabel(f"Version {APP_VERSION}")
        version.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 14px;"
        )
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        # Beschreibung
        desc = QLabel(
            "Modernes Windows-System-Management mit Fokus auf "
            "Privacy, Gaming und Developer-Tools.\n\n"
            "Features:\n"
            "• Live-System-Überwachung\n"
            "• Privacy-Score mit Auto-Fix\n"
            "• Game-Booster\n"
            "• Cleaner mit Papierkorb\n"
            "• RAM-Cleaner\n"
            "• File Shredder (DoD 5220.22-M)\n"
            "• Autostart-Manager"
        )
        desc.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "line-height: 1.6;"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignLeft)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        # Copyright
        copy = QLabel(f"© 2026  ·  Made with 💜  ·  PyQt6")
        copy.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
        )
        copy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copy)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton("Schließen")
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)