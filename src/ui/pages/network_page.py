"""Netzwerk-Monitor — aufgeräumt."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer
import psutil
import time

from src.ui.widgets import Card, MetricCard, PageHeader
from src.ui.theme import Colors


class NetworkPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "🌐 Netzwerk",
            "Live-Netzwerk-Auslastung und aktive Verbindungen"
        ))

        # ─── Metric-Cards ───
        row = QHBoxLayout()
        row.setSpacing(14)
        self.down_card = MetricCard("Download", "⬇️")
        self.up_card = MetricCard("Upload", "⬆️")
        row.addWidget(self.down_card)
        row.addWidget(self.up_card)
        layout.addLayout(row)

        # ─── Verbindungs-Card ───
        conn_card = Card("Aktive Verbindungen")
        self.conn_label = QLabel("Lade...")
        self.conn_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
        )
        self.conn_label.setWordWrap(True)
        conn_card.add(self.conn_label)
        layout.addWidget(conn_card)

        layout.addStretch()

        # ─── State ───
        self._last = psutil.net_io_counters()
        self._last_time = time.time()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)

    def refresh(self):
        try:
            now = psutil.net_io_counters()
            t = time.time()
            dt = t - self._last_time or 1

            down_bps = (now.bytes_recv - self._last.bytes_recv) / dt
            up_bps = (now.bytes_sent - self._last.bytes_sent) / dt

            self._last = now
            self._last_time = t

            self.down_card.set_text(
                self._fmt_speed(down_bps),
                f"Gesamt: {now.bytes_recv / (1024 ** 3):.2f} GB"
            )
            self.up_card.set_text(
                self._fmt_speed(up_bps),
                f"Gesamt: {now.bytes_sent / (1024 ** 3):.2f} GB"
            )

            conns = psutil.net_connections(kind="inet")
            established = [c for c in conns if c.status == "ESTABLISHED"]
            self.conn_label.setText(
                f"{len(established)} aktive Verbindungen  ·  "
                f"{len(conns)} total"
            )
        except RuntimeError:
            pass
        except Exception:
            try:
                self.conn_label.setText("Verbindungsdaten nicht verfügbar")
            except RuntimeError:
                pass

    @staticmethod
    def _fmt_speed(bps: float) -> str:
        for unit in ("B/s", "KB/s", "MB/s", "GB/s"):
            if bps < 1024:
                return f"{bps:.1f} {unit}"
            bps /= 1024
        return f"{bps:.1f} TB/s"