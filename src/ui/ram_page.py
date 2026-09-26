"""RAM-Cleaner-Seite."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import QTimer

from src.ui.widgets import Card, MetricCard, PageHeader
from src.ui.theme import Colors
from src.modules.ram_cleaner import get_memory_status, empty_working_sets


class RamPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        layout.addWidget(PageHeader(
            "💾 RAM-Cleaner",
            "Gibt Arbeitsspeicher frei — ohne Programme zu schließen"
        ))

        # Metric Cards
        row = QHBoxLayout()
        row.setSpacing(16)
        self.used_card = MetricCard("Belegt", "📊")
        self.avail_card = MetricCard("Verfügbar", "✅")
        self.pagefile_card = MetricCard("Pagefile", "💿")
        for w in (self.used_card, self.avail_card, self.pagefile_card):
            row.addWidget(w)
        layout.addLayout(row)

        # Info Card
        info_card = Card("Info")
        info = QLabel(
            "Der RAM-Cleaner leert die Working Sets aller Prozesse. "
            "Das bedeutet: ungenutzte Speicherbereiche werden an Windows "
            "zurückgegeben und stehen wieder zur Verfügung. "
            "Kein Programm wird geschlossen oder beeinträchtigt."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; "
            "line-height: 1.6;"
        )
        info_card.add(info)
        layout.addWidget(info_card)

        # Action
        btn_row = QHBoxLayout()
        self.clean_btn = QPushButton("🚀 RAM jetzt freigeben")
        self.clean_btn.setMinimumHeight(45)
        self.clean_btn.clicked.connect(self.do_clean)
        btn_row.addWidget(self.clean_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Result
        self.result_label = QLabel("")
        self.result_label.setStyleSheet(
            f"color: {Colors.SUCCESS}; font-size: 14px; font-weight: 600;"
        )
        layout.addWidget(self.result_label)

        layout.addStretch()

        # Auto-Refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2000)
        self.refresh()

    def refresh(self):
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
        pagefile_pct = (100 * (s["pagefile_total_gb"] - s["pagefile_avail_gb"])
                        / s["pagefile_total_gb"]) if s["pagefile_total_gb"] else 0
        self.pagefile_card.set_value(
            pagefile_pct,
            f"{s['pagefile_avail_gb']:.1f} GB / "
            f"{s['pagefile_total_gb']:.1f} GB"
        )

    def do_clean(self):
        self.clean_btn.setEnabled(False)
        self.clean_btn.setText("⏳ Leere Working Sets...")
        self.result_label.setText("")

        QTimer.singleShot(100, self._run_clean)

    def _run_clean(self):
        result = empty_working_sets()

        if not result.get("success"):
            QMessageBox.warning(self, "Fehler",
                result.get("error", "Unbekannter Fehler"))
            self.clean_btn.setEnabled(True)
            self.clean_btn.setText("🚀 RAM jetzt freigeben")
            return

        freed = result.get("freed_gb", 0)
        cleared = result.get("processes_cleared", 0)

        self.result_label.setText(
            f"✅ {cleared} Prozesse optimiert  ·  "
            f"{freed:.2f} GB freigegeben"
        )

        self.clean_btn.setEnabled(True)
        self.clean_btn.setText("🚀 RAM jetzt freigeben")
        self.refresh()