"""Globale Konfiguration & Konstanten."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# APP-INFO
# ═══════════════════════════════════════════════════════════════
APP_NAME = "System Diagnostic & Cleaner Pro"
APP_OWNER = "vdnoez"          # ⭐ Besitzer
APP_AUTHOR = "vdnoez"


def _load_version() -> str:
    """Liest Version aus version.txt (neben der EXE)."""
    try:
        version_file = Path(__file__).resolve().parents[2] / "version.txt"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return "1.0.0"


APP_VERSION = _load_version()


# ═══════════════════════════════════════════════════════════════
# GITHUB (für Auto-Update & Download-Statistik)
# ═══════════════════════════════════════════════════════════════
GITHUB_USER = "vdnoez"
GITHUB_REPO = "SystemCleanerPro"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}"
GITHUB_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}"


# ═══════════════════════════════════════════════════════════════
# PFADE
# ═══════════════════════════════════════════════════════════════
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / ".reports"
LOGS_DIR = PROJECT_ROOT / ".logs"

for d in (DATA_DIR, REPORTS_DIR, LOGS_DIR):
    d.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# DESIGN
# ═══════════════════════════════════════════════════════════════
THEME = "slate"   # Standard-Theme