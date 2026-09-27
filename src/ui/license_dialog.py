"""Lizenz-Dialog — Aktivierung + Trial-Anzeige."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt

from src.core.config import APP_NAME, APP_VERSION, APP_OWNER
from src.ui.theme import Colors, get_stylesheet
from src.modules.license import (
    get_license_status, activate_license, TRIAL_DAYS
)


class LicenseDialog(QDialog):
    """Lizenz-Aktivierung."""

    def __init__(self, parent=None, force_activation: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Lizenz aktivieren")
        self.setMinimumSize(560, 480)
        self.setStyleSheet(get_stylesheet())
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self.force_activation = force_activation
        self.activated = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(18)

        # ─── Logo ───
        logo = QLabel("⚡")
        logo.setStyleSheet("font-size: 56px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # ─── Titel ───
        if force_activation:
            title_text = "Testversion abgelaufen"
            subtitle_text = (
                f"Deine {TRIAL_DAYS}-tägige Testphase ist beendet.\n"
                f"Bitte gib einen Lizenz-Key ein um die App weiter zu nutzen."
            )
            title_color = Colors.DANGER
        else:
            title_text = "SystemCleanerPro"
            subtitle_text = (
                "Gib deinen Lizenz-Key ein um alle Features freizuschalten."
            )
            title_color = Colors.ACCENT

        title = QLabel(title_text)
        title.setStyleSheet(
            f"color: {title_color}; font-size: 22px; font-weight: 800;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(subtitle_text)
        subtitle.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # ─── Trial-Info (falls Trial läuft) ───
        status = get_license_status()
        if status["status"] == "trial":
            trial_card = QFrame()
            trial_card.setStyleSheet(
                f"background-color: {Colors.BG_ELEVATED}; "
                f"border: 1px solid {Colors.BORDER}; "
                f"border-radius: 10px; padding: 14px;"
            )
            tcl = QVBoxLayout(trial_card)
            tcl.setSpacing(4)

            trial_title = QLabel("🎁 Testversion aktiv")
            trial_title.setStyleSheet(
                f"color: {Colors.ACCENT}; font-size: 13px; "
                "font-weight: 700;"
            )
            tcl.addWidget(trial_title)

            days = status.get("trial_days_left", 0)
            expires = status.get("trial_expires", "?")

            trial_info = QLabel(
                f"Noch <b>{days} Tage</b> verfügbar "
                f"(bis {expires})"
            )
            trial_info.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
            )
            tcl.addWidget(trial_info)

            layout.addWidget(trial_card)

        layout.addSpacing(8)

        # ─── Key-Eingabe ───
        key_label = QLabel("Lizenz-Key:")
        key_label.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
            "font-weight: 600;"
        )
        layout.addWidget(key_label)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("SCP-XXXX-XXXX-XXXX-XXXX")
        self.key_input.setMinimumHeight(48)
        self.key_input.setStyleSheet(
            f"font-family: Consolas, monospace; font-size: 15px; "
            f"letter-spacing: 2px;"
        )
        self.key_input.textChanged.connect(self._on_text_changed)
        self.key_input.returnPressed.connect(self._activate)
        layout.addWidget(self.key_input)

        # Fehler-Label
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet(
            f"color: {Colors.DANGER}; font-size: 12px;"
        )
        self.error_lbl.setWordWrap(True)
        layout.addWidget(self.error_lbl)

        layout.addStretch()

        # ─── Buttons ───
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        if not force_activation:
            skip_btn = QPushButton("Später")
            skip_btn.setObjectName("SecondaryButton")
            skip_btn.setMinimumHeight(44)
            skip_btn.clicked.connect(self.reject)
            btn_row.addWidget(skip_btn)

        btn_row.addStretch()

        self.activate_btn = QPushButton("🔓 Aktivieren")
        self.activate_btn.setMinimumHeight(44)
        self.activate_btn.setMinimumWidth(180)
        self.activate_btn.setEnabled(False)
        self.activate_btn.clicked.connect(self._activate)
        btn_row.addWidget(self.activate_btn)

        if force_activation:
            quit_btn = QPushButton("Beenden")
            quit_btn.setObjectName("DangerButton")
            quit_btn.setMinimumHeight(44)
            quit_btn.clicked.connect(self._quit)
            btn_row.addWidget(quit_btn)

        layout.addLayout(btn_row)

        # ─── Footer ───
        footer = QLabel(
            f"Version {APP_VERSION}  ·  {APP_OWNER}\n"
            f"<a href='https://github.com/{APP_OWNER}/SystemCleanerPro' "
            f"style='color: {Colors.TEXT_MUTED};'>"
            f"github.com/{APP_OWNER}/SystemCleanerPro</a>"
        )
        footer.setOpenExternalLinks(True)
        footer.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 10px;"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def _on_text_changed(self, text: str):
        """Aktiviert Button wenn Format passt."""
        text = text.strip().upper()
        # Format: SCP-XXXX-XXXX-XXXX-XXXX = 22 Zeichen
        valid_format = (
            len(text) == 22 and
            text.startswith("SCP-") and
            text.count("-") == 4
        )
        self.activate_btn.setEnabled(valid_format)
        self.error_lbl.setText("")

    def _activate(self):
        key = self.key_input.text().strip().upper()
        if not key:
            return

        ok, msg = activate_license(key)
        if ok:
            self.activated = True
            self.accept()
        else:
            self.error_lbl.setText(msg)
            self.key_input.selectAll()
            self.key_input.setFocus()

    def _quit(self):
        QApplication.instance().quit()
        self.reject()