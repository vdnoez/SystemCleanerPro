"""Feature-Gate — Pro-Features ohne Lizenz sperren."""
from src.modules.license import is_licensed, get_license_status


# ═══════════════════════════════════════════════════════════════
# KONFIGURATION
# ═══════════════════════════════════════════════════════════════

FREE_PAGES = {
    "Health-Check",
    "Dashboard",
    "System-Info",
    "Prozesse",
    "Netzwerk",
    "BSOD",
    "Downloads",
    "Lizenz",
}

PRO_PAGES = {
    "Cleaner",
    "Software-Updater",
    "RAM",
    "Shredder",
    "Autostart",
    "App-Update",
    "Passwort",
    "Games",
}


def is_pro() -> bool:
    """Prüft ob Pro-Lizenz aktiv."""
    try:
        return is_licensed()
    except Exception:
        return False


def is_page_locked(page_name: str) -> bool:
    """Prüft ob eine Seite gesperrt ist."""
    if page_name in FREE_PAGES:
        return False
    if page_name in PRO_PAGES:
        return not is_pro()
    return False


def get_license_badge() -> dict:
    """Status-Badge für Sidebar."""
    try:
        status = get_license_status()
        if status["status"] == "valid":
            return {"text": "PRO", "color": "#10b981"}
        elif status["status"] == "trial":
            days = status.get("trial_days_left", 0)
            return {"text": f"TRIAL {days}T", "color": "#f59e0b"}
        elif status["status"] == "expired":
            return {"text": "FREE", "color": "#ef4444"}
        else:
            return {"text": "FREE", "color": "#ef4444"}
    except Exception:
        return {"text": "FREE", "color": "#ef4444"}