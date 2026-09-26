"""Theme-System mit 6 umschaltbaren Themes."""


# ═══════════════════════════════════════════════════════════════
# THEME-DEFINITIONEN
# ═══════════════════════════════════════════════════════════════
THEMES = {
    "aurora": {
        "name": "Aurora (Standard)",
        "BG_BASE": "#0a0e1a",
        "BG_GRADIENT_1": "#0f1729",
        "BG_GRADIENT_2": "#1a1f3a",
        "BG_ELEVATED": "#141a2e",
        "BG_GLASS": "#1a2140",
        "BG_OVERLAY": "#1f2844",
        "BG_SIDEBAR": "#0d1320",
        "ACCENT": "#06b6d4",
        "ACCENT_2": "#3b82f6",
        "ACCENT_HOVER": "#22d3ee",
        "ACCENT_DARK": "#0891b2",
        "ACCENT_GLOW": "#67e8f9",
        "SUCCESS": "#10b981",
        "WARNING": "#f59e0b",
        "DANGER": "#ef4444",
        "INFO": "#60a5fa",
        "TEXT_PRIMARY": "#f0f9ff",
        "TEXT_SECONDARY": "#94a3b8",
        "TEXT_MUTED": "#475569",
        "BORDER": "#1e2a4a",
        "BORDER_LIGHT": "#2d3d66",
        "FONT": "Segoe UI Variable, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
    "sunset": {
        "name": "Sunset (Orange-Pink)",
        "BG_BASE": "#1a0f0a",
        "BG_GRADIENT_1": "#2a1410",
        "BG_GRADIENT_2": "#3a1a1f",
        "BG_ELEVATED": "#281410",
        "BG_GLASS": "#331a18",
        "BG_OVERLAY": "#3d2020",
        "BG_SIDEBAR": "#1f0f0a",
        "ACCENT": "#f97316",
        "ACCENT_2": "#ec4899",
        "ACCENT_HOVER": "#fb923c",
        "ACCENT_DARK": "#ea580c",
        "ACCENT_GLOW": "#fdba74",
        "SUCCESS": "#10b981",
        "WARNING": "#fbbf24",
        "DANGER": "#ef4444",
        "INFO": "#60a5fa",
        "TEXT_PRIMARY": "#fff7ed",
        "TEXT_SECONDARY": "#a8998a",
        "TEXT_MUTED": "#695a4a",
        "BORDER": "#3a201a",
        "BORDER_LIGHT": "#5c3428",
        "FONT": "Segoe UI Variable, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
    "emerald": {
        "name": "Emerald (Grün)",
        "BG_BASE": "#051612",
        "BG_GRADIENT_1": "#082019",
        "BG_GRADIENT_2": "#0d2a20",
        "BG_ELEVATED": "#0a1e18",
        "BG_GLASS": "#0f2820",
        "BG_OVERLAY": "#133328",
        "BG_SIDEBAR": "#061a14",
        "ACCENT": "#10b981",
        "ACCENT_2": "#06b6d4",
        "ACCENT_HOVER": "#34d399",
        "ACCENT_DARK": "#059669",
        "ACCENT_GLOW": "#6ee7b7",
        "SUCCESS": "#10b981",
        "WARNING": "#f59e0b",
        "DANGER": "#ef4444",
        "INFO": "#60a5fa",
        "TEXT_PRIMARY": "#ecfdf5",
        "TEXT_SECONDARY": "#7a9d8f",
        "TEXT_MUTED": "#3d5d50",
        "BORDER": "#0f2a22",
        "BORDER_LIGHT": "#1d4536",
        "FONT": "Segoe UI Variable, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
    "royal": {
        "name": "Royal (Violett)",
        "BG_BASE": "#0d0620",
        "BG_GRADIENT_1": "#150a2e",
        "BG_GRADIENT_2": "#1f1140",
        "BG_ELEVATED": "#120a28",
        "BG_GLASS": "#1a0f38",
        "BG_OVERLAY": "#22154a",
        "BG_SIDEBAR": "#0a0518",
        "ACCENT": "#a855f7",
        "ACCENT_2": "#ec4899",
        "ACCENT_HOVER": "#c084fc",
        "ACCENT_DARK": "#9333ea",
        "ACCENT_GLOW": "#d8b4fe",
        "SUCCESS": "#10b981",
        "WARNING": "#f59e0b",
        "DANGER": "#ef4444",
        "INFO": "#60a5fa",
        "TEXT_PRIMARY": "#faf5ff",
        "TEXT_SECONDARY": "#9d8ab8",
        "TEXT_MUTED": "#5c4a7a",
        "BORDER": "#1e1040",
        "BORDER_LIGHT": "#331a5e",
        "FONT": "Segoe UI Variable, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
    "mono": {
        "name": "Mono (Schwarz-Weiß)",
        "BG_BASE": "#0a0a0a",
        "BG_GRADIENT_1": "#101010",
        "BG_GRADIENT_2": "#161616",
        "BG_ELEVATED": "#121212",
        "BG_GLASS": "#181818",
        "BG_OVERLAY": "#1f1f1f",
        "BG_SIDEBAR": "#060606",
        "ACCENT": "#e5e5e5",
        "ACCENT_2": "#a3a3a3",
        "ACCENT_HOVER": "#f5f5f5",
        "ACCENT_DARK": "#a3a3a3",
        "ACCENT_GLOW": "#ffffff",
        "SUCCESS": "#22c55e",
        "WARNING": "#eab308",
        "DANGER": "#ef4444",
        "INFO": "#3b82f6",
        "TEXT_PRIMARY": "#fafafa",
        "TEXT_SECONDARY": "#737373",
        "TEXT_MUTED": "#404040",
        "BORDER": "#1f1f1f",
        "BORDER_LIGHT": "#333333",
        "FONT": "Segoe UI Variable, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
    "light_aurora": {
        "name": "Light Aurora (Hell)",
        "BG_BASE": "#f0f4f8",
        "BG_GRADIENT_1": "#f8fafc",
        "BG_GRADIENT_2": "#e0f2fe",
        "BG_ELEVATED": "#ffffff",
        "BG_GLASS": "#f1f5f9",
        "BG_OVERLAY": "#e2e8f0",
        "BG_SIDEBAR": "#e2e8f0",
        "ACCENT": "#0891b2",
        "ACCENT_2": "#3b82f6",
        "ACCENT_HOVER": "#06b6d4",
        "ACCENT_DARK": "#0e7490",
        "ACCENT_GLOW": "#67e8f9",
        "SUCCESS": "#059669",
        "WARNING": "#d97706",
        "DANGER": "#dc2626",
        "INFO": "#2563eb",
        "TEXT_PRIMARY": "#0f172a",
        "TEXT_SECONDARY": "#475569",
        "TEXT_MUTED": "#94a3b8",
        "BORDER": "#cbd5e1",
        "BORDER_LIGHT": "#94a3b8",
        "FONT": "Segoe UI Variable, Segoe UI, sans-serif",
        "MONO": "Cascadia Code, Consolas, monospace",
    },
}


# ═══════════════════════════════════════════════════════════════
# AKTIVES THEME
# ═══════════════════════════════════════════════════════════════
_current = "aurora"


def set_theme(name: str):
    global _current
    if name in THEMES:
        _current = name


def get_theme_name() -> str:
    return _current


def get_theme() -> dict:
    return THEMES.get(_current, THEMES["aurora"])


def list_themes() -> list:
    return [(k, v["name"]) for k, v in THEMES.items()]


class _ColorsProxy:
    def __getattr__(self, name):
        theme = get_theme()
        return theme.get(name, "#ff0000")


Colors = _ColorsProxy()


FONT_FAMILY = "Segoe UI Variable, Segoe UI, sans-serif"
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


# ═══════════════════════════════════════════════════════════════
# STYLESHEET
# ═══════════════════════════════════════════════════════════════
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
        color: {c['ACCENT']};
        font-size: 16px;
        font-weight: 800;
        padding: 26px 22px;
        border-bottom: 1px solid {c['BORDER']};
        letter-spacing: 0.3px;
    }}

    #CategoryLabel {{
        color: {c['TEXT_MUTED']};
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.8px;
        padding: 16px 22px 6px 22px;
        background-color: transparent;
    }}

    QPushButton#NavButton {{
        background-color: transparent;
        color: {c['TEXT_SECONDARY']};
        border: none;
        border-radius: 10px;
        padding: 10px 18px;
        text-align: left;
        font-size: 13px;
        font-weight: 500;
        margin: 2px 12px;
    }}
    QPushButton#NavButton:hover {{
        background-color: {c['BG_OVERLAY']};
        color: {c['TEXT_PRIMARY']};
    }}
    QPushButton#NavButton:checked {{
        background-color: {c['ACCENT']};
        color: white;
        font-weight: 700;
    }}

    /* ═════════ CARDS ═════════ */
    #Card {{
        background-color: {c['BG_GLASS']};
        border: 1px solid {c['BORDER']};
        border-radius: 16px;
    }}

    #CardTitle {{
        color: {c['TEXT_SECONDARY']};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
    }}

    #CardValue {{
        color: {c['ACCENT']};
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -1px;
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
        background-color: {c['ACCENT']};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 11px 24px;
        font-size: 13px;
        font-weight: 700;
        min-height: 22px;
    }}
    QPushButton:hover {{ background-color: {c['ACCENT_HOVER']}; }}
    QPushButton:pressed {{ background-color: {c['ACCENT_DARK']}; }}
    QPushButton:disabled {{
        background-color: {c['BORDER']};
        color: {c['TEXT_MUTED']};
    }}

    QPushButton#SecondaryButton {{
        background-color: transparent;
        color: {c['TEXT_PRIMARY']};
        border: 1.5px solid {c['BORDER_LIGHT']};
    }}
    QPushButton#SecondaryButton:hover {{
        border-color: {c['ACCENT']};
        color: {c['ACCENT']};
        background-color: {c['BG_OVERLAY']};
    }}

    QPushButton#DangerButton {{
        background-color: {c['DANGER']};
    }}
    QPushButton#DangerButton:hover {{
        background-color: #fca5a5;
    }}

    /* ═════════ PROGRESS BARS ═════════ */
    QProgressBar {{
        background-color: {c['BG_OVERLAY']};
        border: none;
        border-radius: 5px;
        height: 8px;
        text-align: center;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background-color: {c['ACCENT']};
        border-radius: 5px;
    }}
    QProgressBar#Success::chunk {{ background-color: {c['SUCCESS']}; }}
    QProgressBar#Warning::chunk {{ background-color: {c['WARNING']}; }}
    QProgressBar#Danger::chunk  {{ background-color: {c['DANGER']}; }}

    /* ═════════ LISTS / TABLES ═════════ */
    QListWidget, QTreeWidget, QTableWidget {{
        background-color: {c['BG_GLASS']};
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
    QListWidget::item:hover, QTreeWidget::item:hover {{
        background-color: {c['BG_OVERLAY']};
    }}
    QListWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {c['ACCENT']};
        color: white;
    }}

    /* ═════════ INPUTS ═════════ */
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {c['BG_OVERLAY']};
        color: {c['TEXT_PRIMARY']};
        border: 1.5px solid {c['BORDER']};
        border-radius: 12px;
        padding: 8px 14px;
        font-size: 13px;
        min-height: 20px;
        selection-background-color: {c['ACCENT']};
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1.5px solid {c['ACCENT']};
    }}
    QLineEdit::placeholder {{ color: {c['TEXT_MUTED']}; }}
    QComboBox::drop-down {{ border: none; width: 26px; }}
    QComboBox QAbstractItemView {{
        background-color: {c['BG_ELEVATED']};
        color: {c['TEXT_PRIMARY']};
        border: 1.5px solid {c['BORDER_LIGHT']};
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
        width: 18px; height: 18px;
        border-radius: 5px;
        border: 1.5px solid {c['BORDER_LIGHT']};
        background-color: {c['BG_OVERLAY']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['ACCENT']};
        border: 1.5px solid {c['ACCENT']};
    }}
    QCheckBox::indicator:hover {{ border-color: {c['ACCENT']}; }}

    /* ═════════ GROUP BOX ═════════ */
    QGroupBox {{
        color: {c['TEXT_SECONDARY']};
        border: 1.5px solid {c['BORDER']};
        border-radius: 14px;
        margin-top: 16px;
        padding: 20px;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.5px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 10px;
    }}

    /* ═════════ SCROLLBAR ═════════ */
    QScrollBar:vertical {{
        background: transparent; width: 10px; margin: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['BORDER_LIGHT']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {c['ACCENT']}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QScrollBar:horizontal {{
        background: transparent; height: 10px; margin: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {c['BORDER_LIGHT']};
        border-radius: 5px;
        min-width: 30px;
    }}

    /* ═════════ TOOLTIPS ═════════ */
    QToolTip {{
        background-color: {c['BG_ELEVATED']};
        color: {c['TEXT_PRIMARY']};
        border: 1.5px solid {c['ACCENT']};
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 12px;
    }}

    /* ═════════ STATUS BAR ═════════ */
    QStatusBar {{
        background-color: {c['BG_SIDEBAR']};
        color: {c['TEXT_SECONDARY']};
        border-top: 1px solid {c['BORDER']};
        font-size: 12px;
    }}

    QLabel {{ color: {c['TEXT_PRIMARY']}; background-color: transparent; }}

    QFrame[frameShape="4"] {{
        background-color: {c['BORDER']};
        max-height: 1px;
        border: none;
    }}
    """