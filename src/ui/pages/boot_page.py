"""Boot-Time-Analyzer — mit Toasts und Empty-States."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QApplication, QStackedWidget
)

from src.ui.widgets import (
    Card, MetricCard, PageHeader, EmptyState, LoadingState
)
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.boot_analyzer import get_boot_summary, format_ms


class BootPage(QWidget):
    def __init__(self):
        super().__init__()
        self._busy = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        layout.addWidget(PageHeader(
            "📈 Boot-Time-Analyzer",
            "Zeigt wie lange Windows zum Starten braucht"
        ))

        row = QHBoxLayout()
        row.setSpacing(14)
        self.latest_card = MetricCard("Letzter Boot", "🕐")
        self.avg_card = MetricCard("Durchschnitt", "📊")
        self.fastest_card = MetricCard("Schnellster", "⚡")
        for w in (self.latest_card, self.avg_card, self.fastest_card):
            row.addWidget(w)
        layout.addLayout(row)

        info_card = Card("Info")
        info = QLabel(
            "Windows loggt bei jedem Boot die Zeit die es braucht. "
            "Werte unter 30 Sekunden sind normal, über 60 Sekunden "
            "deuten auf zu viele Autostart-Programme hin."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        info_card.add(info)
        layout.addWidget(info_card)

        btn_row = QHBoxLayout()
        self.scan_btn = QPushButton("🔍 Boot-Daten laden")
        self.scan_btn.setMinimumHeight(42)
        self.scan_btn.clicked.connect(self.scan)
        btn_row.addWidget(self.scan_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Result-Stack
        result_card = Card("Boot-Verlauf (letzte 30 Starts)")
        self.stack = QStackedWidget()

        self.empty_state = EmptyState(
            icon="📈",
            title="Noch keine Boot-Daten",
            message="Klick auf 'Boot-Daten laden' um die letzten Startzeiten zu sehen.",
        )
        self.stack.addWidget(self.empty_state)

        self.loading_state = LoadingState("Lade Boot-Daten...")
        self.stack.addWidget(self.loading_state)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(260)
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
            self.scan_btn.setText("⏳ Lade...")
            self.stack.setCurrentIndex(1)
        except RuntimeError:
            pass
        QApplication.processEvents()

        try:
            summary = get_boot_summary()
        except Exception as e:
            summary = {"total": 0, "events": [], "error": str(e)}

        try:
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("🔍 Boot-Daten laden")
        except RuntimeError:
            pass
        self._busy = False
        self._update_ui(summary)

    def _update_ui(self, summary: dict):
        events = summary.get("events", [])

        try:
            if summary.get("latest_ms"):
                self.latest_card.set_text(
                    format_ms(summary["latest_ms"]),
                    f"{summary['total']} Boots gefunden"
                )
            else:
                self.latest_card.set_text("—", "keine Daten")

            self.avg_card.set_text(
                format_ms(summary.get("avg_ms", 0)), "Durchschnitt"
            )
            self.fastest_card.set_text(
                format_ms(summary.get("fastest_ms", 0)),
                f"Langsamster: {format_ms(summary.get('slowest_ms', 0))}"
            )
        except RuntimeError:
            return

        self.list_widget.clear()

        if not events:
            self.empty_state = EmptyState(
                icon="📭",
                title="Keine Boot-Daten gefunden",
                message="Windows loggt Boot-Performance nur wenn "
                        "Diagnose aktiviert ist.",
            )
            self.stack.removeWidget(self.stack.widget(0))
            self.stack.insertWidget(0, self.empty_state)
            self.stack.setCurrentIndex(0)
            toast.warning("Keine Boot-Daten im Event-Log")
            return

        for ev in events:
            boot = ev.get("boot_ms", 0)
            time_str = ev.get("time", "")
            if "T" in time_str:
                time_str = time_str.replace("T", "  ")[:19]

            icon = "🟢" if boot < 30000 else "🟡" if boot < 60000 else "🔴"
            text = (
                f"{icon}  {time_str}  ·  {format_ms(boot)}\n"
                f"     Hauptpfad: {format_ms(ev.get('main_path_ms', 0))}  ·  "
                f"Post-Boot: {format_ms(ev.get('post_boot_ms', 0))}"
            )
            self.list_widget.addItem(QListWidgetItem(text))

        self.stack.setCurrentIndex(2)
        toast.success(f"{len(events)} Boots geladen")