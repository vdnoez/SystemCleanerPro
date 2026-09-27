"""Startup-Manager — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QLabel, QApplication, QStackedWidget
)
from PyQt6.QtCore import Qt
import winreg

from src.ui.widgets import Card, PageHeader, EmptyState
from src.ui.theme import Colors
from src.ui.toast import toast


DISABLED_KEY = r"Software\SystemCleanerPro\DisabledStartup"


class StartupPage(QWidget):
    RUN_KEYS = [
        (winreg.HKEY_CURRENT_USER,
         r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU", False),
        (winreg.HKEY_LOCAL_MACHINE,
         r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM", True),
        (winreg.HKEY_CURRENT_USER,
         r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
         "HKCU (Once)", False),
    ]

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        layout.addWidget(PageHeader(
            "🚀 Autostart-Manager",
            "Programme die beim Windows-Start geladen werden"
        ))

        # Warnung
        warn_card = Card()
        warn_row = QHBoxLayout()
        warn_row.setSpacing(12)
        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 20px;")
        warn_row.addWidget(icon)
        warn_lbl = QLabel(
            "Deaktivierte Einträge werden in einen Backup-Bereich "
            "verschoben — du kannst sie jederzeit wieder aktivieren."
        )
        warn_lbl.setWordWrap(True)
        warn_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        warn_row.addWidget(warn_lbl, 1)
        warn_card.add_widget_direct(warn_row)
        layout.addWidget(warn_card)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        refresh_btn = QPushButton("🔄 Neu laden")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.load_entries)

        toggle_btn = QPushButton("🔁 Aktivieren / Deaktivieren")
        toggle_btn.setObjectName("SecondaryButton")
        toggle_btn.setMinimumHeight(40)
        toggle_btn.clicked.connect(self.toggle_selected)

        delete_btn = QPushButton("🗑️ Löschen")
        delete_btn.setObjectName("DangerButton")
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(self.delete_selected)

        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(toggle_btn)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Liste (Stacked)
        card = Card("Einträge")
        self.stack = QStackedWidget()

        self.empty_state = EmptyState(
            icon="🚀",
            title="Keine Autostart-Einträge",
            message="Es sind keine Programme für den Autostart konfiguriert.",
        )
        self.stack.addWidget(self.empty_state)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(360)
        self.stack.addWidget(self.list_widget)

        self.stack.setCurrentIndex(0)
        card.add(self.stack)
        layout.addWidget(card)

        layout.addStretch()

        self.load_entries()

    def _load_disabled(self) -> dict:
        result = {}
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, DISABLED_KEY) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        result[name] = value
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass
        return result

    def _save_disabled(self, name: str, value: str):
        try:
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER, DISABLED_KEY,
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
        except Exception:
            pass

    def _remove_disabled(self, name: str):
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, DISABLED_KEY,
                0, winreg.KEY_SET_VALUE
            ) as key:
                winreg.DeleteValue(key, name)
        except FileNotFoundError:
            pass

    def load_entries(self):
        self.list_widget.clear()

        count = 0
        self.list_widget.addItem("─── ✅ AKTIV ───")

        for hive, path, label, need_admin in self.RUN_KEYS:
            try:
                with winreg.OpenKey(hive, path) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            item = QListWidgetItem(
                                f"  🟢 [{label}]  {name}\n      →  {value}"
                            )
                            item.setData(Qt.ItemDataRole.UserRole, {
                                "name": name, "value": value,
                                "path": path, "hive": label,
                                "active": True, "need_admin": need_admin,
                            })
                            self.list_widget.addItem(item)
                            count += 1
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                continue

        disabled = self._load_disabled()
        if disabled:
            self.list_widget.addItem("")
            self.list_widget.addItem("─── ⏸️  DEAKTIVIERT ───")
            for name, value in disabled.items():
                item = QListWidgetItem(
                    f"  ⚪ [Backup]  {name}\n      →  {value}"
                )
                item.setData(Qt.ItemDataRole.UserRole, {
                    "name": name, "value": value,
                    "path": None, "hive": "Backup",
                    "active": False, "need_admin": False,
                })
                self.list_widget.addItem(item)
                count += 1

        if count == 0:
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)

    def toggle_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            toast.warning("Bitte erst Eintrag auswählen")
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        if data["active"]:
            if data["need_admin"]:
                toast.warning("HKLM-Einträge brauchen Admin-Rechte")
                return
            try:
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, data["path"],
                    0, winreg.KEY_SET_VALUE
                ) as key:
                    winreg.DeleteValue(key, data["name"])
                self._save_disabled(data["name"], data["value"])
                toast.success(f"'{data['name']}' deaktiviert")
                self.load_entries()
            except Exception as e:
                toast.error(f"Fehler: {e}")
        else:
            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, data["name"], 0,
                                  winreg.REG_SZ, data["value"])
                winreg.CloseKey(key)
                self._remove_disabled(data["name"])
                toast.success(f"'{data['name']}' aktiviert")
                self.load_entries()
            except Exception as e:
                toast.error(f"Fehler: {e}")

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            toast.warning("Bitte erst Eintrag auswählen")
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        reply = QMessageBox.question(
            self, "Löschen",
            f"'{data['name']}' wirklich endgültig löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if data["active"]:
                if data["need_admin"]:
                    toast.warning("HKLM-Einträge brauchen Admin-Rechte")
                    return
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, data["path"],
                    0, winreg.KEY_SET_VALUE
                ) as key:
                    winreg.DeleteValue(key, data["name"])
            else:
                self._remove_disabled(data["name"])
            toast.success(f"'{data['name']}' gelöscht")
            self.load_entries()
        except Exception as e:
            toast.error(f"Fehler: {e}")