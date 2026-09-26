"""Dashboard-Seite mit Live-Metriken."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt

from src.ui.widgets import Card, MetricCard, CircularProgress, PageHeader
from src.ui.theme import Colors
from src.modules.performance import get_snapshot
import psutil


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        layout.addWidget(PageHeader(
            "Dashboard",
            "Live-System-Überwachung in Echtzeit"
        ))

        # ─── Row 1: Metric Cards ────────────────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        self.cpu_card = MetricCard("CPU", "🔥")
        self.ram_card = MetricCard("RAM", "💾")
        self.disk_card = MetricCard("Disk C:", "💿")
        self.net_card = MetricCard("Netzwerk", "🌐")

        for card in (self.cpu_card, self.ram_card,
                     self.disk_card, self.net_card):
            row1.addWidget(card)
        layout.addLayout(row1)

        # ─── Row 2: Privacy Score + System Info ─────────────
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        # Privacy Card
        privacy_card = Card()
        privacy_layout = QVBoxLayout()
        privacy_title = QLabel("PRIVACY-SCORE")
        privacy_title.setObjectName("CardTitle")
        privacy_layout.addWidget(privacy_title)

        self.privacy_ring = CircularProgress()
        privacy_layout.addWidget(self.privacy_ring, alignment=Qt.AlignmentFlag.AlignCenter)
        privacy_card.layout.addLayout(privacy_layout)
        row2.addWidget(privacy_card, 1)

        # System Info Card
        info_card = Card()
        info_title = QLabel("SYSTEM")
        info_title.setObjectName("CardTitle")
        info_card.layout.addWidget(info_title)

        self.info_label = QLabel("--")
        self.info_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; line-height: 1.6;"
        )
        self.info_label.setWordWrap(True)
        info_card.layout.addWidget(self.info_label)
        info_card.layout.addStretch()
        row2.addWidget(info_card, 2)

        layout.addLayout(row2)
        layout.addStretch()

        # ─── Timer ──────────────────────────────────────────
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1500)
        self.refresh()

        # System-Info nur einmal
        self._load_system_info()

    def refresh(self):
        # Snapshot
        s = get_snapshot()
        cpu_freq = psutil.cpu_freq()
        cpu_detail = f"{psutil.cpu_count()} Kerne"
        if cpu_freq:
            cpu_detail += f" · {cpu_freq.current:.0f} MHz"

        self.cpu_card.set_value(s.cpu, cpu_detail)

        vm = psutil.virtual_memory()
        self.ram_card.set_value(
            s.ram,
            f"{vm.used // (1024**3)} GB / {vm.total // (1024**3)} GB"
        )

        du = psutil.disk_usage("C:/")
        self.disk_card.set_value(
            s.disk,
            f"{du.free // (1024**3)} GB frei"
        )

        # Netzwerk
        try:
            net = psutil.net_io_counters()
            sent_mb = net.bytes_sent / (1024**2)
            recv_mb = net.bytes_recv / (1024**2)
            self.net_card.set_text(
                f"↓{recv_mb:.0f} MB",
                f"↑{sent_mb:.0f} MB gesendet"
            )
        except Exception:
            self.net_card.set_text("n/a")

        # Privacy
        try:
            from src.modules.privacy import calculate_privacy_score
            score, _ = calculate_privacy_score()
            self.privacy_ring.set_value(score)
        except Exception:
            self.privacy_ring.set_value(0)

    def _load_system_info(self):
        import platform
        try:
            info = (
                f"<b>Betriebssystem:</b> {platform.system()} {platform.release()}<br>"
                f"<b>Version:</b> {platform.version()}<br>"
                f"<b>Prozessor:</b> {platform.processor()}<br>"
                f"<b>Python:</b> {platform.python_version()}<br>"
                f"<b>Hostname:</b> {platform.node()}"
            )
            self.info_label.setText(info)
        except Exception:
            self.info_label.setText("System-Info nicht verfügbar")