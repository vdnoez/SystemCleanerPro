"""Lädt externe JSON-Configs. Damit kannst du Regeln ändern
   ohne die EXE neu zu bauen."""
import json
import os
from functools import lru_cache
from pathlib import Path

from src.core.config import DATA_DIR


@lru_cache(maxsize=None)
def load_json(filename: str) -> dict:
    """Lädt eine JSON-Datei aus data/. Cached für Performance."""
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[config_loader] Fehler beim Laden von {filename}: {e}")
        return {}


def reload_all():
    """Cache leeren — beim nächsten load_json() wird neu gelesen."""
    load_json.cache_clear()


def expand_path(p: str) -> Path:
    """Ersetzt %TEMP% etc. mit echten Pfaden."""
    return Path(os.path.expandvars(p))


def get_cleanup_rules() -> dict:
    return load_json("cleanup_rules.json")


def get_games() -> dict:
    return load_json("games.json")


def get_windows_temp_dirs() -> list[Path]:
    rules = get_cleanup_rules()
    dirs = rules.get("windows_temp_dirs", [])
    return [expand_path(d) for d in dirs if expand_path(d).exists()]


def get_dev_patterns() -> set[str]:
    rules = get_cleanup_rules()
    return set(rules.get("dev_temp_patterns", []))


def get_max_depth() -> int:
    return get_cleanup_rules().get("max_scan_depth", 6)