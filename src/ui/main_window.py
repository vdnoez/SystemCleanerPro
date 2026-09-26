"""Hauptfenster — Sidebar mit Kategorien und Update-Seite."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QButtonGroup,
    QFrame, QApplication, QSystemTrayIcon, QScrollArea
)
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt

from src.core.config import APP_NAME, APP_VERSION
from src.ui.theme import get_stylesheet, Colors, get_theme_name
from src.ui.icons import icon
from src.ui.dashboard import Dashboard
from src.ui.pages.health_page import HealthPage
from src.ui.pages.games_page import GamesPage
from src.ui.pages.cleaner_page import CleanerPage
from src.ui.pages.updater_page import UpdaterPage
from src.ui.pages.ram_page import RamPage
from src.ui.pages.processes_page import ProcessesPage
from src.ui.pages.network_page import NetworkPage
from src.ui.pages.startup_page import StartupPage
from src.ui.pages.shredder_page import ShredderPage
from src.ui.pages.bsod_page import BsodPage
from src.ui.pages.boot_page import BootPage
from src.ui.pages.dns_page import DnsPage
from src.ui.pages.vpn_page import VpnPage
from src.ui.pages.password_page import PasswordPage
from src.ui.pages.update_page import UpdatePage
from src.ui.settings_dialog import SettingsDialog, load_settings
from src.ui.about_dialog import AboutDialog
from src.ui.tray import create_tray_icon


# ═══════════════════════════════════════════════════════════════
# NAVIGATION
# ═══════════════════════════════════════════════════════════════
NAV_STRUCTURE = [
    {
        "label": "📊  ÜBERSICHT",
        "items": [
            ("Health-Check", "shield"),
            ("Dashboard", "dashboard"),
            ("Prozesse", "processes"),
            ("Netzwerk", "network"),
        ],
    },
    {
        "label": "🧹  WARTUNG",
        "items": [
            ("Cleaner", "cleaner"),
            ("Software-Updater", "refresh"),
            ("RAM", "ram"),
            ("Shredder", "shredder"),
            ("Autostart", "startup"),
            ("App-Update", "bolt"),
        ],
    },
    {
        "label": "🔐  SICHERHEIT",
        "items": [
            ("VPN", "shield"),
            ("Passwort", "shield"),
            ("DNS", "network"),
        ],
    },
    {
        "label": "🔍  ANALYSE",
        "items": [
            ("BSOD", "search"),
            ("Boot", "dashboard"),
        ],
    },
    {
        "label": "🎮  SPIELE",
        "items": [
            ("Games", "games"),
        ],
    },
]


PAGES_ORDER = []
for cat in NAV_STRUCTURE:
    for item in cat["items"]:
        PAGES_ORDER.append(item)


class MainWindow(QMainWindow):
    def __init__(self, tray: bool = True):
        super().__init__()
        self.settings = load_settings()
        self.setWindowTitle(f"{APP_NAME}  ·  v{APP_VERSION}")
        self.resize(1400, 880)
        self.setMinimumSize(1180, 720)
        self.setStyleSheet(get_stylesheet())

        self.setWindowIcon(icon("bolt", Colors.ACCENT))

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        # ═══════ CONTENT ═══════
        self.stack = QStackedWidget()
        self._pages = [
            HealthPage(),      # 1.  Health-Check
            Dashboard(),       # 2.  Dashboard
            ProcessesPage(),   # 3.  Prozesse
            NetworkPage(),     # 4.  Netzwerk
            CleanerPage(),     # 5.  Cleaner
            UpdaterPage(),     # 6.  Software-Updater
            RamPage(),         # 7.  RAM
            ShredderPage(),    # 8.  Shredder
            StartupPage(),     # 9.  Autostart
            UpdatePage(),      # 10. App-Update
            VpnPage(),         # 11. VPN
            PasswordPage(),    # 12. Passwort
            DnsPage(),         # 13. DNS
            BsodPage(),        # 14. BSOD
            BootPage(),        # 15. Boot
            GamesPage(),       # 16. Games
        ]

        for p in self._pages:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            scroll.setWidget(p)
            self.stack.addWidget(scroll)

        root.addWidget(self.stack, 1)

        self.statusBar().showMessage(
            f"Bereit.  ·  Theme: {get_theme_name()}"
        )

        # Tray
        self.tray = None
        if tray and QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = create_tray_icon(self)
            self.tray.show()

        self._setup_shortcuts()

    def _setup_shortcuts(self):
        for i in range(min(9, len(PAGES_ORDER))):
            sc = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            sc.activated.connect(lambda idx=i: self._switch_page(idx))
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(
            QApplication.instance().quit)
        QShortcut(QKeySequence("Ctrl+,"), self).activated.connect(
            self.open_settings)
        QShortcut(QKeySequence("F5"), self).activated.connect(self._refresh)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel("⚡  Cleaner Pro")
        logo.setObjectName("Logo")
        layout.addWidget(logo)
        layout.addSpacing(6)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self._nav_buttons = []

        button_index = 0
        for cat in NAV_STRUCTURE:
            cat_lbl = QLabel(cat["label"])
            cat_lbl.setObjectName("CategoryLabel")
            layout.addWidget(cat_lbl)

            for label, icon_name in cat["items"]:
                btn = QPushButton(f"   {label}")
                btn.setObjectName("NavButton")
                btn.setIcon(icon(icon_name, Colors.TEXT_SECONDARY))
                btn.setCheckable(True)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)

                if button_index == 0:
                    btn.setChecked(True)

                idx = button_index
                btn.clicked.connect(
                    lambda _, i=idx: self._switch_page(i)
                )
                self.nav_group.addButton(btn, button_index)
                self._nav_buttons.append(btn)
                layout.addWidget(btn)
                button_index += 1

        layout.addStretch()

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(
            f"background-color: {Colors.BORDER}; max-height: 1px;"
        )
        layout.addWidget(sep)

        settings_btn = QPushButton("   Einstellungen")
        settings_btn.setObjectName("NavButton")
        settings_btn.setIcon(icon("settings", Colors.TEXT_SECONDARY))
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

        about_btn = QPushButton("   Über")
        about_btn.setObjectName("NavButton")
        about_btn.setIcon(icon("about", Colors.TEXT_SECONDARY))
        about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        about_btn.clicked.connect(self.open_about)
        layout.addWidget(about_btn)

        version_lbl = QLabel(f"  v{APP_VERSION}")
        version_lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px; padding: 16px;"
        )
        layout.addWidget(version_lbl)

        return sidebar

    def _switch_page(self, index: int):
        if index >= self.stack.count():
            return
        self.stack.setCurrentIndex(index)
        if index < len(self._nav_buttons):
            self._nav_buttons[index].setChecked(True)
        label = PAGES_ORDER[index][0] if index < len(PAGES_ORDER) else "?"
        self.statusBar().showMessage(
            f"{label}  ·  {index + 1}/{self.stack.count()}"
        )

    def open_update_page(self):
        """Öffnet die App-Update-Seite (Index 9)."""
        for i, (name, _) in enumerate(PAGES_ORDER):
            if name == "App-Update":
                self._switch_page(i)
                # Check direkt starten
                try:
                    page = self.stack.widget(i).widget()
                    if hasattr(page, "check_update"):
                        page.check_update()
                except Exception:
                    pass
                return

    def _refresh(self):
        current = self.stack.currentWidget()
        if isinstance(current, QScrollArea):
            current = current.widget()
        if hasattr(current, "refresh"):
            current.refresh()
        self.statusBar().showMessage("Aktualisiert.", 2000)

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec():
            self.statusBar().showMessage("Einstellungen gespeichert.", 3000)

    def open_about(self):
        AboutDialog(self).exec()

    def reload_theme(self):
        from src.ui.theme import get_stylesheet, get_theme_name
        self.setStyleSheet(get_stylesheet())
        for btn in self._nav_buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.update()
        self.statusBar().showMessage(f"Theme: {get_theme_name()}", 3000)

    def changeEvent(self, event):
        from PyQt6.QtCore import QEvent
        if (event.type() == QEvent.Type.WindowStateChange
                and self.isMinimized()
                and self.tray
                and self.settings.get("minimize_to_tray", True)):
            self.hide()
            event.ignore()
            return
        super().changeEvent(event)

    def closeEvent(self, event):
        if (self.tray
                and self.settings.get("close_to_tray", True)):
            event.ignore()
            self.hide()
            self.tray.showMessage(
                APP_NAME,
                "Läuft im Hintergrund. Doppelklick zum Anzeigen.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()