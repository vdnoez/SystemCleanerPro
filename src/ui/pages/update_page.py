"""App-Update-Seite — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QMessageBox, QTextEdit, QApplication
)
from PyQt6.QtCore import QThread, pyqtSignal

from src.ui.widgets import Card, PageHeader
from src.ui.theme import Colors
from src.ui.toast import toast
from src.core.config import APP_VERSION
from src.modules.updater import (
    check_for_update, download_update, apply_update,
    get_download_size, format_bytes
)


class CheckWorker(QThread):
    finished_signal = pyqtSignal(dict)

    def run(self):
        result = check_for_update()
        self.finished_signal.emit(result)


class DownloadWorker(QThread):
    progress = pyqtSignal(int, int, int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        ok, result = download_update(
            self.url,
            progress_cb=lambda p, d, t: self.progress.emit(p, d, t)
        )
        self.finished_signal.emit(ok, result)


class UpdatePage(QWidget):
    def __init__(self):
        super().__init__()
        self._check_worker = None
        self._download_worker = None
        self._update_info = None
        self._downloaded_path = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "🔄 App-Update",
            "Prüft auf neue Versionen über GitHub"
        ))

        # Status
        status_card = Card("Aktuelle Version")
        status_row = QHBoxLayout()
        status_row.setSpacing(14)

        icon_lbl = QLabel("📦")
        icon_lbl.setStyleSheet("font-size: 28px;")
        status_row.addWidget(icon_lbl)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        self.version_lbl = QLabel(f"Version {APP_VERSION}")
        self.version_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; "
            "font-weight: 800;"
        )
        info_col.addWidget(self.version_lbl)

        self.status_lbl = QLabel("Klicke auf 'Nach Updates suchen'")
        self.status_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        info_col.addWidget(self.status_lbl)

        status_row.addLayout(info_col, 1)

        self.check_btn = QPushButton("🔍 Nach Updates suchen")
        self.check_btn.setMinimumHeight(42)
        self.check_btn.clicked.connect(self.check_update)
        status_row.addWidget(self.check_btn)

        status_card.add_widget_direct(status_row)
        layout.addWidget(status_card)

        # Update-Card
        self.update_card = Card("✅ Update verfügbar")
        self.update_card.setVisible(False)

        self.update_info_lbl = QLabel("")
        self.update_info_lbl.setWordWrap(True)
        self.update_info_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 13px;"
        )
        self.update_card.add(self.update_info_lbl)

        notes_lbl = QLabel("Release Notes:")
        notes_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; "
            "font-weight: 700; letter-spacing: 1px; padding-top: 6px;"
        )
        self.update_card.add(notes_lbl)

        self.notes_view = QTextEdit()
        self.notes_view.setReadOnly(True)
        self.notes_view.setMaximumHeight(150)
        self.update_card.add(self.notes_view)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.update_card.add(self.progress_bar)

        self.progress_lbl = QLabel("")
        self.progress_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;"
        )
        self.progress_lbl.setVisible(False)
        self.update_card.add(self.progress_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.download_btn = QPushButton("📥 Jetzt herunterladen")
        self.download_btn.setMinimumHeight(42)
        self.download_btn.clicked.connect(self.download_update)
        btn_row.addWidget(self.download_btn)

        self.install_btn = QPushButton("⚡ Installieren & Neu starten")
        self.install_btn.setMinimumHeight(42)
        self.install_btn.setVisible(False)
        self.install_btn.clicked.connect(self.install_update)
        btn_row.addWidget(self.install_btn)

        self.open_release_btn = QPushButton("🌐 Release-Seite öffnen")
        self.open_release_btn.setObjectName("SecondaryButton")
        self.open_release_btn.setMinimumHeight(42)
        self.open_release_btn.clicked.connect(self.open_release_page)
        btn_row.addWidget(self.open_release_btn)

        btn_row.addStretch()
        self.update_card.add_widget_direct(btn_row)
        layout.addWidget(self.update_card)

        info_card = Card("ℹ️ Info")
        info_text = QLabel(
            "Die App prüft auf GitHub nach neuen Releases. "
            "Wenn eine neuere Version verfügbar ist, kannst du sie hier "
            "herunterladen und installieren."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            "line-height: 1.6;"
        )
        info_card.add(info_text)
        layout.addWidget(info_card)

        layout.addStretch()

    def check_update(self):
        self.check_btn.setEnabled(False)
        self.check_btn.setText("⏳ Prüfe...")
        self.status_lbl.setText("Prüfe GitHub auf neue Version...")
        QApplication.processEvents()

        self._check_worker = CheckWorker()
        self._check_worker.finished_signal.connect(self._on_check_done)
        self._check_worker.start()

    def _on_check_done(self, result: dict):
        self.check_btn.setEnabled(True)
        self.check_btn.setText("🔍 Nach Updates suchen")
        self._update_info = result

        if result.get("error"):
            self.status_lbl.setText(f"❌ {result['error']}")
            self.status_lbl.setStyleSheet(
                f"color: {Colors.DANGER}; font-size: 12px;"
            )
            toast.error(f"Update-Check: {result['error']}")
            return

        if result.get("update_available"):
            self.status_lbl.setText(
                f"🎉 Update verfügbar: {result['latest_version']}"
            )
            self.status_lbl.setStyleSheet(
                f"color: {Colors.SUCCESS}; font-size: 12px; font-weight: 700;"
            )

            size = get_download_size(result["download_url"])
            size_str = f"  ·  {format_bytes(size)}" if size else ""

            self.update_info_lbl.setText(
                f"<b>Neue Version:</b> {result['latest_version']}{size_str}<br>"
                f"<b>Aktuell:</b> {result['current_version']}<br>"
                f"<b>Veröffentlicht:</b> {result['published_at'][:10]}"
            )
            self.notes_view.setPlainText(
                result.get("release_notes") or "Keine Release Notes."
            )
            self.update_card.setVisible(True)
            self.download_btn.setVisible(True)
            self.install_btn.setVisible(False)
            self.progress_bar.setVisible(False)
            self.progress_lbl.setVisible(False)

            toast.info(f"Update {result['latest_version']} verfügbar")
        else:
            self.status_lbl.setText(
                f"✅ Du hast die neueste Version ({result['current_version']})"
            )
            self.status_lbl.setStyleSheet(
                f"color: {Colors.SUCCESS}; font-size: 12px;"
            )
            self.update_card.setVisible(False)
            toast.success(f"Neueste Version: {result['current_version']}")

    def download_update(self):
        if not self._update_info or not self._update_info.get("download_url"):
            return

        self.download_btn.setEnabled(False)
        self.download_btn.setText("⏳ Lade herunter...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.progress_lbl.setVisible(True)
        self.progress_lbl.setText("Starte Download...")

        self._download_worker = DownloadWorker(
            self._update_info["download_url"]
        )
        self._download_worker.progress.connect(self._on_progress)
        self._download_worker.finished_signal.connect(self._on_download_done)
        self._download_worker.start()

    def _on_progress(self, percent: int, done: int, total: int):
        self.progress_bar.setValue(percent)
        self.progress_lbl.setText(
            f"{percent}%  ·  {format_bytes(done)} / {format_bytes(total)}"
        )

    def _on_download_done(self, ok: bool, result: str):
        self.download_btn.setEnabled(True)
        self.download_btn.setText("📥 Jetzt herunterladen")

        if not ok:
            self.progress_lbl.setText(f"❌ Fehler: {result}")
            toast.error(f"Download: {result[:80]}")
            return

        self._downloaded_path = result
        self.progress_bar.setValue(100)
        self.progress_lbl.setText("✅ Download fertig!")

        self.download_btn.setVisible(False)
        self.install_btn.setVisible(True)

        toast.success("Download fertig")

    def install_update(self):
        if not self._downloaded_path:
            return

        reply = QMessageBox.question(
            self, "Update installieren",
            "Jetzt installieren?\n\nApp wird beendet und neu gestartet.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        ok, msg = apply_update(self._downloaded_path)
        if ok:
            toast.info("Update wird installiert...")
            QApplication.quit()
        else:
            toast.error(f"Fehler: {msg[:80]}")

    def open_release_page(self):
        if not self._update_info:
            return
        url = self._update_info.get("release_url", "")
        if not url:
            return
        try:
            import subprocess
            subprocess.Popen(["start", url], shell=True)
            toast.info("Release-Seite geöffnet")
        except Exception as e:
            toast.error(f"Fehler: {e}")