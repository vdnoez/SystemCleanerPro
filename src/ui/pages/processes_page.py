"""Prozess-Manager — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit
)
from PyQt6.QtCore import QTimer
import psutil

from src.ui.widgets import Card, PageHeader
from src.ui.theme import Colors
from src.ui.toast import toast


class ProcessesPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        layout.addWidget(PageHeader(
            "⚙️ Prozesse",
            "Top-Verbraucher und Prozess-Verwaltung"
        ))

        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Prozess suchen...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self._filter_table)
        search_row.addWidget(self.search_input, 1)
        layout.addLayout(search_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.refresh)

        kill_btn = QPushButton("⛔ Beenden")
        kill_btn.setObjectName("DangerButton")
        kill_btn.setMinimumHeight(40)
        kill_btn.clicked.connect(self.kill_selected)

        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(kill_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        table_card = Card("Top 30 Prozesse (nach RAM)")
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["PID", "Name", "CPU %", "RAM (MB)"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setMinimumHeight(360)
        table_card.add(self.table)
        layout.addWidget(table_card)

        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(3000)
        self.refresh()

    def refresh(self):
        procs = []
        for p in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_info"]
        ):
            try:
                info = p.info
                mem_mb = (info["memory_info"].rss / (1024 ** 2)
                          if info["memory_info"] else 0)
                procs.append((
                    info["pid"], info["name"] or "?",
                    info["cpu_percent"] or 0.0, mem_mb
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        procs.sort(key=lambda x: x[3], reverse=True)
        top = procs[:30]

        self.table.setRowCount(len(top))
        for row, (pid, name, cpu, mem) in enumerate(top):
            self.table.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{cpu:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{mem:.1f}"))

        if hasattr(self, "search_input"):
            self._filter_table(self.search_input.text())

    def _filter_table(self, text: str):
        text = text.lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)

    def kill_selected(self):
        row = self.table.currentRow()
        if row < 0:
            toast.warning("Bitte erst Prozess auswählen")
            return

        pid_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        if not pid_item:
            return

        pid = int(pid_item.text())
        name = name_item.text() if name_item else "?"

        reply = QMessageBox.question(
            self, "Prozess beenden",
            f"'{name}' (PID {pid}) wirklich beenden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                psutil.Process(pid).terminate()
                toast.success(f"'{name}' beendet")
                self.refresh()
            except Exception as e:
                toast.error(f"Fehler: {e}")