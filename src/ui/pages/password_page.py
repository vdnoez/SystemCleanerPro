"""Passwort-Manager — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QApplication,
    QCheckBox, QSpinBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QComboBox,
    QAbstractItemView, QInputDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

from src.ui.widgets import Card, PageHeader, EmptyState
from src.ui.theme import Colors, FONT_MONO
from src.ui.toast import toast
from src.modules.password_checker import (
    check_password, generate_password, password_strength
)
from src.modules.vault import vault


class CheckWorker(QThread):
    finished_signal = pyqtSignal(dict)

    def __init__(self, password: str):
        super().__init__()
        self.password = password

    def run(self):
        try:
            result = check_password(self.password)
        except Exception as e:
            result = {"error": str(e)}
        self.finished_signal.emit(result)


# ═══════════════════════════════════════════════════════════════
# DETAIL-DIALOG
# ═══════════════════════════════════════════════════════════════
class DetailDialog(QDialog):
    def __init__(self, parent, entry: dict):
        super().__init__(parent)
        self.entry = entry
        self.setWindowTitle(f"🔑  {entry.get('name', '?')}")
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel(entry.get("name", "?"))
        title.setStyleSheet(
            f"color: {Colors.ACCENT}; font-size: 22px; font-weight: 800;"
        )
        layout.addWidget(title)

        cat = QLabel(f"Kategorie: {entry.get('category', '—')}")
        cat.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        layout.addWidget(cat)

        layout.addSpacing(8)

        # Benutzername
        layout.addWidget(self._field_label("Benutzername"))
        user_row = QHBoxLayout()
        user_field = QLineEdit(entry.get("username", ""))
        user_field.setReadOnly(True)
        user_field.setMinimumHeight(40)
        user_row.addWidget(user_field)
        copy_user = QPushButton("📋")
        copy_user.setFixedWidth(50)
        copy_user.setMinimumHeight(40)
        copy_user.clicked.connect(
            lambda: self._copy(entry.get("username", ""), "Benutzername")
        )
        user_row.addWidget(copy_user)
        layout.addLayout(user_row)

        # Passwort
        layout.addWidget(self._field_label("Passwort"))
        pw_row = QHBoxLayout()

        self.pw_field = QLineEdit(entry.get("password", ""))
        self.pw_field.setReadOnly(True)
        self.pw_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_field.setMinimumHeight(40)
        self.pw_field.setStyleSheet(
            f"font-family: {FONT_MONO}; font-size: 14px; letter-spacing: 1.5px;"
        )
        pw_row.addWidget(self.pw_field)

        self.toggle_btn = QPushButton("👁")
        self.toggle_btn.setFixedWidth(50)
        self.toggle_btn.setMinimumHeight(40)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self._toggle_pw)
        pw_row.addWidget(self.toggle_btn)

        copy_pw = QPushButton("📋")
        copy_pw.setFixedWidth(50)
        copy_pw.setMinimumHeight(40)
        copy_pw.clicked.connect(
            lambda: self._copy(entry.get("password", ""), "Passwort")
        )
        pw_row.addWidget(copy_pw)
        layout.addLayout(pw_row)

        if entry.get("url"):
            layout.addWidget(self._field_label("URL"))
            url_row = QHBoxLayout()
            url_field = QLineEdit(entry["url"])
            url_field.setReadOnly(True)
            url_field.setMinimumHeight(40)
            url_row.addWidget(url_field)
            copy_url = QPushButton("📋")
            copy_url.setFixedWidth(50)
            copy_url.setMinimumHeight(40)
            copy_url.clicked.connect(
                lambda: self._copy(entry["url"], "URL")
            )
            url_row.addWidget(copy_url)
            layout.addLayout(url_row)

        if entry.get("notes"):
            layout.addWidget(self._field_label("Notizen"))
            notes = QTextEdit(entry["notes"])
            notes.setReadOnly(True)
            notes.setMaximumHeight(80)
            layout.addWidget(notes)

        meta = QLabel(
            f"Erstellt: {entry.get('created', '?')[:19]}   ·   "
            f"Geändert: {entry.get('modified', '?')[:19]}"
        )
        meta.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 10px;"
        )
        layout.addWidget(meta)

        layout.addSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Schließen")
        close_btn.setObjectName("SecondaryButton")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 10px; "
            "font-weight: 700; letter-spacing: 1.2px; padding-top: 4px;"
        )
        return lbl

    def _toggle_pw(self):
        if self.toggle_btn.isChecked():
            self.pw_field.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.pw_field.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setText("👁")

    def _copy(self, text: str, what: str):
        if text:
            QApplication.clipboard().setText(text)
            toast.success(f"{what} kopiert")


# ═══════════════════════════════════════════════════════════════
# ENTRY-DIALOG
# ═══════════════════════════════════════════════════════════════
class EntryDialog(QDialog):
    def __init__(self, parent=None, entry: dict = None):
        super().__init__(parent)
        self.entry = entry or {}
        self.setWindowTitle("Eintrag bearbeiten" if entry else "Neuer Eintrag")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(12)

        self.name_input = QLineEdit(self.entry.get("name", ""))
        self.name_input.setPlaceholderText("z. B. Gmail")
        form.addRow("Name:", self.name_input)

        self.user_input = QLineEdit(self.entry.get("username", ""))
        self.user_input.setPlaceholderText("benutzer@beispiel.de")
        form.addRow("Benutzername:", self.user_input)

        pw_row = QHBoxLayout()
        self.pw_input = QLineEdit(self.entry.get("password", ""))
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        pw_row.addWidget(self.pw_input)

        gen_btn = QPushButton("🎲")
        gen_btn.setFixedWidth(40)
        gen_btn.setToolTip("Passwort generieren")
        gen_btn.clicked.connect(self._generate)
        pw_row.addWidget(gen_btn)

        self.show_btn = QPushButton("👁")
        self.show_btn.setFixedWidth(40)
        self.show_btn.setCheckable(True)
        self.show_btn.clicked.connect(self._toggle_show)
        pw_row.addWidget(self.show_btn)
        form.addRow("Passwort:", pw_row)

        self.url_input = QLineEdit(self.entry.get("url", ""))
        self.url_input.setPlaceholderText("https://...")
        form.addRow("URL:", self.url_input)

        self.cat_combo = QComboBox()
        self.cat_combo.setEditable(True)
        for c in ["Privat", "Arbeit", "Banking", "Social",
                  "E-Mail", "Shopping", "Sonstiges"]:
            self.cat_combo.addItem(c)
        current_cat = self.entry.get("category", "Sonstiges")
        idx = self.cat_combo.findText(current_cat)
        if idx >= 0:
            self.cat_combo.setCurrentIndex(idx)
        else:
            self.cat_combo.setEditText(current_cat)
        form.addRow("Kategorie:", self.cat_combo)

        self.notes_input = QLineEdit(self.entry.get("notes", ""))
        self.notes_input.setPlaceholderText("Notizen (optional)")
        form.addRow("Notizen:", self.notes_input)

        layout.addLayout(form)
        layout.addSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Speichern")
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _generate(self):
        self.pw_input.setText(generate_password(20, True))

    def _toggle_show(self):
        if self.show_btn.isChecked():
            self.pw_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_btn.setText("🙈")
        else:
            self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_btn.setText("👁")

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "username": self.user_input.text().strip(),
            "password": self.pw_input.text(),
            "url": self.url_input.text().strip(),
            "category": self.cat_combo.currentText().strip() or "Sonstiges",
            "notes": self.notes_input.text().strip(),
        }


# ═══════════════════════════════════════════════════════════════
# HAUPT-SEITE
# ═══════════════════════════════════════════════════════════════
class PasswordPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None
        self._show_passwords = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "🔐 Passwort-Manager",
            "Sicherer Speicher mit Verschlüsselung, Leak-Check und Generator"
        ))

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self._build_manager_tab(), "🔑 Meine Passwörter")
        self.tabs.addTab(self._build_leak_tab(), "🛡️ Leak-Check")
        self.tabs.addTab(self._build_vault_tab(), "⚙ Vault-Einstellungen")

        layout.addStretch()
        self._update_vault_ui()

    def _build_manager_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "🔍 Suche nach Name, Benutzer, Kategorie..."
        )
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self._filter_entries)
        top_row.addWidget(self.search_input, 1)

        add_btn = QPushButton("➕ Neu")
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self._add_entry)
        top_row.addWidget(add_btn)
        layout.addLayout(top_row)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Benutzername", "Passwort", "Kategorie", "URL", ""]
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setSortingEnabled(True)

        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 130)

        self.table.doubleClicked.connect(self._open_detail)
        self.table.setMinimumHeight(320)
        layout.addWidget(self.table)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self.show_pw_cb = QCheckBox("Alle Passwörter anzeigen")
        self.show_pw_cb.stateChanged.connect(self._toggle_show_passwords)
        action_row.addWidget(self.show_pw_cb)

        action_row.addStretch()

        info_lbl = QLabel("Doppelklick = Details")
        info_lbl.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px;"
        )
        action_row.addWidget(info_lbl)
        action_row.addSpacing(12)

        edit_btn = QPushButton("✏️ Bearbeiten")
        edit_btn.setObjectName("SecondaryButton")
        edit_btn.clicked.connect(self._edit_entry)
        action_row.addWidget(edit_btn)

        del_btn = QPushButton("🗑️ Löschen")
        del_btn.setObjectName("DangerButton")
        del_btn.clicked.connect(self._delete_entry)
        action_row.addWidget(del_btn)

        layout.addLayout(action_row)
        return w

    def _refresh_table(self):
        try:
            entries = vault.get_all()
        except Exception:
            entries = []

        entries.sort(key=lambda e: e.get("name", "").lower())

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(entries))

        for row, e in enumerate(entries):
            name_item = QTableWidgetItem(e.get("name", ""))
            name_item.setData(Qt.ItemDataRole.UserRole, e.get("id"))
            self.table.setItem(row, 0, name_item)

            self.table.setItem(
                row, 1, QTableWidgetItem(e.get("username", ""))
            )

            pw = e.get("password", "")
            pw_display = pw if self._show_passwords else "●" * min(len(pw), 12)
            pw_item = QTableWidgetItem(pw_display)
            pw_item.setData(Qt.ItemDataRole.UserRole + 1, pw)
            self.table.setItem(row, 2, pw_item)

            self.table.setItem(
                row, 3, QTableWidgetItem(e.get("category", ""))
            )
            self.table.setItem(
                row, 4, QTableWidgetItem(e.get("url", ""))
            )

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(4)

            view_btn = QPushButton("👁")
            view_btn.setFixedSize(32, 32)
            view_btn.setObjectName("SecondaryButton")
            eid = e.get("id")
            view_btn.clicked.connect(
                lambda _, id=eid: self._open_detail_by_id(id)
            )
            btn_layout.addWidget(view_btn)

            copy_btn = QPushButton("📋")
            copy_btn.setFixedSize(32, 32)
            copy_btn.setObjectName("SecondaryButton")
            pw_val = e.get("password", "")
            copy_btn.clicked.connect(
                lambda _, p=pw_val: self._copy_pw(p)
            )
            btn_layout.addWidget(copy_btn)

            self.table.setCellWidget(row, 5, btn_widget)

        self.table.setSortingEnabled(True)

    def _copy_pw(self, pw: str):
        if pw:
            QApplication.clipboard().setText(pw)
            toast.success("Passwort kopiert")

    def _filter_entries(self, text: str):
        text = text.lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(5):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)

    def _toggle_show_passwords(self, state):
        self._show_passwords = (state == Qt.CheckState.Checked.value)
        self._refresh_table()

    def _get_selected_id(self) -> str:
        row = self.table.currentRow()
        if row < 0:
            return ""
        item = self.table.item(row, 0)
        if not item:
            return ""
        return item.data(Qt.ItemDataRole.UserRole) or ""

    def _open_detail(self, *_):
        eid = self._get_selected_id()
        if eid:
            self._open_detail_by_id(eid)

    def _open_detail_by_id(self, eid: str):
        for e in vault.get_all():
            if e.get("id") == eid:
                DetailDialog(self, e).exec()
                return

    def _add_entry(self):
        if not vault.is_unlocked():
            toast.warning("Bitte entsperre zuerst den Vault")
            return

        dlg = EntryDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data["name"]:
                toast.warning("Name ist erforderlich")
                return
            ok, msg = vault.add(**data)
            if ok:
                toast.success(f"'{data['name']}' gespeichert")
                self._refresh_table()
            else:
                toast.error(f"Fehler: {msg}")

    def _edit_entry(self):
        eid = self._get_selected_id()
        if not eid:
            toast.warning("Bitte erst Eintrag auswählen")
            return
        entry = None
        for e in vault.get_all():
            if e["id"] == eid:
                entry = e
                break
        if not entry:
            return

        dlg = EntryDialog(self, entry)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            vault.update(eid, **data)
            toast.success("Eintrag aktualisiert")
            self._refresh_table()

    def _delete_entry(self):
        eid = self._get_selected_id()
        if not eid:
            toast.warning("Bitte erst Eintrag auswählen")
            return
        reply = QMessageBox.question(
            self, "Löschen",
            "Diesen Eintrag wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            vault.delete(eid)
            toast.success("Eintrag gelöscht")
            self._refresh_table()

    def _build_leak_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(16)

        info_card = Card()
        info_row = QHBoxLayout()
        info_row.setSpacing(12)
        icon = QLabel("🛡️")
        icon.setStyleSheet("font-size: 22px;")
        info_row.addWidget(icon)
        text = QLabel(
            "Prüft ob ein Passwort in bekannten Datenlecks auftaucht. "
            "Nutzt k-Anonymität: Nur die ersten 5 Zeichen eines lokalen "
            "SHA-1-Hashes werden gesendet."
        )
        text.setWordWrap(True)
        text.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        info_row.addWidget(text, 1)
        info_card.add_widget_direct(info_row)
        layout.addWidget(info_card)

        check_card = Card("Passwort prüfen")

        self.leak_input = QLineEdit()
        self.leak_input.setPlaceholderText("Hier eingeben...")
        self.leak_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.leak_input.setMinimumHeight(40)
        self.leak_input.textChanged.connect(self._on_leak_text_changed)
        check_card.add(self.leak_input)

        self.leak_strength = QLabel("Stärke wird nach Eingabe angezeigt")
        self.leak_strength.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 12px; font-style: italic;"
        )
        check_card.add(self.leak_strength)
        check_card.add_spacing(4)

        btn_row = QHBoxLayout()
        show_cb = QCheckBox("Passwort anzeigen")
        show_cb.stateChanged.connect(
            lambda s: self.leak_input.setEchoMode(
                QLineEdit.EchoMode.Normal
                if s == Qt.CheckState.Checked.value
                else QLineEdit.EchoMode.Password
            )
        )
        btn_row.addWidget(show_cb)
        btn_row.addStretch()

        self.leak_btn = QPushButton("🔍 Auf Lecks prüfen")
        self.leak_btn.setMinimumHeight(40)
        self.leak_btn.clicked.connect(self._do_leak_check)
        btn_row.addWidget(self.leak_btn)
        check_card.add_widget_direct(btn_row)
        layout.addWidget(check_card)

        result_card = Card("Ergebnis")
        self.leak_result = QListWidget()
        self.leak_result.setMinimumHeight(80)
        result_card.add(self.leak_result)
        layout.addWidget(result_card)

        gen_card = Card("Passwort-Generator")
        gen_row = QHBoxLayout()
        gen_row.setSpacing(12)
        gen_row.addWidget(QLabel("Länge:"))

        self.gen_len = QSpinBox()
        self.gen_len.setRange(8, 64)
        self.gen_len.setValue(20)
        self.gen_len.setFixedWidth(90)
        gen_row.addWidget(self.gen_len)

        self.gen_sym = QCheckBox("Mit Sonderzeichen")
        self.gen_sym.setChecked(True)
        gen_row.addWidget(self.gen_sym)
        gen_row.addStretch()

        gen_btn = QPushButton("🎲 Generieren")
        gen_btn.setMinimumHeight(40)
        gen_btn.clicked.connect(self._do_generate)
        gen_row.addWidget(gen_btn)

        gen_card.add_widget_direct(gen_row)
        gen_card.add_spacing(6)

        self.gen_out = QLineEdit()
        self.gen_out.setReadOnly(True)
        self.gen_out.setMinimumHeight(40)
        self.gen_out.setStyleSheet(
            f"font-family: {FONT_MONO}; font-size: 14px; letter-spacing: 1.5px;"
        )
        self.gen_out.setPlaceholderText("— noch nichts generiert —")
        gen_card.add(self.gen_out)
        gen_card.add_spacing(4)

        copy_btn = QPushButton("📋 In Zwischenablage kopieren")
        copy_btn.setObjectName("SecondaryButton")
        copy_btn.setMinimumHeight(38)
        copy_btn.clicked.connect(self._copy_gen)
        gen_card.add(copy_btn)

        layout.addWidget(gen_card)
        layout.addStretch()
        return w

    def _copy_gen(self):
        text = self.gen_out.text()
        if text:
            QApplication.clipboard().setText(text)
            toast.success("Passwort kopiert")

    def _on_leak_text_changed(self, text):
        if not text:
            self.leak_strength.setText("Stärke wird nach Eingabe angezeigt")
            self.leak_strength.setStyleSheet(
                f"color: {Colors.TEXT_MUTED}; font-size: 12px; "
                "font-style: italic;"
            )
            return
        r = password_strength(text)
        self.leak_strength.setText(
            f"Stärke: {r['label']}  ·  {r['score']}/100  ·  "
            f"{r['length']} Zeichen"
        )
        self.leak_strength.setStyleSheet(
            f"color: {r['color']}; font-size: 12px; font-weight: 700;"
        )

    def _do_leak_check(self):
        pw = self.leak_input.text()
        if not pw:
            toast.warning("Bitte erst ein Passwort eingeben")
            return
        if self._worker and self._worker.isRunning():
            return

        self.leak_btn.setEnabled(False)
        self.leak_btn.setText("⏳ Prüfe...")
        QApplication.processEvents()

        self._worker = CheckWorker(pw)
        self._worker.finished_signal.connect(self._on_leak_done)
        self._worker.start()

    def _on_leak_done(self, result):
        self.leak_btn.setEnabled(True)
        self.leak_btn.setText("🔍 Auf Lecks prüfen")
        self.leak_result.clear()

        if result.get("error"):
            toast.error(f"Fehler: {result['error']}")
            self.leak_result.addItem(f"❌ Fehler: {result['error']}")
            return

        if result.get("pwned"):
            count = result.get("count", 0)
            self.leak_result.addItem(
                f"🚨 GEFUNDEN in {count:,} Datenlecks! → sofort ändern!"
            )
            toast.error(f"Passwort in {count:,} Lecks gefunden!")
        else:
            self.leak_result.addItem("✅ NICHT gefunden — Passwort ist sicher.")
            toast.success("Passwort ist sicher")

    def _do_generate(self):
        pw = generate_password(self.gen_len.value(), self.gen_sym.isChecked())
        self.gen_out.setText(pw)
        toast.info("Passwort generiert")

    def _build_vault_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(16)

        status_card = Card("Vault-Status")
        self.vault_status_lbl = QLabel("Status wird geladen...")
        self.vault_status_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; "
            "line-height: 1.6;"
        )
        self.vault_status_lbl.setWordWrap(True)
        status_card.add(self.vault_status_lbl)
        layout.addWidget(status_card)

        action_card = Card("Aktionen")

        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self.create_btn = QPushButton("🔐 Vault erstellen")
        self.create_btn.setMinimumHeight(42)
        self.create_btn.clicked.connect(self._create_vault)
        row1.addWidget(self.create_btn)

        self.unlock_btn = QPushButton("🔓 Vault entsperren")
        self.unlock_btn.setMinimumHeight(42)
        self.unlock_btn.clicked.connect(self._unlock_vault)
        row1.addWidget(self.unlock_btn)

        self.lock_btn = QPushButton("🔒 Sperren")
        self.lock_btn.setObjectName("SecondaryButton")
        self.lock_btn.setMinimumHeight(42)
        self.lock_btn.clicked.connect(self._lock_vault)
        row1.addWidget(self.lock_btn)
        row1.addStretch()
        action_card.add_widget_direct(row1)

        action_card.add_spacing(8)

        row2 = QHBoxLayout()
        row2.setSpacing(10)

        change_btn = QPushButton("🔑 Master-Passwort ändern")
        change_btn.setObjectName("SecondaryButton")
        change_btn.setMinimumHeight(42)
        change_btn.clicked.connect(self._change_master)
        row2.addWidget(change_btn)
        row2.addStretch()

        delete_btn = QPushButton("💥 Vault löschen")
        delete_btn.setObjectName("DangerButton")
        delete_btn.setMinimumHeight(42)
        delete_btn.clicked.connect(self._delete_vault)
        row2.addWidget(delete_btn)
        action_card.add_widget_direct(row2)

        layout.addWidget(action_card)
        layout.addStretch()
        return w

    def _update_vault_ui(self):
        try:
            initialized = vault.is_initialized()
            unlocked = vault.is_unlocked()
        except Exception:
            initialized = False
            unlocked = False

        if not initialized:
            self.vault_status_lbl.setText(
                "⚠️  <b>Kein Vault vorhanden.</b><br>"
                "Klicke auf 'Vault erstellen' um ein Master-Passwort zu setzen."
            )
            self.create_btn.setEnabled(True)
            self.unlock_btn.setEnabled(False)
            self.lock_btn.setEnabled(False)
        elif not unlocked:
            self.vault_status_lbl.setText(
                "🔒  <b>Vault vorhanden, aber gesperrt.</b><br>"
                "Klicke auf 'Vault entsperren'."
            )
            self.create_btn.setEnabled(False)
            self.unlock_btn.setEnabled(True)
            self.lock_btn.setEnabled(False)
        else:
            count = len(vault.get_all())
            self.vault_status_lbl.setText(
                f"✅  <b>Vault entsperrt.</b><br>"
                f"Einträge gespeichert: {count}"
            )
            self.create_btn.setEnabled(False)
            self.unlock_btn.setEnabled(False)
            self.lock_btn.setEnabled(True)
            self._refresh_table()

    def _create_vault(self):
        pw, ok = QInputDialog.getText(
            self, "Master-Passwort setzen",
            "Neues Master-Passwort (min. 6 Zeichen):",
            QLineEdit.EchoMode.Password
        )
        if not ok or not pw:
            return
        pw2, ok2 = QInputDialog.getText(
            self, "Master-Passwort bestätigen",
            "Master-Passwort wiederholen:",
            QLineEdit.EchoMode.Password
        )
        if not ok2 or pw != pw2:
            toast.error("Passwörter stimmen nicht überein")
            return

        ok, msg = vault.create(pw)
        if ok:
            toast.success("Vault erstellt")
        else:
            toast.error(msg)
        self._update_vault_ui()

    def _unlock_vault(self):
        pw, ok = QInputDialog.getText(
            self, "Vault entsperren",
            "Master-Passwort:",
            QLineEdit.EchoMode.Password
        )
        if not ok or not pw:
            return
        ok, msg = vault.unlock(pw)
        if not ok:
            toast.error(msg)
        else:
            toast.success("Vault entsperrt")
        self._update_vault_ui()

    def _lock_vault(self):
        vault.lock()
        toast.info("Vault gesperrt")
        self._update_vault_ui()

    def _change_master(self):
        if not vault.is_unlocked():
            return
        old, ok = QInputDialog.getText(
            self, "Master-Passwort ändern",
            "Aktuelles Master-Passwort:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return

        v2 = type(vault)()
        success, msg = v2.unlock(old)
        if not success:
            toast.error("Altes Passwort falsch")
            return

        new, ok = QInputDialog.getText(
            self, "Neues Master-Passwort",
            "Neues Master-Passwort (min. 6):",
            QLineEdit.EchoMode.Password
        )
        if not ok or len(new) < 6:
            return

        entries = vault.get_all()
        from src.modules.vault import VAULT_FILE, META_FILE, _derive_key
        import secrets, base64, json
        from cryptography.fernet import Fernet

        salt = secrets.token_bytes(16)
        key = _derive_key(new, salt)
        f = Fernet(key)
        encrypted = f.encrypt(
            json.dumps(entries, ensure_ascii=False).encode()
        )
        VAULT_FILE.write_bytes(encrypted)
        META_FILE.write_text(json.dumps({
            "salt": base64.b64encode(salt).decode(),
            "version": 1,
        }, indent=2), encoding="utf-8")

        toast.success("Master-Passwort geändert")
        vault.lock()
        self._update_vault_ui()

    def _delete_vault(self):
        reply = QMessageBox.warning(
            self, "Vault löschen",
            "ALLE gespeicherten Passwörter werden ENDGÜLTIG gelöscht!\n\n"
            "Wirklich fortfahren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        from src.modules.vault import VAULT_FILE, META_FILE
        for f in (VAULT_FILE, META_FILE):
            try:
                if f.exists():
                    f.unlink()
            except Exception:
                pass
        vault.lock()
        self._refresh_table()
        self._update_vault_ui()
        toast.success