"""System-Info-Seite — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.ui.widgets import Card, PageHeader
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.system_info import get_all_info


class InfoRow(QWidget):
    """Zeile mit Label + Wert."""
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(16)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 12px; "
            "font-weight: 600;"
        )
        lbl.setMinimumWidth(140)
        layout.addWidget(lbl)

        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
            "font-weight: 600;"
        )
        self.value_lbl.setWordWrap(True)
        self.value_lbl.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.value_lbl, 1)


class InfoWorker(QThread):
    finished_signal = pyqtSignal(dict)

    def run(self):
        try:
            self.finished_signal.emit(get_all_info())
        except Exception as e:
            self.finished_signal.emit({"error": str(e)})


class SysInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "🖥️ System-Information",
            "Hardware & Betriebssystem auf einen Blick"
        ))

        # Refresh-Button
        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄  Aktualisieren")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.clicked.connect(self.refresh)
        btn_row.addWidget(self.refresh_btn)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 12px;"
        )
        btn_row.addWidget(self.status_lbl)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Grid für Cards
        self.grid = QGridLayout()
        self.grid.setSpacing(16)

        # CPU
        self.cpu_card = Card("🔲  Prozessor (CPU)")
        self.cpu_content = QVBoxLayout()
        self.cpu_content.setSpacing(2)
        self.cpu_card.add_widget_direct(self.cpu_content)

        # RAM
        self.ram_card = Card("💾  Arbeitsspeicher (RAM)")
        self.ram_content = QVBoxLayout()
        self.ram_content.setSpacing(2)
        self.ram_card.add_widget_direct(self.ram_content)

        # GPU
        self.gpu_card = Card("🎮  Grafikkarte (GPU)")
        self.gpu_content = QVBoxLayout()
        self.gpu_content.setSpacing(2)
        self.gpu_card.add_widget_direct(self.gpu_content)

        # OS
        self.os_card = Card("🪟  Betriebssystem")
        self.os_content = QVBoxLayout()
        self.os_content.setSpacing(2)
        self.os_card.add_widget_direct(self.os_content)

        # Mainboard
        self.board_card = Card("🔧  Mainboard & BIOS")
        self.board_content = QVBoxLayout()
        self.board_content.setSpacing(2)
        self.board_card.add_widget_direct(self.board_content)

        # Disks
        self.disks_card = Card("💿  Laufwerke")
        self.disks_content = QVBoxLayout()
        self.disks_content.setSpacing(2)
        self.disks_card.add_widget_direct(self.disks_content)

        # Grid-Layout
        self.grid.addWidget(self.cpu_card, 0, 0)
        self.grid.addWidget(self.ram_card, 0, 1)
        self.grid.addWidget(self.gpu_card, 1, 0)
        self.grid.addWidget(self.os_card, 1, 1)
        self.grid.addWidget(self.board_card, 2, 0, 1, 2)
        self.grid.addWidget(self.disks_card, 3, 0, 1, 2)

        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)

        layout.addLayout(self.grid)
        layout.addStretch()

        # Initial laden
        self.refresh()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _add_rows(self, layout, rows: list):
        for label, value in rows:
            if value:
                layout.addWidget(InfoRow(label, str(value)))

    def refresh(self):
        if self._worker and self._worker.isRunning():
            return

        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("⏳ Lade...")
        self.status_lbl.setText("Sammle System-Informationen...")
        QApplication.processEvents()

        self._worker = InfoWorker()
        self._worker.finished_signal.connect(self._on_done)
        self._worker.start()

    def _on_done(self, info: dict):
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄  Aktualisieren")

        if info.get("error"):
            self.status_lbl.setText(f"❌ {info['error']}")
            toast.error(f"System-Info: {info['error'][:60]}")
            return

        self.status_lbl.setText("✅ Informationen aktualisiert")
        self._update_ui(info)
        toast.success("System-Informationen aktualisiert")

    def _update_ui(self, info: dict):
        # ═══ CPU ═══
        self._clear_layout(self.cpu_content)
        cpu = info.get("cpu", {})
        self._add_rows(self.cpu_content, [
            ("Modell", cpu.get("name", "—")),
            ("Kerne", f"{cpu.get('cores_physical', '?')} physisch "
                      f"/ {cpu.get('cores_logical', '?')} logisch"),
            ("Takt", f"{cpu.get('freq_current', '?')}  "
                     f"(max. {cpu.get('freq_max', '?')})"),
            ("Architektur", cpu.get("arch", "—")),
        ])

        # ═══ RAM ═══
        self._clear_layout(self.ram_content)
        ram = info.get("ram", {})
        percent = ram.get("percent", 0)
        self._add_rows(self.ram_content, [
            ("Größe", f"{ram.get('total_gb', '?')} GB"),
            ("Verfügbar", f"{ram.get('available_gb', '?')} GB "
                          f"({100 - percent:.0f}%)"),
            ("Typ", ram.get("type", "—")),
            ("Geschwindigkeit", ram.get("speed", "—")),
            ("Slots", f"{ram.get('slots_used', '?')} von "
                      f"{ram.get('slots_total', '?')} belegt"),
        ])

        # ═══ GPU ═══
        self._clear_layout(self.gpu_content)
        gpus = info.get("gpu", [])
        if not gpus:
            self.gpu_content.addWidget(InfoRow("Status", "Keine GPU erkannt"))
        else:
            for i, gpu in enumerate(gpus):
                if i > 0:
                    self.gpu_content.addSpacing(10)
                vram = gpu.get('vram_gb', 0)
                self._add_rows(self.gpu_content, [
                    ("Modell", gpu.get("name", "—")),
                    ("VRAM", f"{vram} GB" if vram else "—"),
                    ("Treiber", gpu.get("driver", "—")),
                    ("Treiber-Datum", gpu.get("driver_date", "—")),
                ])

        # ═══ OS ═══
        self._clear_layout(self.os_content)
        os_info = info.get("os", {})
        act_status = ("✅ Aktiviert" if os_info.get("activated")
                      else "⚠️ Nicht aktiviert")
        self._add_rows(self.os_content, [
            ("Name", os_info.get("name", "—")),
            ("Version", os_info.get("version", "—")),
            ("Build", os_info.get("build", "—")),
            ("Architektur", os_info.get("arch", "—")),
            ("Aktivierung", act_status),
            ("Hostname", os_info.get("hostname", "—")),
        ])

        # ═══ Mainboard ═══
        self._clear_layout(self.board_content)
        board = info.get("board", {})
        b = board.get("board", {})
        bios = board.get("bios", {})
        self._add_rows(self.board_content, [
            ("Mainboard", f"{b.get('manufacturer', '?')}  "
                          f"{b.get('product', '?')}"),
            ("BIOS-Hersteller", bios.get("manufacturer", "—")),
            ("BIOS-Version", bios.get("version", "—")),
            ("BIOS-Datum", bios.get("date", "—")),
        ])

        # ═══ Disks ═══
        self._clear_layout(self.disks_content)
        disks = info.get("disks", [])
        if not disks:
            self.disks_content.addWidget(InfoRow("Status", "Keine Laufwerke"))
        else:
            for disk in disks:
                device = disk.get("device", "?")
                total = disk.get("total_gb", 0)
                free = disk.get("free_gb", 0)
                used_pct = disk.get("percent", 0)
                fstype = disk.get("fstype", "?")
                self.disks_content.addWidget(InfoRow(
                    f"{device}  ({fstype})",
                    f"{total} GB  ·  {free} GB frei  ·  "
                    f"{used_pct:.0f}% belegt"
                ))