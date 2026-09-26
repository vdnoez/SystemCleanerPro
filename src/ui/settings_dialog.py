"""Einstellungen mit Theme-Auswahl und Auto-Update."""
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QGroupBox, QSpinBox
)

from src.core.config import DATA_DIR
from src.ui.theme import Colors, list_themes, set_theme

SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "theme": "aurora",
    "start_minimized": False,
    "minimize_to_tray": True,
    "close_to_tray": True,
    "auto_refresh_seconds": 2,
    "show_splash": True,
    "confirm_delete": True,
    "auto_check_updates": True,
    "auto_install_updates": False,
}


def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    SETTINGS_FILE.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.setMinimumSize(560, 620)
        self.settings = load_settings()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # ═══ DESIGN ═══
        design_group = QGroupBox("DESIGN")
        design_layout = QVBoxLayout(design_group)
        design_layout.setSpacing(12)

        theme_row = QHBoxLayout()
        theme_lbl = QLabel("Theme:")
        theme_lbl.setMinimumWidth(120)
        theme_row.addWidget(theme_lbl)

        self.theme_combo = QComboBox()
        for key, name in list_themes():
            self.theme_combo.addItem(name, key)

        current = self.settings.get("theme", "aurora")
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current:
                self.theme_combo.setCurrentIndex(i)
                break

        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_combo, 1)
        design_layout.addLayout(theme_row)

        hint = QLabel("💡 Theme wird sofort angewendet")
        hint.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px; "
            "font-style: italic;"
        )
        design_layout.addWidget(hint)

        layout.addWidget(design_group)

        # ═══ VERHALTEN ═══
        behavior_group = QGroupBox("VERHALTEN")
        behavior_layout = QVBoxLayout(behavior_group)
        behavior_layout.setSpacing(10)

        self.tray_cb = QCheckBox("Minimieren in Tray")
        self.tray_cb.setChecked(self.settings.get("minimize_to_tray", True))
        behavior_layout.addWidget(self.tray_cb)

        self.close_tray_cb = QCheckBox("Beim Schließen in Tray")
        self.close_tray_cb.setChecked(self.settings.get("close_to_tray", True))
        behavior_layout.addWidget(self.close_tray_cb)

        self.splash_cb = QCheckBox("Splash-Screen beim Start zeigen")
        self.splash_cb.setChecked(self.settings.get("show_splash", True))
        behavior_layout.addWidget(self.splash_cb)

        self.confirm_cb = QCheckBox("Vor Löschen bestätigen")
        self.confirm_cb.setChecked(self.settings.get("confirm_delete", True))
        behavior_layout.addWidget(self.confirm_cb)

        refresh_row = QHBoxLayout()
        refresh_row.addWidget(QLabel("Auto-Refresh (Sekunden):"))
        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(1, 60)
        self.refresh_spin.setValue(
            self.settings.get("auto_refresh_seconds", 2)
        )
        refresh_row.addWidget(self.refresh_spin)
        refresh_row.addStretch()
        behavior_layout.addLayout(refresh_row)

        layout.addWidget(behavior_group)

        # ═══ UPDATES ═══
        update_group = QGroupBox("UPDATES")
        update_layout = QVBoxLayout(update_group)
        update_layout.setSpacing(10)

        self.auto_check_cb = QCheckBox(
            "Automatisch nach Updates suchen (beim Start)"
        )
        self.auto_check_cb.setChecked(
            self.settings.get("auto_check_updates", True)
        )
        update_layout.addWidget(self.auto_check_cb)

        self.auto_install_cb = QCheckBox(
            "Updates automatisch installieren (ohne Nachfrage)"
        )
        self.auto_install_cb.setChecked(
            self.settings.get("auto_install_updates", False)
        )
        update_layout.addWidget(self.auto_install_cb)

        update_hint = QLabel(
            "💡 Updates werden über GitHub Releases bezogen."
        )
        update_hint.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px; "
            "font-style: italic;"
        )
        update_layout.addWidget(update_hint)

        layout.addWidget(update_group)

        layout.addStretch()

        # ═══ BUTTONS ═══
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Speichern")
        save_btn.clicked.connect(self.save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_theme_changed(self, index: int):
        key = self.theme_combo.itemData(index)
        if not key:
            return
        set_theme(key)
        main_win = self.parent()
        while main_win and not hasattr(main_win, "reload_theme"):
            main_win = main_win.parent()
        if main_win:
            main_win.reload_theme()

    def save(self):
        self.settings["theme"] = self.theme_combo.currentData()
        self.settings["minimize_to_tray"] = self.tray_cb.isChecked()
        self.settings["close_to_tray"] = self.close_tray_cb.isChecked()
        self.settings["show_splash"] = self.splash_cb.isChecked()
        self.settings["confirm_delete"] = self.confirm_cb.isChecked()
        self.settings["auto_refresh_seconds"] = self.refresh_spin.value()
        self.settings["auto_check_updates"] = self.auto_check_cb.isChecked()
        self.settings["auto_install_updates"] = (
            self.auto_install_cb.isChecked()
        )
        save_settings(self.settings)
        self.accept()