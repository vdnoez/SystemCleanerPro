"""File Shredder — mit Toasts und Empty-States."""
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QProgressDialog, QListWidget,
    QApplication, QStackedWidget
)
from PyQt6.QtCore import Qt

from src.ui.widgets import Card, PageHeader, EmptyState, LoadingState
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.dev_tools import human_size


def shred_file(path: Path, passes: int = 3) -> tuple:
    try:
        size = path.stat().st_size
        with open(path, "r+b") as f:
            for i in range(passes):
                f.seek(0)
                chunk = b"\x00" * 65536 if i % 2 == 0 else os.urandom(65536)
                written = 0
                while written < size:
                    to_write = min(65536, size - written)
                    f.write(chunk[:to_write])
                    written += to_write
                f.flush()
                os.fsync(f.fileno())
        path.unlink()
        return True, ""
    except Exception as e:
        return False, str(e)


class ShredderPage(QWidget):
    def __init__(self):
        super().__init__()
        self._files = []
        self.passes = 3

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        layout.addWidget(PageHeader(
            "🔥 File Shredder",
            "Sicheres Löschen mit mehrfachem Überschreiben — "
            "Dateien können NICHT wiederhergestellt werden"
        ))

        # Warnung
        warn_card = Card()
        warn_row = QHBoxLayout()
        warn_row.setSpacing(12)
        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 20px;")
        warn_row.addWidget(icon)
        warn_lbl = QLabel(
            "Shredderte Dateien sind ENDGÜLTIG weg. "
            "Auch mit Recovery-Tools nicht wiederherstellbar."
        )
        warn_lbl.setWordWrap(True)
        warn_lbl.setStyleSheet(
            f"color: {Colors.DANGER}; font-size: 12px;"
        )
        warn_row.addWidget(warn_lbl, 1)
        warn_card.add_widget_direct(warn_row)
        layout.addWidget(warn_card)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        add_files_btn = QPushButton("📄 Dateien hinzufügen")
        add_files_btn.setMinimumHeight(40)
        add_files_btn.clicked.connect(self.add_files)

        add_folder_btn = QPushButton("📁 Ordner hinzufügen")
        add_folder_btn.setObjectName("SecondaryButton")
        add_folder_btn.setMinimumHeight(40)
        add_folder_btn.clicked.connect(self.add_folder)

        clear_btn = QPushButton("🗑️ Liste leeren")
        clear_btn.setObjectName("SecondaryButton")
        clear_btn.setMinimumHeight(40)
        clear_btn.clicked.connect(self.clear_list)

        btn_row.addWidget(add_files_btn)
        btn_row.addWidget(add_folder_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Datei-Liste (Stacked)
        card = Card("Ausgewählte Dateien")
        self.stack = QStackedWidget()

        # Empty-State
        self.empty_state = EmptyState(
            icon="📄",
            title="Keine Dateien ausgewählt",
            message="Füge Dateien oder Ordner hinzu um sie sicher zu löschen.",
        )
        self.stack.addWidget(self.empty_state)

        # Liste
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(220)
        self.stack.addWidget(self.list_widget)

        self.stack.setCurrentIndex(0)
        card.add(self.stack)
        layout.addWidget(card)

        # Passes + Shred-Button
        passes_row = QHBoxLayout()
        passes_row.setSpacing(10)
        passes_row.addWidget(QLabel("Überschreib-Durchläufe:"))

        for n in (1, 3, 7, 35):
            btn = QPushButton(f"{n}x")
            btn.setFixedWidth(60)
            btn.setMinimumHeight(38)
            if n != 3:
                btn.setObjectName("SecondaryButton")
            btn.clicked.connect(lambda _, p=n: self.set_passes(p))
            passes_row.addWidget(btn)

        passes_row.addStretch()

        self.passes_label = QLabel("Aktuell: 3 Durchläufe")
        self.passes_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        passes_row.addWidget(self.passes_label)
        layout.addLayout(passes_row)

        self.shred_btn = QPushButton("🔥 JETZT SICHER LÖSCHEN")
        self.shred_btn.setObjectName("DangerButton")
        self.shred_btn.setMinimumHeight(48)
        self.shred_btn.clicked.connect(self.do_shred)
        layout.addWidget(self.shred_btn)

        layout.addStretch()

    def set_passes(self, n: int):
        self.passes = n
        self.passes_label.setText(f"Aktuell: {n} Durchläufe")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Dateien zum sicheren Löschen auswählen"
        )
        added = 0
        for f in files:
            p = Path(f)
            if p not in self._files:
                self._files.append(p)
                added += 1
        if added:
            toast.info(f"{added} Datei(en) hinzugefügt")
        self._refresh_list()

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Ordner zum sicheren Löschen auswählen"
        )
        if not folder:
            return
        root = Path(folder)
        added = 0
        for f in root.rglob("*"):
            if f.is_file() and f not in self._files:
                self._files.append(f)
                added += 1
        if added:
            toast.info(f"{added} Datei(en) hinzugefügt")
        self._refresh_list()

    def clear_list(self):
        if not self._files:
            return
        count = len(self._files)
        self._files.clear()
        self._refresh_list()
        toast.info(f"Liste geleert ({count} entfernt)")

    def _refresh_list(self):
        self.list_widget.clear()

        if not self._files:
            self.stack.setCurrentIndex(0)
            return

        self.stack.setCurrentIndex(1)
        total = 0
        for f in self._files:
            try:
                size = f.stat().st_size
                total += size
                self.list_widget.addItem(
                    f"{human_size(size):>10}  ·  {f}"
                )
            except OSError:
                self.list_widget.addItem(f"       ???  ·  {f}")
        if self._files:
            self.list_widget.addItem("")
            self.list_widget.addItem(
                f"── Gesamt: {human_size(total)} ──"
            )

    def do_shred(self):
        if not self._files:
            toast.warning("Keine Dateien ausgewählt")
            return

        reply = QMessageBox.warning(
            self, "Endgültig löschen?",
            f"{len(self._files)} Dateien werden mit {self.passes} "
            f"Durchläufen überschrieben.\n\n"
            f"Das kann NICHT rückgängig gemacht werden!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        progress = QProgressDialog(
            "Lösche...", "Abbrechen", 0, len(self._files), self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        ok = 0
        fail = 0
        total_size = 0

        for i, path in enumerate(self._files):
            if progress.wasCanceled():
                break
            progress.setValue(i)
            progress.setLabelText(f"Überschreibe {path.name}...")

            try:
                size = path.stat().st_size
            except OSError:
                size = 0

            success, err = shred_file(path, self.passes)
            if success:
                ok += 1
                total_size += size
            else:
                fail += 1

        progress.setValue(len(self._files))

        if ok > 0:
            toast.success(
                f"{ok} Dateien sicher gelöscht · "
                f"{human_size(total_size)} freigegeben"
            )
        if fail > 0:
            toast.error(f"{fail} Dateien fehlgeschlagen")

        self._files.clear()
        self._refresh_list()