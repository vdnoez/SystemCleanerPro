"""Einstellungen — mit Backup-Knopf."""
import json
import shutil
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QGroupBox, QSpinBox, QTabWidget,
    QWidget, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt

from src.core.config import (
    DATA_DIR, PROJECT_ROOT, APP_NAME, APP_VERSION, APP_OWNER
)
from src.ui.theme import Colors, list_themes, set_theme
from src.ui.toast import toast

SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "theme": "slate",
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
        self.setMinimumSize(620, 560)
        self.settings = load_settings()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_design_tab(), "🎨 Design")
        self.tabs.addTab(self._build_behavior_tab(), "⚙ Verhalten")
        self.tabs.addTab(self._build_update_tab(), "🔄 Updates")
        self.tabs.addTab(self._build_data_tab(), "💾 Daten")
        self.tabs.addTab(self._build_about_tab(), "ℹ Info")
        layout.addWidget(self.tabs, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Speichern")
        save_btn.setMinimumHeight(40)
        save_btn.setMinimumWidth(140)
        save_btn.clicked.connect(self.save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _build_design_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Farbschema:"))

        self.theme_combo = QComboBox()
        for key, name in list_themes():
            self.theme_combo.addItem(name, key)

        current = self.settings.get("theme", "slate")
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current:
                self.theme_combo.setCurrentIndex(i)
                break

        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_combo, 1)
        theme_layout.addLayout(theme_row)

        hint = QLabel("💡 Theme wird sofort angewendet")
        hint.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px; "
            "font-style: italic;"
        )
        theme_layout.addWidget(hint)
        layout.addWidget(theme_group)
        layout.addStretch()
        return w

    def _build_behavior_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        group = QGroupBox("Verhalten")
        gl = QVBoxLayout(group)

        self.tray_cb = QCheckBox("Minimieren in Tray")
        self.tray_cb.setChecked(self.settings.get("minimize_to_tray", True))
        gl.addWidget(self.tray_cb)

        self.close_tray_cb = QCheckBox("Beim Schließen in Tray")
        self.close_tray_cb.setChecked(self.settings.get("close_to_tray", True))
        gl.addWidget(self.close_tray_cb)

        self.splash_cb = QCheckBox("Splash-Screen beim Start zeigen")
        self.splash_cb.setChecked(self.settings.get("show_splash", True))
        gl.addWidget(self.splash_cb)

        self.confirm_cb = QCheckBox("Vor Löschen bestätigen")
        self.confirm_cb.setChecked(self.settings.get("confirm_delete", True))
        gl.addWidget(self.confirm_cb)

        refresh_row = QHBoxLayout()
        refresh_row.addWidget(QLabel("Auto-Refresh (Sekunden):"))
        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(1, 60)
        self.refresh_spin.setValue(
            self.settings.get("auto_refresh_seconds", 2)
        )
        refresh_row.addWidget(self.refresh_spin)
        refresh_row.addStretch()
        gl.addLayout(refresh_row)

        layout.addWidget(group)
        layout.addStretch()
        return w

    def _build_update_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        group = QGroupBox("Updates")
        gl = QVBoxLayout(group)

        self.auto_check_cb = QCheckBox(
            "Automatisch nach Updates suchen (beim Start)"
        )
        self.auto_check_cb.setChecked(
            self.settings.get("auto_check_updates", True)
        )
        gl.addWidget(self.auto_check_cb)

        self.auto_install_cb = QCheckBox(
            "Updates automatisch installieren"
        )
        self.auto_install_cb.setChecked(
            self.settings.get("auto_install_updates", False)
        )
        gl.addWidget(self.auto_install_cb)

        update_hint = QLabel(
            f"💡 Updates werden über GitHub Releases bezogen.\n"
            f"    Repository: github.com/{APP_OWNER}/SystemCleanerPro"
        )
        update_hint.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px; "
            "font-style: italic;"
        )
        update_hint.setWordWrap(True)
        gl.addWidget(update_hint)

        layout.addWidget(group)
        layout.addStretch()
        return w

    def _build_data_tab(self) -> QWidget:
        """Backup + Daten-Verwaltung."""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ─── Backup ───
        backup_group = QGroupBox("💾 Backup")
        bl = QVBoxLayout(backup_group)

        backup_info = QLabel(
            "Erstellt ein ZIP-Backup deiner Einstellungen und Daten.\n"
            "Enthält: data/ (Configs, Passwort-Vault)."
        )
        backup_info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;"
        )
        backup_info.setWordWrap(True)
        bl.addWidget(backup_info)
        bl.addSpacing(6)

        backup_row = QHBoxLayout()
        backup_row.addStretch()

        backup_btn = QPushButton("💾 Backup erstellen")
        backup_btn.setMinimumHeight(42)
        backup_btn.setMinimumWidth(180)
        backup_btn.clicked.connect(self._create_backup)
        backup_row.addWidget(backup_btn)
        bl.addLayout(backup_row)

        layout.addWidget(backup_group)

        # ─── Logs ───
        logs_group = QGroupBox("📋 Logs")
        ll = QVBoxLayout(logs_group)

        logs_info = QLabel(
            "Zeigt den Log-Ordner mit Anwendungs-Protokollen."
        )
        logs_info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;"
        )
        ll.addWidget(logs_info)
        ll.addSpacing(6)

        logs_row = QHBoxLayout()
        logs_row.addStretch()

        open_logs_btn = QPushButton("📂 Log-Ordner öffnen")
        open_logs_btn.setObjectName("SecondaryButton")
        open_logs_btn.setMinimumHeight(42)
        open_logs_btn.setMinimumWidth(180)
        open_logs_btn.clicked.connect(self._open_logs)
        logs_row.addWidget(open_logs_btn)
        ll.addLayout(logs_row)

        layout.addWidget(logs_group)

        # ─── Reset ───
        reset_group = QGroupBox("⚠️ Zurücksetzen")
        rl = QVBoxLayout(reset_group)

        reset_info = QLabel(
            "Setzt alle Einstellungen auf Standard zurück.\n"
            "Vault und Configs bleiben unberührt."
        )
        reset_info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;"
        )
        reset_info.setWordWrap(True)
        rl.addWidget(reset_info)
        rl.addSpacing(6)

        reset_row = QHBoxLayout()
        reset_row.addStretch()

        reset_btn = QPushButton("🔄 Einstellungen zurücksetzen")
        reset_btn.setObjectName("DangerButton")
        reset_btn.setMinimumHeight(42)
        reset_btn.setMinimumWidth(200)
        reset_btn.clicked.connect(self._reset_settings)
        reset_row.addWidget(reset_btn)
        rl.addLayout(reset_row)

        layout.addWidget(reset_group)
        layout.addStretch()
        return w

    def _build_about_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        logo = QLabel("⚡")
        logo.setStyleSheet("font-size: 48px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        name = QLabel(APP_NAME)
        name.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; "
            "font-weight: 800;"
        )
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        ver = QLabel(f"Version {APP_VERSION}")
        ver.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)

        owner_frame = QFrame()
        owner_frame.setStyleSheet(
            f"background-color: {Colors.BG_ELEVATED}; "
            f"border: 1px solid {Colors.BORDER}; "
            "border-radius: 10px; padding: 14px;"
        )
        ofl = QVBoxLayout(owner_frame)
        ofl.setSpacing(2)

        owner_lbl = QLabel("BESITZER")
        owner_lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 10px; "
            "font-weight: 700; letter-spacing: 1.5px;"
        )
        owner_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ofl.addWidget(owner_lbl)

        owner_name = QLabel(APP_OWNER)
        owner_name.setStyleSheet(
            f"color: {Colors.ACCENT}; font-size: 18px; "
            "font-weight: 800;"
        )
        owner_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ofl.addWidget(owner_name)

        layout.addWidget(owner_frame)

        github = QLabel(
            f'<a href="https://github.com/{APP_OWNER}/SystemCleanerPro" '
            f'style="color: {Colors.ACCENT}; text-decoration: none;">'
            f'github.com/{APP_OWNER}/SystemCleanerPro</a>'
        )
        github.setOpenExternalLinks(True)
        github.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(github)

        layout.addStretch()
        return w

    # ═══════════════════════════════════════════════════════════
    def _create_backup(self):
        """Erstellt ZIP-Backup."""
        try:
            # Ziel-Datei
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            desktop = Path.home() / "Desktop"
            default_name = f"SystemCleanerPro_Backup_{timestamp}.zip"
            default_path = desktop / default_name

            target, _ = QFileDialog.getSaveFileName(
                self, "Backup speichern",
                str(default_path),
                "ZIP-Dateien (*.zip)"
            )
            if not target:
                return

            target = Path(target)

            # ZIP erstellen
            with __import__("zipfile").ZipFile(
                target, "w", __import__("zipfile").ZIP_DEFLATED
            ) as zf:
                # data/ einpacken
                for f in DATA_DIR.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(PROJECT_ROOT))

                # settings.json
                if SETTINGS_FILE.exists():
                    zf.write(SETTINGS_FILE, SETTINGS_FILE.relative_to(PROJECT_ROOT))

            size_mb = target.stat().st_size / (1024 * 1024)
            toast.success(f"Backup erstellt · {size_mb:.1f} MB")
        except Exception as e:
            toast.error(f"Backup-Fehler: {e}")

    def _open_logs(self):
        """Öffnet Log-Ordner."""
        try:
            import subprocess
            from src.core.config import LOGS_DIR
            subprocess.Popen(["explorer", str(LOGS_DIR)])
            toast.info("Log-Ordner geöffnet")
        except Exception as e:
            toast.error(f"Fehler: {e}")

    def _reset_settings(self):
        """Setzt Einstellungen zurück."""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Zurücksetzen",
            "Alle Einstellungen auf Standard zurücksetzen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if SETTINGS_FILE.exists():
                SETTINGS_FILE.unlink()
            toast.success("Einstellungen zurückgesetzt")
            self.reject()
        except Exception as e:
            toast.error(f"Fehler: {e}")

    # ═══════════════════════════════════════════════════════════
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
        toast.success("Einstellungen gespeichert")
        self.accept()