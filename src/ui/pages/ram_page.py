"""RAM-Cleaner-Seite — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QApplication
)
from PyQt6.QtCore import QTimer

from src.ui.widgets import Card, MetricCard, PageHeader
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.ram_cleaner import get_memory_status, empty_working_sets


class RamPage(QWidget):
    def __init__(self):
        super().__init__()
        self._busy = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "💾 RAM-Cleaner",
            "Gibt Arbeitsspeicher frei — ohne Programme zu schließen"
        ))

        row = QHBoxLayout()
        row.setSpacing(14)
        self.used_card = MetricCard("Belegt", "📊")
        self.avail_card = MetricCard("Verfügbar", "✅")
        self.pagefile_card = MetricCard("Pagefile", "💿")
        for w in (self.used_card, self.avail_card, self.pagefile_card):
            row.addWidget(w)
        layout.addLayout(row)

        info_card = Card("Info")
        info = QLabel(
            "Der RAM-Cleaner leert die Working Sets aller Prozesse. "
            "Ungenutzte Speicherbereiche werden an Windows zurückgegeben. "
            "Kein Programm wird geschlossen oder beeinträchtigt."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "line-height: 1.6;"
        )
        info_card.add(info)
        layout.addWidget(info_card)

        btn_row = QHBoxLayout()
        self.clean_btn = QPushButton("🚀 RAM jetzt freigeben")
        self.clean_btn.setMinimumHeight(44)
        self.clean_btn.clicked.connect(self.do_clean)
        btn_row.addWidget(self.clean_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.result_label = QLabel("")
        self.result_label.setStyleSheet(
            f"color: {Colors.SUCCESS}; font-size: 13px; font-weight: 700;"
        )
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2000)
        self.refresh()

    def refresh(self):
        try:
            s = get_memory_status()
            if not s:
                return
            self.used_card.set_value(
                s["percent"],
                f"{s['used_gb']:.1f} GB / {s['total_gb']:.1f} GB"
            )
            self.avail_card.set_value(
                100 - s["percent"],
                f"{s['avail_gb']:.1f} GB verfügbar"
            )
            pf_pct = (
                100 * (s["pagefile_total_gb"] - s["pagefile_avail_gb"])
                / s["pagefile_total_gb"]
            ) if s["pagefile_total_gb"] else 0
            self.pagefile_card.set_value(
                pf_pct,
                f"{s['pagefile_avail_gb']:.1f} GB / "
                f"{s['pagefile_total_gb']:.1f} GB"
            )
        except RuntimeError:
            pass

    def do_clean(self):
        if self._busy:
            return
        self._busy = True

        try:
            self.clean_btn.setEnabled(False)
            self.clean_btn.setText("⏳ Optimiere RAM...")
            self.result_label.setText("")
        except RuntimeError:
            pass

        QApplication.processEvents()

        try:
            result = empty_working_sets()
        except Exception as e:
            result = {"success": False, "error": str(e)}

        try:
            self.clean_btn.setEnabled(True)
            self.clean_btn.setText("🚀 RAM jetzt freigeben")
        except RuntimeError:
            pass

        self._busy = False

        if not result.get("success"):
            toast.error(f"Fehler: {result.get('error', 'Unbekannt')}")
            return

        freed = result.get("freed_gb", 0)
        cleared = result.get("processes_cleared", 0)
        skipped = result.get("processes_skipped", 0)
        failed = result.get("processes_failed", 0)

        msg = f"✅ {cleared} Prozesse optimiert  ·  {freed:.2f} GB freigegeben"
        if skipped or failed:
            msg += f"  ·  {skipped} übersprungen, {failed} fehlgeschlagen"

        try:
            self.result_label.setText(msg)
        except RuntimeError:
            pass

        toast.success(f"RAM optimiert · {freed:.2f} GB freigegeben")
        self.refresh()