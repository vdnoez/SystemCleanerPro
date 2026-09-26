"""Erkennt Spiele."""
import json, ctypes
from pathlib import Path
from typing import Iterator
import psutil
from src.core.config import DATA_DIR

GAME_DB_PATH = DATA_DIR / "games.json"
PROCESS_SET_INFORMATION = 0x0200
HIGH_PRIORITY_CLASS = 0x00000080


def load_game_db() -> dict:
    if not GAME_DB_PATH.exists():
        return {}
    return json.loads(GAME_DB_PATH.read_text(encoding="utf-8"))


def set_high_priority(pid: int) -> bool:
    try:
        k = ctypes.windll.kernel32
        h = k.OpenProcess(PROCESS_SET_INFORMATION, False, pid)
        if not h:
            return False
        ok = k.SetPriorityClass(h, HIGH_PRIORITY_CLASS)
        k.CloseHandle(h)
        return bool(ok)
    except Exception:
        return False


def detect_games() -> Iterator[dict]:
    db = load_game_db()
    if not db:
        return
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            name = (proc.info["name"] or "").lower()
            if name in db:
                yield {"name": name, "pid": proc.info["pid"], "meta": db[name]}
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
