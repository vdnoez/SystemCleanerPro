"""Über-Dialog — mit Besitzer-Info."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame
)
from PyQt6.QtCore import Qt

from src.core.config import APP_NAME, APP_VERSION, APP_OWNER
from src.ui.theme import Colors, get_stylesheet


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Über {APP_NAME}")
        self.setMinimumSize(520, 520)
        self.setStyleSheet(get_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # ═══ Logo ═══
        title = QLabel("⚡")
        title.setStyleSheet("font-size: 64px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ═══ App-Name ═══
        app_name = QLabel("Cleaner Pro")
        app_name.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 26px; "
            "font-weight: 800; letter-spacing: -0.5px;"
        )
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_name)

        # ═══ Version ═══
        version = QLabel(f"Version {APP_VERSION}")
        version.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
        )
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        layout.addSpacing(8)

        # ═══ Besitzer-Card ═══
        owner_card = QFrame()
        owner_card.setObjectName("Card")
        owner_layout = QVBoxLayout(owner_card)
        owner_layout.setContentsMargins(20, 16, 20, 16)
        owner_layout.setSpacing(4)

        owner_label = QLabel("BESITZER")
        owner_label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 10px; "
            "font-weight: 700; letter-spacing: 1.5px;"
        )
        owner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        owner_layout.addWidget(owner_label)

        owner_name = QLabel(APP_OWNER)
        owner_name.setStyleSheet(
            f"color: {Colors.ACCENT}; font-size: 20px; "
            "font-weight: 800;"
        )
        owner_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        owner_layout.addWidget(owner_name)

        github_link = QLabel(
            f'<a href="https://github.com/{APP_OWNER}/SystemCleanerPro" '
            f'style="color: {Colors.TEXT_SECONDARY}; '
            f'text-decoration: none;">github.com/{APP_OWNER}</a>'
        )
        github_link.setOpenExternalLinks(True)
        github_link.setStyleSheet("font-size: 11px;")
        github_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        owner_layout.addWidget(github_link)

        layout.addWidget(owner_card)

        layout.addSpacing(8)

        # ═══ Beschreibung ═══
        desc = QLabel(
            "Modernes Windows-System-Tool mit Fokus auf Privacy, "
            "Gaming und Developer-Tools.<br><br>"
            "<b>17 Seiten</b> · <b>5 Themes</b> · <b>Auto-Updater</b>"
        )
        desc.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "line-height: 1.6;"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        # ═══ Copyright ═══
        copy = QLabel(
            f"© 2026 {APP_OWNER}  ·  Made with 💜  ·  PyQt6"
        )
        copy.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
        )
        copy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copy)

        # ═══ Buttons ═══
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        close_btn = QPushButton("Schließen")
        close_btn.setMinimumHeight(40)
        close_btn.setMinimumWidth(120)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)