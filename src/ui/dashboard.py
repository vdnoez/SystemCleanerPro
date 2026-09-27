"""Dashboard — Fokus auf System-Score + Live-Metriken."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QGridLayout, QPushButton
)
from PyQt6.QtCore import QTimer, Qt

from src.ui.widgets import Card, CircularProgress, PageHeader
from src.ui.theme import Colors
from src.modules.performance import get_snapshot
import psutil


class LiveBar(QWidget):
    """Eine Zeile mit Label + Wert + Progress."""
    def __init__(self, label: str, icon: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)

        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 14px;")
            icon_lbl.setFixedWidth(20)
            layout.addWidget(icon_lbl)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "font-weight: 600;"
        )
        lbl.setFixedWidth(60)
        layout.addWidget(lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        layout.addWidget(self.bar, 1)

        self.value_lbl = QLabel("--%")
        self.value_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
            "font-weight: 700;"
        )
        self.value_lbl.setFixedWidth(60)
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.value_lbl)

    def set_value(self, value: float):
        self.value_lbl.setText(f"{value:.0f}%")
        self.bar.setValue(int(value))

        if value >= 85:
            self.bar.setObjectName("Danger")
        elif value >= 65:
            self.bar.setObjectName("Warning")
        else:
            self.bar.setObjectName("Success")
        self.bar.style().unpolish(self.bar)
        self.bar.style().polish(self.bar)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(20)

        layout.addWidget(PageHeader(
            "Dashboard",
            "System-Überwachung in Echtzeit"
        ))

        # ═══════ TOP: Score + Live-Bars ═══════
        top_row = QHBoxLayout()
        top_row.setSpacing(20)

        # ─── Score-Card ───
        score_card = Card("System-Score")
        score_layout = QVBoxLayout()
        score_layout.setSpacing(10)

        self.score_ring = CircularProgress()
        score_layout.addWidget(
            self.score_ring,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.score_label = QLabel("Gesamtgesundheit")
        self.score_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(self.score_label)

        score_card.add_widget_direct(score_layout)
        top_row.addWidget(score_card, 1)

        # ─── Live-Metriken ───
        live_card = Card("Live-Metriken")
        live_layout = QVBoxLayout()
        live_layout.setSpacing(6)

        self.cpu_bar = LiveBar("CPU", "🔥")
        self.ram_bar = LiveBar("RAM", "💾")
        self.disk_bar = LiveBar("DISK", "💿")
        self.net_bar = LiveBar("NETZ", "🌐")

        live_layout.addWidget(self.cpu_bar)
        live_layout.addWidget(self.ram_bar)
        live_layout.addWidget(self.disk_bar)
        live_layout.addWidget(self.net_bar)

        live_layout.addSpacing(8)

        self.info_lbl = QLabel("--")
        self.info_lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
        )
        live_layout.addWidget(self.info_lbl)

        live_card.add_widget_direct(live_layout)
        top_row.addWidget(live_card, 2)

        layout.addLayout(top_row)

        # ═══════ Quick-Actions ═══════
        actions_card = Card("Schnellzugriff")
        actions_layout = QGridLayout()
        actions_layout.setSpacing(10)

        actions = [
            ("🧹  Cleaner", self.open_cleaner),
            ("🔄  Updater", self.open_updater),
            ("💾  RAM", self.open_ram),
            ("🔥  Shredder", self.open_shredder),
            ("🩺  Health", self.open_health),
            ("📦  Software", self.open_software),
        ]

        for i, (label, callback) in enumerate(actions):
            btn = QPushButton(label)
            btn.setMinimumHeight(52)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("SecondaryButton")
            btn.clicked.connect(callback)
            actions_layout.addWidget(btn, i // 3, i % 3)

        actions_card.add_widget_direct(actions_layout)
        layout.addWidget(actions_card)

        # ═══════ System-Info ═══════
        sys_card = Card("System")
        self.sys_info_lbl = QLabel("--")
        self.sys_info_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "line-height: 1.6;"
        )
        self.sys_info_lbl.setWordWrap(True)
        sys_card.add(self.sys_info_lbl)
        layout.addWidget(sys_card)

        layout.addStretch()

        # ═══════ Timer ═══════
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1500)
        self.refresh()
        self._load_system_info()

    def refresh(self):
        try:
            s = get_snapshot()
            self.cpu_bar.set_value(s.cpu)
            self.ram_bar.set_value(s.ram)
            self.disk_bar.set_value(s.disk)

            try:
                net = psutil.net_io_counters()
                sent_mb = net.bytes_sent / (1024**2)
                recv_mb = net.bytes_recv / (1024**2)
                net_pct = min(100, (sent_mb + recv_mb) / 100)
                self.net_bar.set_value(net_pct)
                self.info_lbl.setText(
                    f"↓ {recv_mb:.0f} MB  ·  ↑ {sent_mb:.0f} MB"
                )
            except Exception:
                pass

            try:
                from src.modules.privacy import calculate_privacy_score
                privacy, _ = calculate_privacy_score()
            except Exception:
                privacy = 0

            score = int(
                (100 - s.cpu) * 0.3 +
                (100 - s.ram) * 0.3 +
                (100 - s.disk) * 0.2 +
                privacy * 0.2
            )
            self.score_ring.set_value(max(0, min(100, score)))
        except RuntimeError:
            pass

    def _load_system_info(self):
        import platform
        try:
            info = (
                f"<b>Betriebssystem:</b> {platform.system()} "
                f"{platform.release()}<br>"
                f"<b>Prozessor:</b> {platform.processor()}<br>"
                f"<b>Python:</b> {platform.python_version()}<br>"
                f"<b>Hostname:</b> {platform.node()}"
            )
            self.sys_info_lbl.setText(info)
        except Exception:
            self.sys_info_lbl.setText("System-Info nicht verfügbar")

    # ═══════════════════════════════════════════════════════════
    def _switch_to(self, page_name: str):
        try:
            win = self.window()
            if hasattr(win, "_goto_page"):
                win._goto_page(page_name)
        except Exception:
            pass

    def open_cleaner(self):
        self._switch_to("Cleaner")

    def open_updater(self):
        self._switch_to("Software-Updater")

    def open_ram(self):
        self._switch_to("RAM")

    def open_shredder(self):
        self._switch_to("Shredder")

    def open_health(self):
        self._switch_to("Health-Check")

    def open_software(self):
        self._switch_to("Software-Updater")