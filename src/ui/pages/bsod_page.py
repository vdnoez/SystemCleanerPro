"""BSOD-Analyzer — mit Toasts und Empty-States."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QApplication,
    QStackedWidget
)
from PyQt6.QtCore import Qt

from src.ui.widgets import (
    Card, MetricCard, PageHeader, EmptyState, LoadingState
)
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.bsod_analyzer import get_crash_summary, STOP_CODES


class BsodPage(QWidget):
    def __init__(self):
        super().__init__()
        self._busy = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        layout.addWidget(PageHeader(
            "🔍 BSOD-Analyzer",
            "Analysiert Bluescreen-Minidumps und zeigt Ursachen"
        ))

        # Metric-Cards
        row = QHBoxLayout()
        row.setSpacing(14)
        self.total_card = MetricCard("Crashes gesamt", "💥")
        self.latest_card = MetricCard("Letzter Crash", "🕐")
        self.top_card = MetricCard("Häufigster Code", "📊")
        for w in (self.total_card, self.latest_card, self.top_card):
            row.addWidget(w)
        layout.addLayout(row)

        info_card = Card("Info")
        info = QLabel(
            "Windows speichert bei jedem Bluescreen einen Minidump in "
            "C:\\Windows\\Minidump. Der Analyzer liest diese Dateien aus "
            "und erklärt was schiefgelaufen ist."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        info_card.add(info)
        layout.addWidget(info_card)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.scan_btn = QPushButton("🔍 Minidumps scannen")
        self.scan_btn.setMinimumHeight(42)
        self.scan_btn.clicked.connect(self.scan)

        open_btn = QPushButton("📂 Minidump-Ordner öffnen")
        open_btn.setObjectName("SecondaryButton")
        open_btn.setMinimumHeight(42)
        open_btn.clicked.connect(self.open_folder)

        btn_row.addWidget(self.scan_btn)
        btn_row.addWidget(open_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Result-Stack
        result_card = Card("Gefundene Bluescreens")
        self.stack = QStackedWidget()

        # Page 0: Empty
        self.empty_state = EmptyState(
            icon="✨",
            title="Keine Crashes gefunden",
            message="Klick auf 'Minidumps scannen' um Bluescreen-Logs zu analysieren.",
        )
        self.stack.addWidget(self.empty_state)

        # Page 1: Loading
        self.loading_state = LoadingState("Scanne Minidumps...")
        self.stack.addWidget(self.loading_state)

        # Page 2: Liste
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(280)
        self.stack.addWidget(self.list_widget)

        self.stack.setCurrentIndex(0)
        result_card.add(self.stack)
        layout.addWidget(result_card)

        layout.addStretch()

    def scan(self):
        if self._busy:
            return
        self._busy = True

        try:
            self.scan_btn.setEnabled(False)
            self.scan_btn.setText("⏳ Scanne...")
            self.stack.setCurrentIndex(1)
        except RuntimeError:
            pass
        QApplication.processEvents()

        try:
            summary = get_crash_summary()
        except Exception as e:
            summary = {"total": 0, "crashes": [], "error": str(e)}

        try:
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("🔍 Minidumps scannen")
        except RuntimeError:
            pass
        self._busy = False
        self._update_ui(summary)

    def _update_ui(self, summary: dict):
        total = summary.get("total", 0)
        crashes = summary.get("crashes", [])
        top_codes = summary.get("top_codes", [])

        try:
            self.total_card.set_text(str(total), f"{total} Minidumps")

            if crashes and crashes[0].get("date"):
                latest = crashes[0]
                self.latest_card.set_text(
                    latest["date"].split("  ")[0],
                    latest.get("name") or "Unbekannt"
                )
            else:
                self.latest_card.set_text("—", "keine Crashes")

            if top_codes:
                code, count = top_codes[0]
                name = STOP_CODES.get(code, ("Unbekannt", ""))[0]
                self.top_card.set_text(f"{count}x", name)
            else:
                self.top_card.set_text("—", "keine Daten")
        except RuntimeError:
            return

        self.list_widget.clear()

        if not crashes:
            self.empty_state = EmptyState(
                icon="✅",
                title="Keine Bluescreens gefunden",
                message=f"Dein System läuft stabil!\n"
                        f"{total} Minidumps überprüft.",
            )
            self.stack.removeWidget(self.stack.widget(0))
            self.stack.insertWidget(0, self.empty_state)
            self.stack.setCurrentIndex(0)
            toast.success("Keine Bluescreens gefunden — System stabil")
            return

        for c in crashes:
            severity_icon = {
                "critical": "🔴",
                "warning": "🟡",
                "unknown": "⚪",
            }.get(c.get("severity", "unknown"), "⚪")

            name = c.get("name") or "Unbekannter Stop-Code"
            code = c.get("stop_code_hex") or "n/a"
            desc = c.get("description") or "Keine Beschreibung verfügbar."

            text = (
                f"{severity_icon}  {c['date']}  ·  {c['filename']}  "
                f"({c['size_kb']:.1f} KB)\n"
                f"     {code}  ·  {name}\n"
                f"     → {desc}"
            )
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, str(c["path"]))
            self.list_widget.addItem(item)

        self.stack.setCurrentIndex(2)
        toast.warning(f"{len(crashes)} Bluescreen(s) gefunden")

    def open_folder(self):
        import subprocess
        try:
            subprocess.Popen(["explorer", r"C:\Windows\Minidump"])
            toast.info("Minidump-Ordner geöffnet")
        except Exception as e:
            toast.error(f"Fehler: {e}")