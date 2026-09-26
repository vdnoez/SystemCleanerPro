"""VPN-Info-Seite — zeigt wie man VPNs manuell einrichtet."""
import subprocess

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame
)
from PyQt6.QtCore import Qt

from src.ui.widgets import Card, PageHeader
from src.ui.theme import Colors


# ═══════════════════════════════════════════════════════════════
# VPN-ANBIETER-LISTE
# ═══════════════════════════════════════════════════════════════
VPN_PROVIDERS = [
    {
        "name": "Proton VPN",
        "url": "https://protonvpn.com/free-vpn",
        "free": "Unbegrenzt, sicher, kein Logging",
        "note": "Empfohlen — Open Source, CERN-Wissenschaftler",
        "color": "#10b981",
    },
    {
        "name": "hide.me",
        "url": "https://hide.me/en/free-vpn",
        "free": "Unbegrenzt, keine Anmeldung nötig",
        "note": "8 Standorte, kein E-Mail-Zwang",
        "color": "#10b981",
    },
    {
        "name": "Windscribe",
        "url": "https://windscribe.com/",
        "free": "10 GB/Monat",
        "note": "Viele Standorte, WireGuard-Support",
        "color": "#f59e0b",
    },
    {
        "name": "TunnelBear",
        "url": "https://www.tunnelbear.com/",
        "free": "2 GB/Monat",
        "note": "Einfach zu bedienen, jährliche Audits",
        "color": "#f59e0b",
    },
    {
        "name": "Mullvad",
        "url": "https://mullvad.net/",
        "free": "Kostenpflichtig (5€/Monat)",
        "note": "Beste Privacy — keine Accounts, Bar-Zahlung",
        "color": "#3b82f6",
    },
]


class VpnPage(QWidget):
    """Info-Seite statt VPN-Manager."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "🔒 VPN-Einrichtung",
            "Anleitung zum manuellen Einrichten von VPNs unter Windows"
        ))

        # ─── Info-Banner ───
        info_card = Card()
        info_row = QHBoxLayout()
        info_row.setSpacing(14)

        icon = QLabel("ℹ️")
        icon.setStyleSheet("font-size: 24px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_row.addWidget(icon)

        info_text = QLabel(
            "<b>Automatische VPN-Verwaltung wurde entfernt.</b><br><br>"
            "Die Windows-eigene VPN-Verwaltung hat auf vielen Systemen "
            "Probleme (WMI-Fehler 0x80041010). Deshalb zeigen wir dir "
            "hier, wie du VPNs <b>manuell</b> und <b>zuverlässig</b> "
            "einrichtest — in 2 Minuten erledigt."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "line-height: 1.6;"
        )
        info_row.addWidget(info_text, 1)

        info_card.add_widget_direct(info_row)
        layout.addWidget(info_card)

        # ─── Anleitung ───
        guide_card = Card("📖 So richtest du ein VPN ein")

        steps = [
            ("1.", "Windows-Einstellungen öffnen",
             "Klicke unten auf den Button 'Windows-Einstellungen öffnen'"),
            ("2.", "Zu 'Netzwerk & Internet' → 'VPN'",
             "Links in der Navigation"),
            ("3.", "'VPN hinzufügen' klicken",
             "Oben in der Liste"),
            ("4.", "Anbieter auswählen",
             "Wähle einen der unten vorgeschlagenen Anbieter"),
            ("5.", "Server + Zugangsdaten eintragen",
             "Die bekommst du von deinem VPN-Anbieter auf der Website"),
            ("6.", "Speichern und verbinden",
             "Fertig! Du kannst jetzt über das Netzwerk-Symbol in der "
             "Taskleiste verbinden"),
        ]

        for num, title, desc in steps:
            step_widget = QWidget()
            step_row = QHBoxLayout(step_widget)
            step_row.setContentsMargins(0, 4, 0, 4)
            step_row.setSpacing(12)

            num_lbl = QLabel(num)
            num_lbl.setFixedWidth(28)
            num_lbl.setStyleSheet(
                f"color: {Colors.ACCENT}; font-size: 14px; "
                "font-weight: 800;"
            )
            num_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
            step_row.addWidget(num_lbl)

            text_col = QVBoxLayout()
            text_col.setSpacing(2)

            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
                "font-weight: 700;"
            )
            text_col.addWidget(title_lbl)

            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;"
            )
            text_col.addWidget(desc_lbl)

            step_row.addLayout(text_col, 1)
            guide_card.add(step_widget)

        layout.addWidget(guide_card)

        # ─── Windows-Einstellungen öffnen Button ───
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        open_btn = QPushButton("⚙  Windows-Einstellungen öffnen")
        open_btn.setMinimumHeight(46)
        open_btn.clicked.connect(self._open_windows_vpn_settings)
        btn_row.addWidget(open_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ─── Anbieter-Liste ───
        providers_card = Card("🆓 Empfohlene VPN-Anbieter")

        for provider in VPN_PROVIDERS:
            prov_widget = QWidget()
            prov_row = QHBoxLayout(prov_widget)
            prov_row.setContentsMargins(0, 6, 0, 6)
            prov_row.setSpacing(14)

            # Farbiger Punkt
            dot = QLabel("●")
            dot.setStyleSheet(
                f"color: {provider['color']}; font-size: 18px;"
            )
            dot.setFixedWidth(20)
            prov_row.addWidget(dot)

            # Info
            info_col = QVBoxLayout()
            info_col.setSpacing(2)

            name_lbl = QLabel(provider["name"])
            name_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
                "font-weight: 700;"
            )
            info_col.addWidget(name_lbl)

            free_lbl = QLabel(
                f"{provider['free']}  ·  {provider['note']}"
            )
            free_lbl.setStyleSheet(
                f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
            )
            info_col.addWidget(free_lbl)

            prov_row.addLayout(info_col, 1)

            # Open-Button
            open_prov_btn = QPushButton("Website öffnen")
            open_prov_btn.setObjectName("SecondaryButton")
            open_prov_btn.setMinimumHeight(34)
            open_prov_btn.setMinimumWidth(140)
            url = provider["url"]
            open_prov_btn.clicked.connect(
                lambda _, u=url: self._open_url(u)
            )
            prov_row.addWidget(open_prov_btn)

            providers_card.add(prov_widget)

        layout.addWidget(providers_card)

        # ─── Warnung ───
        warn_card = Card()
        warn_row = QHBoxLayout()
        warn_row.setSpacing(14)

        warn_icon = QLabel("⚠️")
        warn_icon.setStyleSheet("font-size: 24px;")
        warn_icon.setAlignment(Qt.AlignmentFlag.AlignTop)
        warn_row.addWidget(warn_icon)

        warn_text = QLabel(
            "<b>Wichtig zur Sicherheit:</b><br>"
            "• Öffentliche VPN-Server (VPN Gate, kostenlose Relays) sind "
            "<b>nicht</b> für sensible Daten geeignet (Banking, Passwörter).<br>"
            "• Nutze für Privacy <b>Proton VPN, hide.me oder Mullvad</b>.<br>"
            "• Ein VPN ersetzt <b>kein</b> Antivirus und <b>keine</b> "
            "Firewall."
        )
        warn_text.setWordWrap(True)
        warn_text.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; "
            "line-height: 1.6;"
        )
        warn_row.addWidget(warn_text, 1)

        warn_card.add_widget_direct(warn_row)
        layout.addWidget(warn_card)

        layout.addStretch()

    # ═══════════════════════════════════════════════════════════
    def _open_windows_vpn_settings(self):
        """Öffnet die Windows-VPN-Einstellungen."""
        try:
            # Windows 11 Settings URI
            subprocess.Popen(["start", "ms-settings:network-vpn"], shell=True)
        except Exception:
            try:
                subprocess.Popen(
                    ["explorer.exe", "ms-settings:network-vpn"]
                )
            except Exception as e:
                print(f"Fehler: {e}")

    def _open_url(self, url: str):
        """Öffnet URL im Standard-Browser."""
        try:
            subprocess.Popen(["start", url], shell=True)
        except Exception as e:
            print(f"Fehler: {e}")