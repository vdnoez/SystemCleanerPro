"""Slate Design — ruhig, luftig, konsistent."""


THEMES = {
    "slate": {
        "name": "Slate (Standard)",
        "BG_BASE": "#0f1116",
        "BG_ELEVATED": "#181b22",
        "BG_OVERLAY": "#1e222b",
        "BG_SIDEBAR": "#0a0c10",
        "BG_GRADIENT_1": "#0f1116",
        "BG_GRADIENT_2": "#141721",
        "ACCENT": "#6366f1",
        "ACCENT_HOVER": "#818cf8",
        "ACCENT_DARK": "#4f46e5",
        "ACCENT_GLOW": "#a5b4fc",
        "ACCENT_2": "#8b5cf6",
        "SUCCESS": "#10b981",
        "WARNING": "#f59e0b",
        "DANGER": "#ef4444",
        "INFO": "#60a5fa",
        "TEXT_PRIMARY": "#e6e8ec",
        "TEXT_SECONDARY": "#8a92a6",
        "TEXT_MUTED": "#4a5163",
        "BORDER": "#262a35",
        "BORDER_LIGHT": "#363b4a",
        "FONT": "Segoe UI Variable Display, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
    "carbon": {
        "name": "Carbon (Schwarz)",
        "BG_BASE": "#0a0a0a",
        "BG_ELEVATED": "#131313",
        "BG_OVERLAY": "#1a1a1a",
        "BG_SIDEBAR": "#050505",
        "BG_GRADIENT_1": "#0a0a0a",
        "BG_GRADIENT_2": "#111111",
        "ACCENT": "#ffffff",
        "ACCENT_HOVER": "#e5e5e5",
        "ACCENT_DARK": "#a3a3a3",
        "ACCENT_GLOW": "#f5f5f5",
        "ACCENT_2": "#d4d4d4",
        "SUCCESS": "#22c55e",
        "WARNING": "#eab308",
        "DANGER": "#ef4444",
        "INFO": "#3b82f6",
        "TEXT_PRIMARY": "#fafafa",
        "TEXT_SECONDARY": "#737373",
        "TEXT_MUTED": "#404040",
        "BORDER": "#1f1f1f",
        "BORDER_LIGHT": "#2e2e2e",
        "FONT": "Segoe UI Variable Display, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
    "ocean": {
        "name": "Ocean (Blau)",
        "BG_BASE": "#0a141c",
        "BG_ELEVATED": "#0f1e28",
        "BG_OVERLAY": "#132833",
        "BG_SIDEBAR": "#061018",
        "BG_GRADIENT_1": "#0a141c",
        "BG_GRADIENT_2": "#0f1e2a",
        "ACCENT": "#0ea5e9",
        "ACCENT_HOVER": "#38bdf8",
        "ACCENT_DARK": "#0284c7",
        "ACCENT_GLOW": "#7dd3fc",
        "ACCENT_2": "#06b6d4",
        "SUCCESS": "#10b981",
        "WARNING": "#f59e0b",
        "DANGER": "#ef4444",
        "INFO": "#3b82f6",
        "TEXT_PRIMARY": "#e0f2fe",
        "TEXT_SECONDARY": "#7a9bb3",
        "TEXT_MUTED": "#3f5c70",
        "BORDER": "#1a3240",
        "BORDER_LIGHT": "#264658",
        "FONT": "Segoe UI Variable Display, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
    "forest": {
        "name": "Forest (Grün)",
        "BG_BASE": "#0c1510",
        "BG_ELEVATED": "#111f18",
        "BG_OVERLAY": "#162a20",
        "BG_SIDEBAR": "#08100b",
        "BG_GRADIENT_1": "#0c1510",
        "BG_GRADIENT_2": "#101e17",
        "ACCENT": "#10b981",
        "ACCENT_HOVER": "#34d399",
        "ACCENT_DARK": "#059669",
        "ACCENT_GLOW": "#6ee7b7",
        "ACCENT_2": "#22c55e",
        "SUCCESS": "#10b981",
        "WARNING": "#f59e0b",
        "DANGER": "#ef4444",
        "INFO": "#3b82f6",
        "TEXT_PRIMARY": "#ecfdf5",
        "TEXT_SECONDARY": "#7a9e8c",
        "TEXT_MUTED": "#3d5e50",
        "BORDER": "#163228",
        "BORDER_LIGHT": "#1f4738",
        "FONT": "Segoe UI Variable Display, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
    "light": {
        "name": "Light (Hell)",
        "BG_BASE": "#f5f7fa",
        "BG_ELEVATED": "#ffffff",
        "BG_OVERLAY": "#e8ecf1",
        "BG_SIDEBAR": "#e5e8ed",
        "BG_GRADIENT_1": "#f5f7fa",
        "BG_GRADIENT_2": "#eef1f5",
        "ACCENT": "#6366f1",
        "ACCENT_HOVER": "#818cf8",
        "ACCENT_DARK": "#4f46e5",
        "ACCENT_GLOW": "#a5b4fc",
        "ACCENT_2": "#8b5cf6",
        "SUCCESS": "#059669",
        "WARNING": "#d97706",
        "DANGER": "#dc2626",
        "INFO": "#2563eb",
        "TEXT_PRIMARY": "#0f172a",
        "TEXT_SECONDARY": "#475569",
        "TEXT_MUTED": "#94a3b8",
        "BORDER": "#d1d8e0",
        "BORDER_LIGHT": "#b8c0cc",
        "FONT": "Segoe UI Variable Display, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
}


_current = "slate"


def set_theme(name: str):
    global _current
    if name in THEMES:
        _current = name


def get_theme_name() -> str:
    return _current


def get_theme() -> dict:
    return THEMES.get(_current, THEMES["slate"])


def list_themes() -> list:
    return [(k, v["name"]) for k, v in THEMES.items()]


class _ColorsProxy:
    def __getattr__(self, name):
        theme = get_theme()
        return theme.get(name, "#ff0000")


Colors = _ColorsProxy()


FONT_FAMILY = "Segoe UI Variable Display, Segoe UI, sans-serif"
FONT_MONO = "Cascadia Code, Consolas, monospace"


class Icons:
    DASHBOARD = "📊"
    GAMES = "🎮"
    CLEANER = "🧹"
    PROCESSES = "⚙️"
    NETWORK = "🌐"
    STARTUP = "🚀"
    PRIVACY = "🔒"
    DEV = "💻"
    SYSTEM = "🖥️"
    SETTINGS = "⚙"


def get_stylesheet() -> str:
    c = get_theme()
    return f"""
    /* ═════════ GLOBAL ═════════ */
    * {{ font-family: {c['FONT']}; outline: none; }}

    QMainWindow, QWidget {{
        background-color: {c['BG_BASE']};
        color: {c['TEXT_PRIMARY']};
    }}

    /* ═════════ SIDEBAR ═════════ */
    #Sidebar {{
        background-color: {c['BG_SIDEBAR']};
        border-right: 1px solid {c['BORDER']};
    }}

    #Logo {{
        color: {c['TEXT_PRIMARY']};
        font-size: 16px;
        font-weight: 800;
        padding: 26px 24px 18px 24px;
        letter-spacing: 0.3px;
        background-color: transparent;
    }}

    #CategoryLabel {{
        color: {c['TEXT_MUTED']};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        padding: 20px 24px 8px 24px;
        background-color: transparent;
    }}

    QPushButton#NavButton {{
        background-color: transparent;
        color: {c['TEXT_SECONDARY']};
        border: none;
        border-radius: 10px;
        padding: 11px 18px;
        text-align: left;
        font-size: 13px;
        font-weight: 500;
        margin: 2px 14px;
    }}
    QPushButton#NavButton:hover {{
        background-color: {c['BG_OVERLAY']};
        color: {c['TEXT_PRIMARY']};
    }}
    QPushButton#NavButton:checked {{
        background-color: {c['BG_OVERLAY']};
        color: {c['ACCENT']};
        font-weight: 700;
    }}

    /* ═════════ CARDS ═════════ */
    #Card {{
        background-color: {c['BG_ELEVATED']};
        border: 1px solid {c['BORDER']};
        border-radius: 14px;
    }}

    #CardTitle {{
        color: {c['TEXT_SECONDARY']};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
    }}

    #CardValue {{
        color: {c['TEXT_PRIMARY']};
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}

    /* ═════════ HEADINGS ═════════ */
    QLabel#PageTitle {{
        font-size: 28px;
        font-weight: 800;
        color: {c['TEXT_PRIMARY']};
        letter-spacing: -0.5px;
        padding: 0;
    }}
    QLabel#PageSubtitle {{
        font-size: 13px;
        color: {c['TEXT_SECONDARY']};
        padding: 0;
    }}

    /* ═════════ BUTTONS ═════════ */
    QPushButton {{
        background-color: transparent;
        color: {c['TEXT_PRIMARY']};
        border: 1px solid {c['BORDER_LIGHT']};
        border-radius: 10px;
        padding: 10px 22px;
        font-size: 13px;
        font-weight: 600;
        min-height: 22px;
    }}
    QPushButton:hover {{
        background-color: {c['ACCENT']};
        color: white;
        border-color: {c['ACCENT']};
    }}
    QPushButton:pressed {{
        background-color: {c['ACCENT_DARK']};
    }}
    QPushButton:disabled {{
        background-color: transparent;
        color: {c['TEXT_MUTED']};
        border-color: {c['BORDER']};
    }}

    QPushButton#PrimaryButton {{
        background-color: {c['ACCENT']};
        color: white;
        border: none;
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {c['ACCENT_HOVER']};
    }}

    QPushButton#SecondaryButton {{
        background-color: transparent;
        color: {c['TEXT_SECONDARY']};
        border: 1px solid {c['BORDER_LIGHT']};
    }}
    QPushButton#SecondaryButton:hover {{
        border-color: {c['ACCENT']};
        color: {c['ACCENT']};
        background-color: {c['BG_OVERLAY']};
    }}

    QPushButton#DangerButton {{
        background-color: transparent;
        color: {c['DANGER']};
        border: 1px solid {c['DANGER']};
    }}
    QPushButton#DangerButton:hover {{
        background-color: {c['DANGER']};
        color: white;
    }}

    /* ═════════ PROGRESS BARS ═════════ */
    QProgressBar {{
        background-color: {c['BG_OVERLAY']};
        border: none;
        border-radius: 5px;
        height: 6px;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background-color: {c['ACCENT']};
        border-radius: 5px;
    }}
    QProgressBar#Success::chunk {{ background-color: {c['SUCCESS']}; }}
    QProgressBar#Warning::chunk {{ background-color: {c['WARNING']}; }}
    QProgressBar#Danger::chunk  {{ background-color: {c['DANGER']}; }}

    /* ═════════ LISTS ═════════ */
    QListWidget, QTreeWidget, QTableWidget {{
        background-color: {c['BG_ELEVATED']};
        border: 1px solid {c['BORDER']};
        border-radius: 12px;
        padding: 6px;
        color: {c['TEXT_PRIMARY']};
        font-size: 13px;
    }}
    QListWidget::item, QTreeWidget::item {{
        padding: 11px 14px;
        border-radius: 8px;
        margin: 2px 0;
    }}
    QListWidget::item:hover {{
        background-color: {c['BG_OVERLAY']};
    }}
    QListWidget::item:selected {{
        background-color: {c['BG_OVERLAY']};
        color: {c['ACCENT']};
    }}

    /* ═════════ INPUTS ═════════ */
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {c['BG_ELEVATED']};
        color: {c['TEXT_PRIMARY']};
        border: 1px solid {c['BORDER']};
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 13px;
        min-height: 22px;
        selection-background-color: {c['ACCENT']};
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {c['ACCENT']};
    }}
    QLineEdit::placeholder {{ color: {c['TEXT_MUTED']}; }}
    QComboBox::drop-down {{ border: none; width: 26px; }}
    QComboBox QAbstractItemView {{
        background-color: {c['BG_ELEVATED']};
        color: {c['TEXT_PRIMARY']};
        border: 1px solid {c['BORDER_LIGHT']};
        border-radius: 10px;
        selection-background-color: {c['ACCENT']};
        padding: 6px;
    }}

    /* ═════════ CHECKBOX ═════════ */
    QCheckBox {{
        color: {c['TEXT_PRIMARY']};
        spacing: 10px;
        font-size: 13px;
    }}
    QCheckBox::indicator {{
        width: 20px; height: 20px;
        border-radius: 5px;
        border: 2px solid {c['BORDER_LIGHT']};
        background-color: {c['BG_ELEVATED']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['ACCENT']};
        border: 2px solid {c['ACCENT']};
    }}
    QCheckBox::indicator:hover {{
        border-color: {c['ACCENT']};
    }}

    /* ═════════ GROUP BOX ═════════ */
    QGroupBox {{
        color: {c['TEXT_SECONDARY']};
        border: 1px solid {c['BORDER']};
        border-radius: 12px;
        margin-top: 16px;
        padding: 20px;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.8px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 10px;
        color: {c['TEXT_SECONDARY']};
    }}

    /* ═════════ TABS ═════════ */
    QTabWidget::pane {{
        border: 1px solid {c['BORDER']};
        border-radius: 12px;
        background-color: {c['BG_ELEVATED']};
        top: -1px;
    }}
    QTabBar::tab {{
        background-color: transparent;
        color: {c['TEXT_SECONDARY']};
        padding: 10px 22px;
        margin-right: 4px;
        border: 1px solid transparent;
        border-radius: 10px;
        font-weight: 600;
        font-size: 12px;
    }}
    QTabBar::tab:hover {{
        background-color: {c['BG_OVERLAY']};
        color: {c['TEXT_PRIMARY']};
    }}
    QTabBar::tab:selected {{
        background-color: {c['ACCENT']};
        color: white;
    }}

    /* ═════════ SCROLLBAR ═════════ */
    QScrollBar:vertical {{
        background: transparent; width: 10px; margin: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['BORDER_LIGHT']};
        border-radius: 5px;
        min-height: 40px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['ACCENT']};
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QScrollBar:horizontal {{
        background: transparent; height: 10px; margin: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {c['BORDER_LIGHT']};
        border-radius: 5px;
        min-width: 40px;
    }}

    /* ═════════ TOOLTIPS ═════════ */
    QToolTip {{
        background-color: {c['BG_ELEVATED']};
        color: {c['TEXT_PRIMARY']};
        border: 1px solid {c['ACCENT']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
    }}

    /* ═════════ STATUS BAR ═════════ */
    QStatusBar {{
        background-color: {c['BG_SIDEBAR']};
        color: {c['TEXT_SECONDARY']};
        border-top: 1px solid {c['BORDER']};
        font-size: 12px;
        padding: 4px 12px;
    }}

    QLabel {{ color: {c['TEXT_PRIMARY']}; background-color: transparent; }}

    QFrame[frameShape="4"] {{
        background-color: {c['BORDER']};
        max-height: 1px;
        border: none;
    }}
    """