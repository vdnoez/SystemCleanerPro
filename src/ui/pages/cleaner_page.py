"""Cleaner-Seite — mit Toasts und EmptyStates."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QMessageBox, QProgressDialog,
    QCheckBox, QApplication, QStackedWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path

from src.ui.widgets import Card, PageHeader, EmptyState, LoadingState
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.dev_tools import (
    find_dev_temp, dir_size, human_size, delete_path
)
from src.core.config_loader import get_windows_temp_dirs, reload_all


class ScanWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, mode: str):
        super().__init__()
        self.mode = mode

    def run(self):
        results = []
        if self.mode == "windows":
            for d in get_windows_temp_dirs():
                self.progress.emit(f"Scanne {d.name}...")
                size = dir_size(d)
                if size > 0:
                    results.append((d, size, "Windows-Temp"))
        elif self.mode == "dev":
            home = Path.home()
            self.progress.emit(f"Scanne {home}...")
            for path, size in find_dev_temp(home):
                if size > 1024 * 1024:
                    results.append((path, size, "Dev-Ordner"))
        self.finished.emit(results)


class CleanerPage(QWidget):
    def __init__(self):
        super().__init__()
        self._found = []
        self._worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        layout.addWidget(PageHeader(
            "🧹 Cleaner",
            "Findet und entfernt unnötige Dateien — sicher & rückholbar"
        ))

        # Scan-Buttons
        scan_row = QHBoxLayout()
        scan_row.setSpacing(10)

        win_btn = QPushButton("🗑️  Windows Temp scannen")
        win_btn.setMinimumHeight(42)
        win_btn.clicked.connect(lambda: self.start_scan("windows"))

        dev_btn = QPushButton("💻 Dev-Ordner scannen")
        dev_btn.setObjectName("SecondaryButton")
        dev_btn.setMinimumHeight(42)
        dev_btn.clicked.connect(lambda: self.start_scan("dev"))

        scan_row.addWidget(win_btn)
        scan_row.addWidget(dev_btn)
        scan_row.addStretch()
        layout.addLayout(scan_row)

        # Status
        self.info_label = QLabel("Bereit. Klick auf 'Scannen'.")
        self.info_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
        )
        layout.addWidget(self.info_label)

        # Ergebnis-Bereich (Stacked: Liste / Empty / Loading)
        result_card = Card("Gefundene Ordner")
        self.result_stack = QStackedWidget()

        # Page 0: Empty-State
        self.empty_state = EmptyState(
            icon="🧹",
            title="Noch nichts gescannt",
            message="Klick auf 'Windows Temp scannen' oder 'Dev-Ordner scannen' "
                    "um Dateien zu finden.",
        )
        self.result_stack.addWidget(self.empty_state)

        # Page 1: Loading
        self.loading_state = LoadingState("Scanne...")
        self.result_stack.addWidget(self.loading_state)

        # Page 2: Liste
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(280)
        self.result_stack.addWidget(self.list_widget)

        self.result_stack.setCurrentIndex(0)
        result_card.add(self.result_stack)
        layout.addWidget(result_card)

        # Action-Zeile
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.select_all_cb = QCheckBox("Alle auswählen")
        self.select_all_cb.stateChanged.connect(self.toggle_all)
        action_row.addWidget(self.select_all_cb)

        action_row.addStretch()

        self.selected_label = QLabel("0 ausgewählt")
        self.selected_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
        )
        action_row.addWidget(self.selected_label)

        trash_btn = QPushButton("♻️ In Papierkorb")
        trash_btn.setMinimumHeight(40)
        trash_btn.clicked.connect(lambda: self.delete_selected(True))

        hard_btn = QPushButton("🔥 Endgültig löschen")
        hard_btn.setObjectName("DangerButton")
        hard_btn.setMinimumHeight(40)
        hard_btn.clicked.connect(lambda: self.delete_selected(False))

        action_row.addWidget(trash_btn)
        action_row.addWidget(hard_btn)
        layout.addLayout(action_row)

        layout.addStretch()

    def start_scan(self, mode: str):
        if self._worker and self._worker.isRunning():
            return

        self.result_stack.setCurrentIndex(1)
        self.info_label.setText(f"Scanne... ({mode})")
        QApplication.processEvents()

        self._worker = ScanWorker(mode)
        self._worker.progress.connect(self.info_label.setText)
        self._worker.finished.connect(self.on_scan_done)
        self._worker.start()

    def on_scan_done(self, results: list):
        self._found = results

        if not results:
            self.info_label.setText("✅ Nichts zu löschen gefunden.")
            self.selected_label.setText("0 ausgewählt")
            self.empty_state = EmptyState(
                icon="✨",
                title="Alles sauber!",
                message="Keine unnötigen Dateien gefunden. Dein System ist aufgeräumt.",
            )
            self.result_stack.removeWidget(self.result_stack.widget(0))
            self.result_stack.insertWidget(0, self.empty_state)
            self.result_stack.setCurrentIndex(0)
            toast.success("Alles sauber — keine Dateien zu löschen")
            return

        # Liste füllen
        self.list_widget.clear()
        total = 0
        for path, size, category in results:
            total += size
            item = QListWidgetItem(
                f"[{category}]  {human_size(size):>10}    {path}"
            )
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, (path, size))
            self.list_widget.addItem(item)

        self.result_stack.setCurrentIndex(2)

        self.info_label.setText(
            f"✅ {len(results)} Ordner gefunden  ·  Gesamt: {human_size(total)}"
        )
        try:
            self.list_widget.itemChanged.connect(self.update_selected_label)
        except TypeError:
            pass
        self.update_selected_label()

        toast.info(f"{len(results)} Ordner gefunden · {human_size(total)}")

    def toggle_all(self, state):
        check = (Qt.CheckState.Checked
                 if state == Qt.CheckState.Checked.value
                 else Qt.CheckState.Unchecked)
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(check)
        self.update_selected_label()

    def update_selected_label(self, *_):
        count = 0
        total = 0
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                count += 1
                data = item.data(Qt.ItemDataRole.UserRole)
                if data:
                    total += data[1]
        self.selected_label.setText(
            f"{count} ausgewählt  ·  {human_size(total)}"
        )

    def delete_selected(self, to_trash: bool):
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                data = item.data(Qt.ItemDataRole.UserRole)
                if data:
                    selected.append(data[0])

        if not selected:
            toast.warning("Bitte wähle mindestens einen Ordner aus.")
            return

        mode_text = (
            "in den Papierkorb verschieben"
            if to_trash
            else "ENDGÜLTIG löschen"
        )
        reply = QMessageBox.question(
            self, "Bestätigung",
            f"{len(selected)} Ordner {mode_text}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        progress = QProgressDialog(
            "Lösche...", "Abbrechen", 0, len(selected), self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)

        ok_count = 0
        fail_count = 0
        freed = 0
        errors = []

        for i, path in enumerate(selected):
            if progress.wasCanceled():
                break
            progress.setValue(i)
            progress.setLabelText(f"Lösche {path.name}...")

            size = 0
            for p, s, _ in self._found:
                if p == path:
                    size = s
                    break

            ok, err = delete_path(path, to_trash=to_trash)
            if ok:
                ok_count += 1
                freed += size
            else:
                fail_count += 1
                errors.append(f"{path.name}: {err}")

        progress.setValue(len(selected))

        if ok_count > 0:
            toast.success(
                f"{ok_count} Ordner gelöscht · {human_size(freed)} freigegeben"
            )
        if fail_count > 0:
            toast.error(f"{fail_count} Ordner konnten nicht gelöscht werden")

        self.info_label.setText(
            f"Fertig · {human_size(freed)} freigegeben"
        )
        self.result_stack.setCurrentIndex(0)
        self.empty_state = EmptyState(
            icon="✅",
            title="Cleanup abgeschlossen",
            message=f"{ok_count} Ordner gelöscht · {human_size(freed)} freigegeben",
        )
        self.result_stack.removeWidget(self.result_stack.widget(0))
        self.result_stack.insertWidget(0, self.empty_state)
        self._found.clear()
        self.selected_label.setText("0 ausgewählt")