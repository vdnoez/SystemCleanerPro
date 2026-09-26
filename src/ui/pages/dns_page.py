"""DNS-Leak-Tester — aufgeräumt."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.ui.widgets import Card, MetricCard, PageHeader
from src.ui.theme import Colors
from src.modules.dns_tester import run_full_test, identify_dns


class DnsWorker(QThread):
    progress = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)

    def run(self):
        try:
            result = run_full_test(progress_cb=self.progress.emit)
        except Exception as e:
            result = {"error": str(e)}
        self.finished_signal.emit(result)


class DnsPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        layout.addWidget(PageHeader(
            "🌐 DNS-Leak-Tester",
            "Prüft DNS-Konfiguration und ob deine Anfragen leaken"
        ))

        # ─── Metric-Cards ───
        row = QHBoxLayout()
        row.setSpacing(14)
        self.ip_card = MetricCard("Öffentliche IP", "🌍")
        self.isp_card = MetricCard("Provider", "📡")
        self.country_card = MetricCard("Standort", "📍")
        for w in (self.ip_card, self.isp_card, self.country_card):
            row.addWidget(w)
        layout.addLayout(row)

        # ─── Info-Card ───
        info_card = Card("Info")
        info = QLabel(
            "DNS-Leaks passieren wenn deine DNS-Anfragen trotz VPN "
            "über deinen echten Provider gehen. Dieser Test zeigt "
            "dir deine DNS-Server und prüft ob sie sicher sind."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        info_card.add(info)
        layout.addWidget(info_card)

        # ─── Button ───
        btn_row = QHBoxLayout()
        self.scan_btn = QPushButton("🔍 DNS-Test starten")
        self.scan_btn.setMinimumHeight(44)
        self.scan_btn.clicked.connect(self.scan)
        btn_row.addWidget(self.scan_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ─── Status ───
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            f"color: {Colors.ACCENT}; font-size: 13px;"
        )
        layout.addWidget(self.status_label)

        # ─── Ergebnis ───
        result_card = Card("Ergebnisse")
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(240)
        result_card.add(self.list_widget)
        layout.addWidget(result_card)

        layout.addStretch()

    def scan(self):
        if self._worker and self._worker.isRunning():
            return

        try:
            self.scan_btn.setEnabled(False)
            self.scan_btn.setText("⏳ Teste...")
            self.status_label.setText("Starte Tests...")
        except RuntimeError:
            pass

        self.list_widget.clear()
        self._worker = DnsWorker()
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_done)
        self._worker.start()

    def _on_progress(self, msg: str):
        try:
            self.status_label.setText(msg)
        except RuntimeError:
            pass

    def _on_done(self, result: dict):
        try:
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("🔍 DNS-Test starten")
            self.status_label.setText("✅ Test abgeschlossen")
        except RuntimeError:
            return

        if result.get("error"):
            self.list_widget.addItem(f"❌ Fehler: {result['error']}")
            return

        pub = result.get("public_ip", {})
        try:
            if pub.get("ip"):
                self.ip_card.set_text(pub["ip"], pub.get("asn", ""))
                isp = pub.get("isp", "?")
                self.isp_card.set_text(
                    (isp[:20] + "...") if len(isp) > 20 else isp,
                    "Internet-Provider"
                )
                self.country_card.set_text(
                    pub.get("country", "?"), pub.get("city", "")
                )
            else:
                self.ip_card.set_text("—", "nicht ermittelbar")
        except RuntimeError:
            return

        dns_servers = result.get("dns_servers", {})
        self.list_widget.addItem("═══ DNS-SERVER ═══")
        self.list_widget.addItem("")

        if not dns_servers:
            self.list_widget.addItem("⚠️  Keine DNS-Server gefunden.")
        else:
            for adapter, servers in dns_servers.items():
                for srv in servers:
                    provider = identify_dns(srv)
                    if provider in ("Cloudflare", "Google", "Quad9"):
                        icon = "✅"
                    elif provider == "Router (lokal)":
                        icon = "🏠"
                    elif provider == "Unbekannt":
                        icon = "⚠️"
                    else:
                        icon = "ℹ️"
                    self.list_widget.addItem(
                        f"{icon}  [{adapter}]  {srv}  →  {provider}"
                    )

        self.list_widget.addItem("")
        self.list_widget.addItem("═══ DNS-AUFLÖSUNG ═══")
        self.list_widget.addItem("")

        res = result.get("resolution", {}).get("tests", [])
        for t in res:
            if t.get("ok"):
                self.list_widget.addItem(
                    f"✅  {t['domain']}  →  {t['resolved_ip']}  "
                    f"({t['duration_ms']} ms)"
                )
            else:
                self.list_widget.addItem(
                    f"❌  {t['domain']}  →  Fehler: {t.get('error', '?')}"
                )