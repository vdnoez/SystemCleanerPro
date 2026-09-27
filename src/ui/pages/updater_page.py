"""Software-Updater via winget — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QApplication, QMessageBox,
    QTabWidget, QLineEdit, QStackedWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize

from src.ui.widgets import Card, PageHeader, EmptyState, LoadingState
from src.ui.theme import Colors
from src.ui.toast import toast
from src.modules.software_updater import (
    is_winget_available, list_upgradable, list_installed,
    upgrade_package, upgrade_all, uninstall_package, search_package
)


class ScanUpgradesWorker(QThread):
    finished_signal = pyqtSignal(list)

    def run(self):
        try:
            self.finished_signal.emit(list_upgradable())
        except Exception:
            self.finished_signal.emit([])


class ScanInstalledWorker(QThread):
    finished_signal = pyqtSignal(list)

    def run(self):
        try:
            self.finished_signal.emit(list_installed())
        except Exception:
            self.finished_signal.emit([])


class UpgradeWorker(QThread):
    progress = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, package_id: str):
        super().__init__()
        self.package_id = package_id

    def run(self):
        ok, msg = upgrade_package(
            self.package_id, progress_cb=self.progress.emit
        )
        self.finished_signal.emit(ok, msg)


class UpgradeAllWorker(QThread):
    progress = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def run(self):
        ok, msg = upgrade_all(progress_cb=self.progress.emit)
        self.finished_signal.emit(ok, msg)


class SoftwareUpdaterPage(QWidget):
    def __init__(self):
        super().__init__()
        self._workers = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        layout.addWidget(PageHeader(
            "📦 Software-Updater",
            "Prüft installierte Programme auf Updates via winget"
        ))

        self.status_card = Card("Status")

        if not is_winget_available():
            warn = QLabel(
                "⚠️  <b>winget ist nicht installiert.</b><br>"
                "Installiere 'App Installer' aus dem Microsoft Store."
            )
            warn.setWordWrap(True)
            warn.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
            )
            self.status_card.add(warn)
            layout.addWidget(self.status_card)
            layout.addStretch()
            return

        self.status_lbl = QLabel("Bereit. Klick auf 'Nach Updates suchen'.")
        self.status_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
        )
        self.status_lbl.setWordWrap(True)
        self.status_card.add(self.status_lbl)
        layout.addWidget(self.status_card)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_upgrades_tab(), "🔄 Verfügbare Updates")
        self.tabs.addTab(self._build_installed_tab(), "📦 Installierte Programme")
        self.tabs.addTab(self._build_search_tab(), "🔍 Suche & Install")
        layout.addWidget(self.tabs, 1)

    def _build_upgrades_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.scan_upd_btn = QPushButton("🔍 Nach Updates suchen")
        self.scan_upd_btn.setMinimumHeight(42)
        self.scan_upd_btn.clicked.connect(self.scan_upgrades)

        self.upgrade_all_btn = QPushButton("🚀 Alle aktualisieren")
        self.upgrade_all_btn.setMinimumHeight(42)
        self.upgrade_all_btn.setEnabled(False)
        self.upgrade_all_btn.clicked.connect(self.do_upgrade_all)

        btn_row.addWidget(self.scan_upd_btn)
        btn_row.addWidget(self.upgrade_all_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.upgrades_stack = QStackedWidget()

        self.upgrades_empty = EmptyState(
            icon="📦",
            title="Noch nicht gescannt",
            message="Klick auf 'Nach Updates suchen' um verfügbare Updates zu finden.",
        )
        self.upgrades_stack.addWidget(self.upgrades_empty)

        self.upgrades_loading = LoadingState("Suche Updates...")
        self.upgrades_stack.addWidget(self.upgrades_loading)

        self.upgrades_list = QListWidget()
        self.upgrades_list.setMinimumHeight(340)
        self.upgrades_list.setSpacing(4)
        self.upgrades_stack.addWidget(self.upgrades_list)

        self.upgrades_stack.setCurrentIndex(0)
        layout.addWidget(self.upgrades_stack, 1)
        return w

    def scan_upgrades(self):
        self.scan_upd_btn.setEnabled(False)
        self.scan_upd_btn.setText("⏳ Scanne...")
        self.upgrades_stack.setCurrentIndex(1)
        self.upgrade_all_btn.setEnabled(False)
        QApplication.processEvents()

        worker = ScanUpgradesWorker()
        worker.finished_signal.connect(self._on_upgrades_done)
        worker.start()
        self._workers.append(worker)

    def _on_upgrades_done(self, packages: list):
        self.scan_upd_btn.setEnabled(True)
        self.scan_upd_btn.setText("🔍 Nach Updates suchen")

        if not packages:
            self.status_lbl.setText("✅ Alle Programme sind aktuell!")
            self.upgrades_empty = EmptyState(
                icon="✨",
                title="Alles aktuell!",
                message="Keine Updates verfügbar — deine Programme sind auf dem neuesten Stand.",
            )
            self.upgrades_stack.removeWidget(self.upgrades_stack.widget(0))
            self.upgrades_stack.insertWidget(0, self.upgrades_empty)
            self.upgrades_stack.setCurrentIndex(0)
            toast.success("Alle Programme aktuell")
            return

        self.status_lbl.setText(f"📦 {len(packages)} Updates verfügbar")
        self.upgrade_all_btn.setEnabled(True)
        toast.info(f"{len(packages)} Updates verfügbar")

        self.upgrades_list.clear()

        for pkg in packages:
            name = pkg.get("name", "?")
            current = pkg.get("current", "?")
            available = pkg.get("available", "?")
            pkg_id = pkg.get("id", "")

            widget = QWidget()
            widget.setMinimumHeight(56)
            row = QHBoxLayout(widget)
            row.setContentsMargins(12, 8, 12, 8)
            row.setSpacing(12)

            info_col = QVBoxLayout()
            info_col.setSpacing(2)

            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
                "font-weight: 700;"
            )
            info_col.addWidget(name_lbl)

            detail_lbl = QLabel(f"{current}   →   {available}")
            detail_lbl.setStyleSheet(
                f"color: {Colors.WARNING}; font-size: 11px;"
            )
            info_col.addWidget(detail_lbl)

            row.addLayout(info_col, 1)

            upd_btn = QPushButton("🔄 Update")
            upd_btn.setMinimumHeight(36)
            upd_btn.setMinimumWidth(120)
            upd_btn.clicked.connect(
                lambda _, i=pkg_id, n=name: self.do_upgrade_one(i, n)
            )
            row.addWidget(upd_btn)

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 60))
            self.upgrades_list.addItem(item)
            self.upgrades_list.setItemWidget(item, widget)

        self.upgrades_stack.setCurrentIndex(2)

    def _build_installed_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(12)

        btn_row = QHBoxLayout()
        self.scan_inst_btn = QPushButton("🔍 Installierte Programme laden")
        self.scan_inst_btn.setMinimumHeight(42)
        self.scan_inst_btn.clicked.connect(self.scan_installed)
        btn_row.addWidget(self.scan_inst_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.installed_stack = QStackedWidget()

        self.installed_empty = EmptyState(
            icon="📦",
            title="Noch nicht geladen",
            message="Klick auf 'Installierte Programme laden'.",
        )
        self.installed_stack.addWidget(self.installed_empty)

        self.installed_loading = LoadingState("Lade Programme...")
        self.installed_stack.addWidget(self.installed_loading)

        self.installed_list = QListWidget()
        self.installed_list.setMinimumHeight(340)
        self.installed_list.setSpacing(4)
        self.installed_stack.addWidget(self.installed_list)

        self.installed_stack.setCurrentIndex(0)
        layout.addWidget(self.installed_stack, 1)
        return w

    def scan_installed(self):
        self.scan_inst_btn.setEnabled(False)
        self.scan_inst_btn.setText("⏳ Lade...")
        self.installed_stack.setCurrentIndex(1)
        QApplication.processEvents()

        worker = ScanInstalledWorker()
        worker.finished_signal.connect(self._on_installed_done)
        worker.start()
        self._workers.append(worker)

    def _on_installed_done(self, packages: list):
        self.scan_inst_btn.setEnabled(True)
        self.scan_inst_btn.setText("🔍 Installierte Programme laden")

        if not packages:
            self.installed_stack.setCurrentIndex(0)
            toast.warning("Keine Programme gefunden")
            return

        self.status_lbl.setText(f"📦 {len(packages)} Programme installiert")
        toast.info(f"{len(packages)} Programme geladen")

        self.installed_list.clear()

        for pkg in packages:
            name = pkg.get("name", "?")
            version = pkg.get("version", "?")
            pkg_id = pkg.get("id", "")

            widget = QWidget()
            widget.setMinimumHeight(56)
            row = QHBoxLayout(widget)
            row.setContentsMargins(12, 8, 12, 8)
            row.setSpacing(12)

            info_col = QVBoxLayout()
            info_col.setSpacing(2)

            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
                "font-weight: 700;"
            )
            info_col.addWidget(name_lbl)

            detail_lbl = QLabel(f"Version: {version}")
            detail_lbl.setStyleSheet(
                f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
            )
            info_col.addWidget(detail_lbl)

            row.addLayout(info_col, 1)

            uninst_btn = QPushButton("🗑️ Deinstallieren")
            uninst_btn.setObjectName("DangerButton")
            uninst_btn.setMinimumHeight(36)
            uninst_btn.setMinimumWidth(140)
            uninst_btn.clicked.connect(
                lambda _, i=pkg_id, n=name: self.do_uninstall(i, n)
            )
            row.addWidget(uninst_btn)

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 60))
            self.installed_list.addItem(item)
            self.installed_list.setItemWidget(item, widget)

        self.installed_stack.setCurrentIndex(2)

    def _build_search_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(12)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "🔍 Suche ein Programm (z. B. 'firefox', 'vscode'...)"
        )
        self.search_input.setMinimumHeight(42)
        self.search_input.returnPressed.connect(self.do_search)

        search_btn = QPushButton("Suchen")
        search_btn.setMinimumHeight(42)
        search_btn.setMinimumWidth(120)
        search_btn.clicked.connect(self.do_search)

        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(search_btn)
        layout.addLayout(search_row)

        self.search_stack = QStackedWidget()

        self.search_empty = EmptyState(
            icon="🔍",
            title="Programm suchen",
            message="Gib einen Programmnamen ein um ihn zu finden und zu installieren.",
        )
        self.search_stack.addWidget(self.search_empty)

        self.search_list = QListWidget()
        self.search_list.setMinimumHeight(340)
        self.search_list.setSpacing(4)
        self.search_stack.addWidget(self.search_list)

        self.search_stack.setCurrentIndex(0)
        layout.addWidget(self.search_stack, 1)
        return w

    def do_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        self.search_list.clear()
        self.search_list.addItem(f"Suche nach '{query}'...")
        QApplication.processEvents()

        try:
            results = search_package(query)
        except Exception as e:
            toast.error(f"Fehler: {e}")
            return

        self.search_list.clear()

        if not results:
            self.search_empty = EmptyState(
                icon="❌",
                title="Keine Ergebnisse",
                message=f"Für '{query}' wurden keine Programme gefunden.",
            )
            self.search_stack.removeWidget(self.search_stack.widget(0))
            self.search_stack.insertWidget(0, self.search_empty)
            self.search_stack.setCurrentIndex(0)
            return

        toast.info(f"{len(results)} Ergebnisse für '{query}'")

        for pkg in results:
            name = pkg.get("name", "?")
            pkg_id = pkg.get("id", "")
            version = pkg.get("version", "")

            widget = QWidget()
            widget.setMinimumHeight(56)
            row = QHBoxLayout(widget)
            row.setContentsMargins(12, 8, 12, 8)
            row.setSpacing(12)

            info_col = QVBoxLayout()
            info_col.setSpacing(2)

            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; "
                "font-weight: 700;"
            )
            info_col.addWidget(name_lbl)

            detail_lbl = QLabel(
                f"{pkg_id}" + (f"  ·  {version}" if version else "")
            )
            detail_lbl.setStyleSheet(
                f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
            )
            info_col.addWidget(detail_lbl)

            row.addLayout(info_col, 1)

            install_btn = QPushButton("📥 Installieren")
            install_btn.setMinimumHeight(36)
            install_btn.setMinimumWidth(140)
            install_btn.clicked.connect(
                lambda _, i=pkg_id: self.do_install(i)
            )
            row.addWidget(install_btn)

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 60))
            self.search_list.addItem(item)
            self.search_list.setItemWidget(item, widget)

        self.search_stack.setCurrentIndex(1)

    def do_upgrade_one(self, package_id: str, name: str):
        if not package_id:
            return

        reply = QMessageBox.question(
            self, "Update starten",
            f"'{name}' jetzt aktualisieren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.status_lbl.setText(f"⏳ Update läuft: {name}...")
        toast.info(f"Update läuft: {name}")

        worker = UpgradeWorker(package_id)
        worker.progress.connect(self.status_lbl.setText)
        worker.finished_signal.connect(self._on_upgrade_done)
        worker.start()
        self._workers.append(worker)

    def do_upgrade_all(self):
        reply = QMessageBox.question(
            self, "Alle Updates",
            "Alle verfügbaren Updates jetzt installieren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.status_lbl.setText("⏳ Alle Updates werden installiert...")
        toast.info("Updates werden installiert...")
        self.upgrade_all_btn.setEnabled(False)

        worker = UpgradeAllWorker()
        worker.progress.connect(self.status_lbl.setText)
        worker.finished_signal.connect(self._on_upgrade_all_done)
        worker.start()
        self._workers.append(worker)

    def _on_upgrade_done(self, ok: bool, msg: str):
        self.status_lbl.setText(msg)
        if ok:
            toast.success("Update erfolgreich installiert")
            self.scan_upgrades()
        else:
            toast.error(f"Update fehlgeschlagen: {msg[:80]}")

    def _on_upgrade_all_done(self, ok: bool, msg: str):
        self.status_lbl.setText(msg)
        self.upgrade_all_btn.setEnabled(True)
        if ok:
            toast.success("Alle Updates installiert")
        else:
            toast.error(f"Fehler: {msg[:80]}")
        self.scan_upgrades()

    def do_uninstall(self, package_id: str, name: str):
        if not package_id:
            return

        reply = QMessageBox.warning(
            self, "Deinstallieren",
            f"'{name}' wirklich deinstallieren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.status_lbl.setText(f"⏳ Deinstalliere: {name}...")
        QApplication.processEvents()

        ok, msg = uninstall_package(package_id)
        self.status_lbl.setText(msg)

        if ok:
            toast.success(f"{name} deinstalliert")
            self.scan_installed()
        else:
            toast.error(f"Fehlgeschlagen: {msg[:80]}")

    def do_install(self, package_id: str):
        if not package_id:
            return

        reply = QMessageBox.question(
            self, "Installieren",
            f"'{package_id}' jetzt installieren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.status_lbl.setText(f"⏳ Installiere {package_id}...")
        toast.info(f"Installiere {package_id}...")
        QApplication.processEvents()

        import subprocess
        try:
            r = subprocess.run(
                ["winget", "install", "--id", package_id,
                 "--silent", "--accept-package-agreements",
                 "--accept-source-agreements"],
                capture_output=True, text=True, timeout=600,
                encoding="utf-8", errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW
                if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            if r.returncode == 0:
                toast.success(f"{package_id} installiert")
            else:
                toast.error(f"Fehler: {(r.stderr or '')[:80]}")
        except Exception as e:
            toast.error(f"Fehler: {e}")