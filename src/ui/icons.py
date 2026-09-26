"""Icon-Helper mit qtawesome."""
try:
    import qtawesome as qta
    HAS_QTA = True
except ImportError:
    HAS_QTA = False

from PyQt6.QtGui import QIcon

from src.ui.theme import Colors


# ─── Icon-Mapping ─────────────────────────────────────────────
ICON_MAP = {
    "dashboard":  "fa5s.tachometer-alt",
    "games":      "fa5s.gamepad",
    "cleaner":    "fa5s.broom",
    "ram":        "fa5s.memory",
    "processes":  "fa5s.cogs",
    "network":    "fa5s.network-wired",
    "startup":    "fa5s.rocket",
    "shredder":   "fa5s.fire",
    "settings":   "fa5s.cog",
    "about":      "fa5s.info-circle",
    "exit":       "fa5s.sign-out-alt",
    "refresh":    "fa5s.sync-alt",
    "search":     "fa5s.search",
    "check":      "fa5s.check",
    "close":      "fa5s.times",
    "warning":    "fa5s.exclamation-triangle",
    "trash":      "fa5s.trash-alt",
    "shield":     "fa5s.shield-alt",
    "bolt":       "fa5s.bolt",
    "cpu":        "fa5s.microchip",
    "disk":       "fa5s.hdd",
    "download":   "fa5s.download",
    "upload":     "fa5s.upload",
    "folder":     "fa5s.folder",
    "file":       "fa5s.file",
}


def icon(name: str, color: str = None) -> QIcon:
    """Gibt ein QIcon zurück. Fallback wenn qtawesome fehlt."""
    if not HAS_QTA:
        return QIcon()
    fa_name = ICON_MAP.get(name, name)
    if color is None:
        color = Colors.TEXT_PRIMARY
    try:
        return qta.icon(fa_name, color=color)
    except Exception:
        return QIcon()


def icon_text(name: str, text: str) -> str:
    """Fallback: Emoji statt Icon."""
    emoji_map = {
        "dashboard": "📊", "games": "🎮", "cleaner": "🧹",
        "ram": "💾", "processes": "⚙️", "network": "🌐",
        "startup": "🚀", "shredder": "🔥", "settings": "⚙",
        "about": "ℹ️", "exit": "🚪", "refresh": "🔄",
        "search": "🔍", "check": "✅", "close": "✖",
        "warning": "⚠️", "trash": "🗑️",
    }
    return f"{emoji_map.get(name, '')}  {text}"