"""Windows-Health-Check-Seite — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess

from src.ui.widgets import Card, MetricCard, PageHeader, CircularProgress
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.windows_check import run_all_checks


class CheckWorker(QThread):
    progress = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)

    def run(self):
        try:
            result = run_all_checks(progress_cb=self.progress.emit)
        except Exception as e:
            result = {
                "score": 0, "results": [], "ok": 0,
                "warn": 0, "error": 0, "total": 0,
                "error": str(e),
            }
        self.finished_signal.emit(result)


class HealthPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "🩺 Windows-Health-Check",
            "Prüft 13 Aspekte deiner Systemgesundheit"
        ))

        # Score + Summary
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        score_card = Card("System-Score")
        self.score_ring = CircularProgress()
        score_card.add(self.score_ring)
        top_row.addWidget(score_card, 1)

        summary_layout = QVBoxLayout()
        summary_layout.setSpacing(12)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        self.ok_card = MetricCard("OK", "✅")
        self.warn_card = MetricCard("Warnungen", "⚠️")
        self.err_card = MetricCard("Fehler", "❌")

        cards_row.addWidget(self.ok_card)
        cards_row.addWidget(self.warn_card)
        cards_row.addWidget(self.err_card)
        summary_layout.addLayout(cards_row)

        self.status_lbl = QLabel("Klicke auf 'Scan starten' um zu beginnen")
        self.status_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
        )
        self.status_lbl.setWordWrap(True)
        summary_layout.addWidget(self.status_lbl)
        summary_layout.addStretch()

        top_row.addLayout(summary_layout, 2)
        layout.addLayout(top_row)

        # Scan-Button
        btn_row = QHBoxLayout()
        self.scan_btn = QPushButton("🔍 Scan starten")
        self.scan_btn.setMinimumHeight(46)
        self.scan_btn.setMinimumWidth(200)
        self.scan_btn.clicked.connect(self.start_scan)
        btn_row.addWidget(self.scan_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Ergebnis-Liste
        result_card = Card("Ergebnisse")
        self.result_list = QListWidget()
        self.result_list.setMinimumHeight(280)
        self.result_list.itemDoubleClicked.connect(self._on_item_double_click)
        result_card.add(self.result_list)

        hint = QLabel(
            "💡 Doppelklick auf einen Eintrag mit Fix öffnet die "
            "entsprechende Windows-Einstellung"
        )
        hint.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px; font-style: italic;"
        )
        result_card.add(hint)

        layout.addWidget(result_card)
        layout.addStretch()

    def start_scan(self):
        if self._worker and self._worker.isRunning():
            return

        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("⏳ Scanne...")
        self.result_list.clear()
        self.status_lbl.setText("Starte Scan...")

        self._worker = CheckWorker()
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_done)
        self._worker.start()

    def _on_progress(self, msg: str):
        try:
            self.status_lbl.setText(msg)
        except RuntimeError:
            pass

    def _on_done(self, result: dict):
        try:
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("🔍 Scan starten")
        except RuntimeError:
            return

        if result.get("error") and not result.get("results"):
            toast.error(f"Fehler: {result['error']}")
            return

        score = result.get("score", 0)
        self.score_ring.set_value(score)

        ok = result.get("ok", 0)
        warn = result.get("warn", 0)
        err = result.get("error", 0)
        total = result.get("total", 0)

        self.ok_card.set_text(str(ok), f"von {total} OK")
        self.warn_card.set_text(str(warn), "Warnungen")
        self.err_card.set_text(str(err), "Fehler")

        if score >= 85:
            msg = f"Ausgezeichnet! Score {score}/100"
            self.status_lbl.setText(f"✅ {msg}")
            toast.success(msg)
        elif score >= 65:
            msg = f"Okay, aber Verbesserungspotenzial. Score {score}/100"
            self.status_lbl.setText(f"⚠️  {msg}")
            toast.warning(msg)
        else:
            msg = f"Mehrere Probleme gefunden. Score {score}/100"
            self.status_lbl.setText(f"❌ {msg}")
            toast.error(msg)

        self.result_list.clear()
        for r in result.get("results", []):
            status = r.get("status", "warn")
            icon = {"ok": "✅", "warn": "⚠️", "error": "❌"}.get(status, "❔")
            name = r.get("name", "?")
            detail = r.get("detail", "")
            has_fix = r.get("fix") is not None

            text = f"{icon}  {name}\n     {detail}"
            if has_fix:
                text += "      🔧 Doppelklick für Fix"

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, r)

            if status == "error":
                item.setForeground(Qt.GlobalColor.red)
            elif status == "warn":
                item.setForeground(Qt.GlobalColor.yellow)
            else:
                item.setForeground(Qt.GlobalColor.green)

            self.result_list.addItem(item)

    def _on_item_double_click(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        fix = data.get("fix")
        if not fix:
            return

        action = fix.get("action")
        value = fix.get("value", "")

        try:
            if action == "open_url":
                subprocess.Popen(["start", value], shell=True)
                toast.info(f"Öffne: {value}")
            elif action == "open_folder":
                subprocess.Popen(["explorer", value])
                toast.info(f"Öffne Ordner")
            else:
                toast.info(f"Aktion: {action}")
        except Exception as e:
            toast.error(f"Fehler: {e}")