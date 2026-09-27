"""Games-Booster — mit Toasts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QApplication, QStackedWidget
)
from src.ui.widgets import Card, PageHeader, EmptyState, LoadingState
from src.ui.theme import Colors
from src.ui.toast import toast
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

        # Info-Card
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

        # Scan-Button
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.scan_btn = QPushButton("🔍 Laufende Spiele scannen & boosten")
        self.scan_btn.setMinimumHeight(44)
        self.scan_btn.clicked.connect(self.scan)
        btn_row.addWidget(self.scan_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Result-Stack
        result_card = Card("Ergebnis")
        self.stack = QStackedWidget()

        self.empty_state = EmptyState(
            icon="🎮",
            title="Kein Scan durchgeführt",
            message="Klick auf 'Scannen' um laufende Spiele zu erkennen.",
        )
        self.stack.addWidget(self.empty_state)

        self.loading_state = LoadingState("Suche laufende Spiele...")
        self.stack.addWidget(self.loading_state)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(240)
        self.stack.addWidget(self.list_widget)

        self.stack.setCurrentIndex(0)
        result_card.add(self.stack)
        layout.addWidget(result_card)

        layout.addStretch()

    def scan(self):
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("⏳ Scanne...")
        self.stack.setCurrentIndex(1)
        QApplication.processEvents()

        games = list(detect_games())

        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔍 Laufende Spiele scannen & boosten")

        self.list_widget.clear()

        if not games:
            self.empty_state = EmptyState(
                icon="🎯",
                title="Keine Spiele aktiv",
                message="Starte ein Spiel und klicke erneut auf 'Scannen'.",
            )
            self.stack.removeWidget(self.stack.widget(0))
            self.stack.insertWidget(0, self.empty_state)
            self.stack.setCurrentIndex(0)
            toast.info("Keine laufenden Spiele gefunden")
            return

        boosted = 0
        for game in games:
            ok = set_high_priority(game["pid"])
            if ok:
                boosted += 1
            icon = "✅" if ok else "⚠️"
            status = "Boosting aktiv" if ok else "Kein Boost möglich"
            self.list_widget.addItem(
                f"{icon}  {game['name']}   ·   PID {game['pid']}   ·   {status}"
            )

        self.stack.setCurrentIndex(2)
        toast.success(f"{boosted} von {len(games)} Spiel(en) geboostet")