"""Lizenz-Verwaltungsseite."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt

from src.ui.widgets import Card, PageHeader
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.license import (
    get_license_status, activate_license, remove_license,
    validate_key, TRIAL_DAYS
)


class LicensePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "🔑 Lizenz",
            "Lizenz-Status und Aktivierung"
        ))

        # ═══════════════════════════════════════════════════════
        # STATUS-CARD
        # ═══════════════════════════════════════════════════════
        self.status_card = Card("Aktueller Status")

        status_row = QHBoxLayout()
        status_row.setSpacing(16)

        self.status_icon = QLabel("⚪")
        self.status_icon.setStyleSheet("font-size: 36px;")
        status_row.addWidget(self.status_icon)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        self.status_lbl = QLabel("Lade Status...")
        self.status_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 17px; "
            "font-weight: 700;"
        )
        info_col.addWidget(self.status_lbl)

        self.status_detail = QLabel("")
        self.status_detail.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        self.status_detail.setWordWrap(True)
        info_col.addWidget(self.status_detail)

        status_row.addLayout(info_col, 1)
        self.status_card.add_widget_direct(status_row)
        layout.addWidget(self.status_card)

        # ═══════════════════════════════════════════════════════
        # AKTIVIERUNGS-CARD
        # ═══════════════════════════════════════════════════════
        self.activate_card = Card("Lizenz aktivieren")

        activate_info = QLabel(
            "Gib hier deinen Lizenz-Key ein "
            "(Format: <code>SCP-XXXX-XXXX-XXXX-XXXX</code>)."
        )
        activate_info.setWordWrap(True)
        activate_info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        self.activate_card.add(activate_info)
        self.activate_card.add_spacing(6)

        # Eingabe-Reihe
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("SCP-XXXX-XXXX-XXXX-XXXX")
        self.key_input.setMinimumHeight(46)
        self.key_input.setStyleSheet(
            f"font-family: Consolas, monospace; font-size: 15px; "
            f"letter-spacing: 2px;"
        )
        self.key_input.returnPressed.connect(self._activate)
        input_row.addWidget(self.key_input, 1)

        self.activate_btn = QPushButton("🔓 Aktivieren")
        self.activate_btn.setMinimumHeight(46)
        self.activate_btn.setMinimumWidth(160)
        self.activate_btn.clicked.connect(self._activate)
        input_row.addWidget(self.activate_btn)

        self.activate_card.add_widget_direct(input_row)

        # Deaktivieren-Button
        self.deactivate_row = QHBoxLayout()
        self.deactivate_row.addStretch()

        self.deactivate_btn = QPushButton("🗑️  Lizenz entfernen")
        self.deactivate_btn.setObjectName("DangerButton")
        self.deactivate_btn.setMinimumHeight(40)
        self.deactivate_btn.setMinimumWidth(200)
        self.deactivate_btn.setVisible(False)
        self.deactivate_btn.clicked.connect(self._deactivate)
        self.deactivate_row.addWidget(self.deactivate_btn)

        self.activate_card.add_widget_direct(self.deactivate_row)
        layout.addWidget(self.activate_card)

        # ═══════════════════════════════════════════════════════
        # PRO-FEATURES-CARD
        # ═══════════════════════════════════════════════════════
        features_card = Card("⭐ Was schaltet die Pro-Lizenz frei?")

        features = [
            "🧹  Cleaner mit Hard-Delete",
            "📦  Software-Updater (winget)",
            "💾  RAM-Cleaner (crashsicher)",
            "🔥  File Shredder (DoD 5220.22-M)",
            "🚀  Autostart-Manager",
            "🔄  App-Update via GitHub",
            "🔐  Passwort-Manager (AES-256)",
            "🎮  Games-Booster",
        ]

        for feat in features:
            feat_lbl = QLabel(feat)
            feat_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 12px; "
                "padding: 3px 0;"
            )
            features_card.add(feat_lbl)

        layout.addWidget(features_card)

        # ═══════════════════════════════════════════════════════
        # INFO-CARD
        # ═══════════════════════════════════════════════════════
        info_card = Card("ℹ️  Info")

        info_text = QLabel(
            f"<b>Testversion:</b><br>"
            f"Beim ersten Start hast du <b>{TRIAL_DAYS} Tage</b> Zeit, "
            f"die App kostenlos zu testen. Danach benötigst du einen "
            f"Lizenz-Key um die Pro-Features weiter zu nutzen.<br><br>"
            f"<b>Lizenz kaufen:</b><br>"
            f"Kontakt: "
            f"<a href='https://github.com/vdnoez/SystemCleanerPro' "
            f"style='color: {Colors.ACCENT}; text-decoration: none;'>"
            f"github.com/vdnoez/SystemCleanerPro</a>"
        )
        info_text.setWordWrap(True)
        info_text.setOpenExternalLinks(True)
        info_text.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "line-height: 1.7;"
        )
        info_card.add(info_text)
        layout.addWidget(info_card)

        layout.addStretch()

        # Initial Status laden
        self._update_status()

    # ═══════════════════════════════════════════════════════════
    def _update_status(self):
        """Aktualisiert Status-Anzeige."""
        try:
            status = get_license_status()
        except Exception as e:
            self.status_icon.setText("❌")
            self.status_lbl.setText("Fehler beim Laden")
            self.status_detail.setText(str(e))
            return

        if status["status"] == "valid":
            # Lizenz aktiv
            self.status_icon.setText("✅")
            self.status_lbl.setText("Lizenz aktiv")
            key = status.get("key", "")
            activated = status.get("activated_at", "?")[:10]

            # Key maskieren
            if len(key) >= 16:
                masked = key[:8] + "-****-****-" + key[-4:]
            else:
                masked = key

            self.status_detail.setText(
                f"Key: {masked}   ·   Aktiviert am: {activated}"
            )
            self.activate_card.setVisible(False)
            self.deactivate_btn.setVisible(True)

        elif status["status"] == "trial":
            # Trial aktiv
            self.status_icon.setText("🎁")
            self.status_lbl.setText("Testversion aktiv")
            days = status.get("trial_days_left", 0)
            expires = status.get("trial_expires", "?")
            self.status_detail.setText(
                f"Noch {days} Tage verfügbar (bis {expires})"
            )
            self.activate_card.setVisible(True)
            self.deactivate_btn.setVisible(False)

        elif status["status"] == "expired":
            # Trial abgelaufen
            self.status_icon.setText("❌")
            self.status_lbl.setText("Testversion abgelaufen")
            self.status_detail.setText(
                "Bitte gib einen Lizenz-Key ein um die Pro-Features "
                "weiter zu nutzen."
            )
            self.activate_card.setVisible(True)
            self.deactivate_btn.setVisible(False)

        else:  # missing
            self.status_icon.setText("⚪")
            self.status_lbl.setText("Kein Status")
            self.status_detail.setText(
                "Bitte App neu starten oder Lizenz-Key eingeben."
            )
            self.activate_card.setVisible(True)
            self.deactivate_btn.setVisible(False)

    # ═══════════════════════════════════════════════════════════
    def _activate(self):
        """Aktiviert Lizenz-Key."""
        key = self.key_input.text().strip().upper()

        if not key:
            toast.warning("Bitte Lizenz-Key eingeben")
            return

        if not validate_key(key):
            toast.error("Ungültiger Lizenz-Key")
            self.key_input.selectAll()
            self.key_input.setFocus()
            return

        ok, msg = activate_license(key)
        if ok:
            toast.success("Lizenz erfolgreich aktiviert!")
            self.key_input.clear()
            self._update_status()

            # Info-Dialog
            QMessageBox.information(
                self,
                "✅ Lizenz aktiviert",
                "Deine Lizenz wurde erfolgreich aktiviert!\n\n"
                "Bitte starte die App neu damit alle Pro-Features "
                "freigeschaltet werden."
            )
        else:
            toast.error(msg)

    # ═══════════════════════════════════════════════════════════
    def _deactivate(self):
        """Entfernt Lizenz."""
        reply = QMessageBox.question(
            self,
            "Lizenz entfernen",
            "Lizenz wirklich entfernen?\n\n"
            "Die App wird beim nächsten Start wieder im Trial-Modus "
            "sein (oder FREE, falls Trial abgelaufen).",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            remove_license()
            toast.info("Lizenz entfernt")
            self._update_status()

            QMessageBox.information(
                self,
                "Lizenz entfernt",
                "Die Lizenz wurde entfernt.\n\n"
                "Bitte starte die App neu."
            )
        except Exception as e:
            toast.error(f"Fehler: {e}")