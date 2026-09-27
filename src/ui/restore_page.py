"""Wiederherstellungspunkte — Sicherung vor kritischen Aktionen."""
import subprocess
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QApplication,
    QInputDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize

from src.ui.widgets import Card, PageHeader
from src.ui.theme import Colors


# ═══════════════════════════════════════════════════════════════
def _run_ps(cmd: str, timeout: int = 60) -> tuple:
    """Führt PowerShell aus."""
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def list_restore_points() -> list:
    """Listet alle Wiederherstellungspunkte."""
    success, out, err = _run_ps(
        "Get-ComputerRestorePoint | "
        "Select-Object SequenceNumber,Description,CreationTime | "
        "ConvertTo-Json -Compress",
        timeout=20
    )
    if not success or not out:
        return []

    import json
    try:
        data = json.loads(out)
    except Exception:
        return []

    if isinstance(data, dict):
        data = [data]

    results = []
    for rp in data:
        try:
            # CreationTime parsen (WMI-Format)
            ct = rp.get("CreationTime", "")
            date_str = "?"
            if ct:
                # Format: 20260927023000.000000-000
                if len(ct) >= 14:
                    d = ct[:14]
                    date_str = (f"{d[6:8]}.{d[4:6]}.{d[0:4]}  "
                                f"{d[8:10]}:{d[10:12]}")

            results.append({
                "seq": rp.get("SequenceNumber", 0),
                "desc": rp.get("Description", "Ohne Beschreibung"),
                "date": date_str,
            })
        except Exception:
            continue

    # Sortieren (neueste zuerst)
    results.sort(key=lambda x: x["seq"], reverse=True)
    return results


def create_restore_point(description: str) -> tuple:
    """Erstellt neuen Wiederherstellungspunkt."""
    safe_desc = description.replace('"', '\\"')[:200]
    cmd = (
        f'Checkpoint-Computer -Description "{safe_desc}" '
        f'-RestorePointType "MODIFY_SETTINGS"'
    )
    success, out, err = _run_ps(cmd, timeout=180)
    if success:
        return True, f"✅ Punkt erstellt: {description}"
    return False, err or "Fehler beim Erstellen"


def enable_system_restore() -> tuple:
    """Aktiviert Systemwiederherstellung auf C:\\."""
    success, out, err = _run_ps(
        "Enable-ComputerRestore -Drive 'C:\\'", timeout=30
    )
    if success:
        return True, "✅ Systemwiederherstellung aktiviert"
    return False, err or "Fehler beim Aktivieren"


def get_restore_status() -> tuple:
    """Prüft ob Systemwiederherstellung aktiviert ist."""
    success, out, err = _run_ps(
        "(Get-ComputerRestorePoint -ErrorAction SilentlyContinue | "
        "Measure-Object).Count",
        timeout=15
    )
    count = int(out) if out.strip().isdigit() else -1
    return count >= 0, str(count)


# ═══════════════════════════════════════════════════════════════
# WORKER
# ═══════════════════════════════════════════════════════════════
class LoadWorker(QThread):
    finished_signal = pyqtSignal(list)

    def run(self):
        try:
            self.finished_signal.emit(list_restore_points())
        except Exception:
            self.finished_signal.emit([])


class CreateWorker(QThread):
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, description: str):
        super().__init__()
        self.description = description

    def run(self):
        ok, msg = create_restore_point(self.description)
        self.finished_signal.emit(ok, msg)


# ═══════════════════════════════════════════════════════════════
# SEITE
# ═══════════════════════════════════════════════════════════════
class RestorePage(QWidget):
    def __init__(self):
        super().__init__()
        self._load_worker = None
        self._create_worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "🛡️ Wiederherstellungspunkte",
            "Sicherungspunkte erstellen — vor großen Änderungen"
        ))

        # ─── Info-Banner ───
        info_card = Card()
        info_row = QHBoxLayout()
        info_row.setSpacing(14)

        icon = QLabel("💡")
        icon.setStyleSheet("font-size: 22px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_row.addWidget(icon)

        info_text = QLabel(
            "<b>Was ist das?</b><br>"
            "Ein Wiederherstellungspunkt speichert den aktuellen "
            "System-Zustand (Registry, Treiber, System-Dateien). "
            "Bei Problemen kannst du Windows damit auf diesen Punkt "
            "zurücksetzen — <b>ohne deine Dateien zu verlieren</b>.<br><br>"
            "<b>Tipp:</b> Erstelle einen Punkt bevor du den Cleaner, "
            "Shredder oder große System-Änderungen ausführst."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "line-height: 1.6;"
        )
        info_row.addWidget(info_text, 1)
        info_card.add_widget_direct(info_row)
        layout.addWidget(info_card)

        # ─── Buttons ───
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.create_btn = QPushButton("➕  Neuen Punkt erstellen")
        self.create_btn.setMinimumHeight(44)
        self.create_btn.clicked.connect(self.create_point)
        btn_row.addWidget(self.create_btn)

        self.refresh_btn = QPushButton("🔄  Aktualisieren")
        self.refresh_btn.setObjectName("SecondaryButton")
        self.refresh_btn.setMinimumHeight(44)
        self.refresh_btn.clicked.connect(self.refresh)
        btn_row.addWidget(self.refresh_btn)

        self.enable_btn = QPushButton("⚙  Systemwiederherstellung aktivieren")
        self.enable_btn.setObjectName("SecondaryButton")
        self.enable_btn.setMinimumHeight(44)
        self.enable_btn.clicked.connect(self.enable_restore)
        btn_row.addWidget(self.enable_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ─── Status ───
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        layout.addWidget(self.status_lbl)

        # ─── Liste ───
        list_card = Card("📋 Vorhandene Wiederherstellungspunkte")
        self.points_list = QListWidget()
        self.points_list.setMinimumHeight(320)
        self.points_list.setSpacing(4)
        list_card.add(self.points_list)
        layout.addWidget(list_card)

        layout.addStretch()

        # Erster Refresh
        self.refresh()

    # ═══════════════════════════════════════════════════════════
    def refresh(self):
        if self._load_worker and self._load_worker.isRunning():
            return

        self.status_lbl.setText("⏳ Lade Wiederherstellungspunkte...")
        self.points_list.clear()
        QApplication.processEvents()

        self._load_worker = LoadWorker()
        self._load_worker.finished_signal.connect(self._on_loaded)
        self._load_worker.start()

    def _on_loaded(self, points: list):
        self.points_list.clear()

        if not points:
            self.points_list.addItem(
                "ℹ️  Keine Wiederherstellungspunkte gefunden.\n"
                "     Klick auf '➕ Neuen Punkt erstellen' "
                "um einen anzulegen."
            )
            self.status_lbl.setText(
                "Systemwiederherstellung möglicherweise deaktiviert."
            )
            return

        self.status_lbl.setText(
            f"✅ {len(points)} Wiederherstellungspunkte gefunden"
        )

        for p in points:
            widget = QWidget()
            widget.setMinimumHeight(60)
            row = QHBoxLayout(widget)
            row.setContentsMargins(14, 8, 14, 8)
            row.setSpacing(14)

            # Icon
            icon_lbl = QLabel("📍")
            icon_lbl.setStyleSheet("font-size: 20px;")
            icon_lbl.setFixedWidth(30)
            row.addWidget(icon_lbl)

            # Info
            info_col = QVBoxLayout()
            info_col.setSpacing(2)

            desc_lbl = QLabel(p["desc"])
            desc_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
                "font-weight: 700;"
            )
            info_col.addWidget(desc_lbl)

            meta_lbl = QLabel(f"📅 {p['date']}   ·   Punkt #{p['seq']}")
            meta_lbl.setStyleSheet(
                f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
            )
            info_col.addWidget(meta_lbl)

            row.addLayout(info_col, 1)

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 64))
            self.points_list.addItem(item)
            self.points_list.setItemWidget(item, widget)

    # ═══════════════════════════════════════════════════════════
    def create_point(self):
        # Standard-Beschreibung
        default_desc = (
            f"Cleaner Pro  ·  {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        desc, ok = QInputDialog.getText(
            self, "Wiederherstellungspunkt erstellen",
            "Beschreibung:",
            text=default_desc
        )
        if not ok or not desc.strip():
            return

        desc = desc.strip()

        reply = QMessageBox.question(
            self, "Punkt erstellen",
            f"Wiederherstellungspunkt erstellen?\n\n"
            f"Name: {desc}\n\n"
            f"Das dauert ca. 30-60 Sekunden.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.status_lbl.setText("⏳ Erstelle Wiederherstellungspunkt...")
        self.create_btn.setEnabled(False)
        self.create_btn.setText("⏳ Erstelle...")

        self._create_worker = CreateWorker(desc)
        self._create_worker.finished_signal.connect(self._on_created)
        self._create_worker.start()

    def _on_created(self, ok: bool, msg: str):
        self.create_btn.setEnabled(True)
        self.create_btn.setText("➕  Neuen Punkt erstellen")

        if ok:
            QMessageBox.information(self, "Erfolg", msg)
            self.refresh()
        else:
            QMessageBox.warning(
                self, "Fehler",
                f"{msg}\n\n"
                "Tipp: Systemwiederherstellung muss aktiviert sein.\n"
                "Klick auf '⚙ Systemwiederherstellung aktivieren'."
            )

    def enable_restore(self):
        reply = QMessageBox.question(
            self, "Aktivieren",
            "Systemwiederherstellung auf Laufwerk C:\\ aktivieren?\n\n"
            "Das belegt ca. 1-5 GB Speicher für Wiederherstellungspunkte.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        ok, msg = enable_system_restore()
        if ok:
            QMessageBox.information(
                self, "Erfolg",
                f"{msg}\n\nDu kannst jetzt Punkte erstellen."
            )
        else:
            QMessageBox.warning(self, "Fehler", msg)