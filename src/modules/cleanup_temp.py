"""Räumt alte _MEI-Ordner von PyInstaller auf."""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta


def cleanup_old_mei(max_age_hours: int = 6) -> int:
    """
    Löscht alte _MEIxxxxx-Ordner aus %TEMP%.
    Nur Ordner die älter als `max_age_hours` sind.
    Returns: Anzahl gelöschter Ordner
    """
    if not getattr(sys, "frozen", False):
        return 0

    try:
        temp = Path(os.environ.get("TEMP", ""))
        if not temp.exists():
            return 0

        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        removed = 0

        for folder in temp.glob("_MEI*"):
            try:
                if not folder.is_dir():
                    continue
                mtime = datetime.fromtimestamp(folder.stat().st_mtime)
                if mtime < cutoff:
                    shutil.rmtree(folder, ignore_errors=True)
                    removed += 1
            except Exception:
                continue

        return removed
    except Exception:
        return 0


def cleanup_all_mei() -> int:
    """Löscht ALLE _MEI-Ordner (auch die aktuellen)."""
    try:
        temp = Path(os.environ.get("TEMP", ""))
        if not temp.exists():
            return 0

        removed = 0
        for folder in temp.glob("_MEI*"):
            try:
                if folder.is_dir():
                    shutil.rmtree(folder, ignore_errors=True)
                    removed += 1
            except Exception:
                continue

        return removed
    except Exception:
        return 0


def get_mei_size() -> float:
    """Berechnet Gesamtgröße aller _MEI-Ordner in MB."""
    try:
        temp = Path(os.environ.get("TEMP", ""))
        if not temp.exists():
            return 0.0

        total = 0
        for folder in temp.glob("_MEI*"):
            try:
                if folder.is_dir():
                    for f in folder.rglob("*"):
                        try:
                            if f.is_file():
                                total += f.stat().st_size
                        except OSError:
                            continue
            except Exception:
                continue

        return round(total / (1024 * 1024), 2)
    except Exception:
        return 0.0