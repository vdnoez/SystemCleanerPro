"""Konfiguration."""
from pathlib import Path

APP_NAME = "System Diagnostic & Cleaner Pro"
# Version aus version.txt lesen
def _load_version() -> str:
    try:
        version_file = Path(__file__).resolve().parents[2] / "version.txt"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return "1.0.0"


APP_VERSION = _load_version()

# GitHub-Repo für Auto-Update
GITHUB_USER = "vdnoez"
GITHUB_REPO = "SystemCleanerPro"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / ".reports"
LOGS_DIR = PROJECT_ROOT / ".logs"

for d in (DATA_DIR, REPORTS_DIR, LOGS_DIR):
    d.mkdir(exist_ok=True)

THEME = "dark"
