"""Gesperrte Seite — zeigt Pro-Hinweis."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame
)
from PyQt6.QtCore import Qt

from src.ui.widgets import Card, PageHeader
from src.ui.theme import Colors


class LockedPage(QWidget):
    """Anzeige für gesperrte Pro-Features."""

    def __init__(self, page_name: str, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(20)

        # ─── Header ───
        layout.addWidget(PageHeader(
            f"🔒  {page_name}",
            "Dieses Feature ist nur in der Pro-Version verfügbar"
        ))

        layout.addStretch()

        # ─── Zentrierte Card ───
        card_container = QHBoxLayout()
        card_container.addStretch()

        card = Card()
        card.setMinimumWidth(480)
        card.setMaximumWidth(620)

        content = QVBoxLayout()
        content.setSpacing(20)

        # Lock-Icon
        icon_lbl = QLabel("🔒")
        icon_lbl.setStyleSheet("font-size: 72px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.addWidget(icon_lbl)

        # Titel
        title = QLabel(f"{page_name} ist gesperrt")
        title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 22px; "
            "font-weight: 800;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.addWidget(title)

        # Beschreibung
        desc = QLabel(
            f"Diese Funktion gehört zur <b>Pro-Version</b> von "
            f"Cleaner Pro.<br><br>"
            f"Aktiviere eine Lizenz um <b>{page_name}</b> und alle "
            f"anderen Pro-Features freizuschalten."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; "
            "line-height: 1.7;"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.addWidget(desc)

        content.addSpacing(8)

        # Pro-Features Liste
        features_frame = QFrame()
        features_frame.setStyleSheet(
            f"background-color: {Colors.BG_OVERLAY}; "
            f"border: 1px solid {Colors.BORDER}; "
            "border-radius: 10px; padding: 16px;"
        )
        features_layout = QVBoxLayout(features_frame)
        features_layout.setSpacing(6)

        features_title = QLabel("⭐  Pro-Features")
        features_title.setStyleSheet(
            f"color: {Colors.ACCENT}; font-size: 13px; "
            "font-weight: 700; padding-bottom: 6px;"
        )
        features_layout.addWidget(features_title)

        pro_features = [
            "🧹  Cleaner mit Hard-Delete",
            "📦  Software-Updater (winget)",
            "💾  RAM-Cleaner (crashsicher)",
            "🔥  File Shredder (DoD 5220.22-M)",
            "🚀  Autostart-Manager",
            "🎮  Games-Booster",
            "🔐  Passwort-Manager (AES-256)",
        ]

        for feat in pro_features:
            feat_lbl = QLabel(feat)
            feat_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 12px;"
            )
            features_layout.addWidget(feat_lbl)

        content.addWidget(features_frame)

        content.addSpacing(8)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        buy_btn = QPushButton("💳  Pro-Version kaufen")
        buy_btn.setMinimumHeight(48)
        buy_btn.setMinimumWidth(220)
        buy_btn.clicked.connect(self._open_shop)
        btn_row.addWidget(buy_btn)

        license_btn = QPushButton("🔑  Lizenz eingeben")
        license_btn.setObjectName("SecondaryButton")
        license_btn.setMinimumHeight(48)
        license_btn.setMinimumWidth(180)
        license_btn.clicked.connect(self._open_license)
        btn_row.addWidget(license_btn)

        btn_row.addStretch()
        content.addLayout(btn_row)

        card.layout.addLayout(content)
        card_container.addWidget(card)
        card_container.addStretch()

        layout.addLayout(card_container)
        layout.addStretch()

    def _open_shop(self):
        """Öffnet Shop-Link."""
        import webbrowser
        try:
            webbrowser.open(
                "https://github.com/vdnoez/SystemCleanerPro"
            )
        except Exception:
            pass

    def _open_license(self):
        """Springt zur Lizenz-Seite."""
        try:
            win = self.window()
            if hasattr(win, "_goto_page"):
                win._goto_page("Lizenz")
        except Exception:
            pass