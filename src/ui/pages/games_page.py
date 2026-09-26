"""Games-Seite — aufgeräumt."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QMessageBox, QApplication
)
from src.ui.widgets import Card, PageHeader
from src.ui.theme import Colors
from src.core.game_detector import detect_games, set_high_priority, load_game_db


class GamesPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)

        layout.addWidget(PageHeader(
            "🎮 Gaming-Booster",
            "Erkennt laufende Spiele und optimiert Prozess-Priorität"
        ))

        # ─── Info-Card ───
        db = load_game_db()
        info_card = Card("Erkannte Spiele in Datenbank")
        info_row = QHBoxLayout()
        info_row.setSpacing(12)

        icon = QLabel("🎯")
        icon.setStyleSheet("font-size: 22px;")
        info_row.addWidget(icon)

        info_lbl = QLabel(
            f"<b>{len(db)}</b> Spiele in der Datenbank. "
            f"Starte ein Spiel und klicke unten auf 'Scannen'."
        )
        info_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        info_row.addWidget(info_lbl, 1)
        info_card.add_widget_direct(info_row)
        layout.addWidget(info_card)

        # ─── Scan-Button ───
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.scan_btn = QPushButton("🔍 Laufende Spiele scannen & boosten")
        self.scan_btn.setMinimumHeight(44)
        self.scan_btn.clicked.connect(self.scan)
        btn_row.addWidget(self.scan_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

        # ─── Ergebnis-Card ───
        result_card = Card("Ergebnis")
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(240)
        result_card.add(self.list_widget)
        layout.addWidget(result_card)

        layout.addStretch()

    def scan(self):
        self.list_widget.clear()
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("⏳ Scanne...")
        QApplication.processEvents()

        games = list(detect_games())

        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔍 Laufende Spiele scannen & boosten")

        if not games:
            self.list_widget.addItem(
                "ℹ️  Keine Spiele aktuell aktiv.\n"
                "     Starte ein Spiel und klicke erneut auf 'Scannen'."
            )
            return

        for game in games:
            ok = set_high_priority(game["pid"])
            icon = "✅" if ok else "⚠️"
            status = "Boosting aktiv" if ok else "Kein Boost möglich"
            self.list_widget.addItem(
                f"{icon}  {game['name']}   ·   PID {game['pid']}   ·   {status}"
            )