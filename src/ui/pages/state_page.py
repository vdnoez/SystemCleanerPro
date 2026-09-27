"""Download-Statistik — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QApplication, QStackedWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize

from src.ui.widgets import (
    Card, MetricCard, PageHeader, EmptyState, LoadingState
)
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.download_stats import (
    get_summary, get_release_stats, get_downloads_over_time
)


class StatsWorker(QThread):
    finished_signal = pyqtSignal(dict)

    def run(self):
        try:
            data = {
                "summary": get_summary(),
                "releases": get_release_stats(),
                "daily": get_downloads_over_time(),
                "error": "",
            }
        except Exception as e:
            data = {"summary": {}, "releases": [], "daily": [],
                    "error": str(e)}
        self.finished_signal.emit(data)


class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "📊 Download-Statistik",
            "Wie viele Leute deine App herunterladen (via GitHub)"
        ))

        # Summary-Cards
        row = QHBoxLayout()
        row.setSpacing(14)

        self.total_card = MetricCard("Gesamt", "📥")
        self.today_card = MetricCard("Heute", "📅")
        self.week_card = MetricCard("Diese Woche", "📈")
        self.latest_card = MetricCard("Neueste Version", "🏷️")

        for w in (self.total_card, self.today_card,
                  self.week_card, self.latest_card):
            row.addWidget(w)
        layout.addLayout(row)

        # Refresh-Button
        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Statistiken aktualisieren")
        self.refresh_btn.setMinimumHeight(42)
        self.refresh_btn.clicked.connect(self.refresh)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.status_lbl = QLabel("Klicke auf 'Aktualisieren'")
        self.status_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        layout.addWidget(self.status_lbl)

        # Result-Stack
        releases_card = Card("📦 Release-Historie")
        self.stack = QStackedWidget()

        self.empty_state = EmptyState(
            icon="📊",
            title="Keine Daten geladen",
            message="Klick auf 'Statistiken aktualisieren' um Download-Zahlen zu sehen.",
        )
        self.stack.addWidget(self.empty_state)

        self.loading_state = LoadingState("Lade Statistiken von GitHub...")
        self.stack.addWidget(self.loading_state)

        self.releases_list = QListWidget()
        self.releases_list.setMinimumHeight(280)
        self.releases_list.setSpacing(4)
        self.stack.addWidget(self.releases_list)

        self.stack.setCurrentIndex(0)
        releases_card.add(self.stack)
        layout.addWidget(releases_card)

        info_card = Card("ℹ️ Info")
        info = QLabel(
            "GitHub zählt jeden Download deiner .exe-Datei. "
            "Die Zahlen sind die offiziellen GitHub-Download-Zahlen."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "line-height: 1.6;"
        )
        info_card.add(info)
        layout.addWidget(info_card)

        layout.addStretch()

        self.refresh()

    def refresh(self):
        if self._worker and self._worker.isRunning():
            return

        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("⏳ Lade...")
        self.status_lbl.setText("Hole Daten von GitHub...")
        self.stack.setCurrentIndex(1)
        QApplication.processEvents()

        self._worker = StatsWorker()
        self._worker.finished_signal.connect(self._on_done)
        self._worker.start()

    def _on_done(self, data: dict):
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Statistiken aktualisieren")

        if data.get("error"):
            self.status_lbl.setText(f"❌ {data['error']}")
            toast.error(f"Statistik-Fehler: {data['error'][:60]}")
            self.stack.setCurrentIndex(0)
            return

        summary = data.get("summary", {})
        releases = data.get("releases", [])

        # Cards
        self.total_card.set_text(
            f"{summary.get('total', 0):,}".replace(",", "."),
            f"{summary.get('release_count', 0)} Releases"
        )
        self.today_card.set_text(
            f"{summary.get('today', 0):,}".replace(",", "."),
            "Downloads heute"
        )
        self.week_card.set_text(
            f"{summary.get('week', 0):,}".replace(",", "."),
            "letzte 7 Tage"
        )
        self.latest_card.set_text(
            summary.get("latest_version", "—"),
            f"{summary.get('latest_downloads', 0)} Downloads"
        )

        self.status_lbl.setText(
            f"✅ {summary.get('total', 0)} Downloads aus "
            f"{summary.get('release_count', 0)} Releases"
        )

        self.releases_list.clear()

        if not releases:
            self.empty_state = EmptyState(
                icon="📭",
                title="Keine Releases gefunden",
                message="Es sind noch keine Releases auf GitHub verfügbar.",
            )
            self.stack.removeWidget(self.stack.widget(0))
            self.stack.insertWidget(0, self.empty_state)
            self.stack.setCurrentIndex(0)
            toast.warning("Keine Releases gefunden")
            return

        for rel in releases:
            tag = rel["tag"]
            date = rel["published"]
            days = rel["days_ago"]
            count = rel["total_downloads"]

            widget = QWidget()
            widget.setMinimumHeight(56)
            row = QHBoxLayout(widget)
            row.setContentsMargins(12, 8, 12, 8)
            row.setSpacing(12)

            icon_lbl = QLabel("🏷️")
            icon_lbl.setStyleSheet("font-size: 18px;")
            icon_lbl.setFixedWidth(30)
            row.addWidget(icon_lbl)

            info_col = QVBoxLayout()
            info_col.setSpacing(2)

            tag_lbl = QLabel(tag)
            tag_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
                "font-weight: 700;"
            )
            info_col.addWidget(tag_lbl)

            date_str = date
            if days == 0:
                date_str += " (heute)"
            elif days == 1:
                date_str += " (gestern)"
            else:
                date_str += f" (vor {days} Tagen)"

            date_lbl = QLabel(date_str)
            date_lbl.setStyleSheet(
                f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
            )
            info_col.addWidget(date_lbl)

            row.addLayout(info_col, 1)

            count_lbl = QLabel(f"📥 {count:,}".replace(",", "."))
            count_lbl.setStyleSheet(
                f"color: {Colors.ACCENT}; font-size: 15px; "
                "font-weight: 800;"
            )
            count_lbl.setFixedWidth(120)
            count_lbl.setAlignment(Qt.AlignmentFlag.AlignRight |
                                   Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(count_lbl)

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 60))
            self.releases_list.addItem(item)
            self.releases_list.setItemWidget(item, widget)

        self.stack.setCurrentIndex(2)
        toast.success(f"{summary.get('total', 0)} Downloads geladen")