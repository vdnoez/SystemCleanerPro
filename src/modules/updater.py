"""Auto-Updater via GitHub Releases."""
import os
import sys
import json
import subprocess
import tempfile
import hashlib
from pathlib import Path
from typing import Callable

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from src.core.config import APP_VERSION, GITHUB_API


def parse_version(v: str) -> tuple:
    """Wandelt '1.2.3' in (1, 2, 3) um."""
    v = v.lstrip("v").strip()
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def is_newer(latest: str, current: str) -> bool:
    """Prüft ob latest > current."""
    return parse_version(latest) > parse_version(current)


def check_for_update(timeout: int = 10) -> dict:
    """
    Prüft GitHub auf neueste Version.
    Returns dict mit:
      - update_available: bool
      - latest_version: str
      - current_version: str
      - download_url: str
      - release_notes: str
      - release_url: str
      - published_at: str
      - error: str (falls Fehler)
    """
    result = {
        "update_available": False,
        "latest_version": APP_VERSION,
        "current_version": APP_VERSION,
        "download_url": "",
        "release_notes": "",
        "release_url": "",
        "published_at": "",
        "error": "",
    }

    if not HAS_REQUESTS:
        result["error"] = "requests-Bibliothek fehlt"
        return result

    try:
        r = requests.get(
            f"{GITHUB_API}/releases/latest",
            timeout=timeout,
            headers={"Accept": "application/vnd.github+json"}
        )

        if r.status_code == 404:
            result["error"] = "Kein Release auf GitHub gefunden"
            return result
        if r.status_code != 200:
            result["error"] = f"HTTP {r.status_code}"
            return result

        data = r.json()
        tag = data.get("tag_name", "").lstrip("v")
        result["latest_version"] = tag
        result["release_notes"] = data.get("body", "")
        result["release_url"] = data.get("html_url", "")
        result["published_at"] = data.get("published_at", "")

        if not is_newer(tag, APP_VERSION):
            return result

        # Download-URL für .exe finden
        assets = data.get("assets", [])
        for asset in assets:
            name = asset.get("name", "").lower()
            if name.endswith(".exe"):
                result["download_url"] = asset.get("browser_download_url", "")
                break

        if not result["download_url"]:
            result["error"] = "Keine .exe im Release gefunden"
            return result

        result["update_available"] = True
        return result

    except requests.Timeout:
        result["error"] = "Zeitüberschreitung"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def download_update(url: str, progress_cb: Callable = None) -> tuple:
    """
    Lädt die neue .exe herunter.
    Returns (success, path_or_error).
    """
    if not HAS_REQUESTS:
        return False, "requests fehlt"

    try:
        tmp_dir = Path(tempfile.gettempdir()) / "CleanerProUpdate"
        tmp_dir.mkdir(exist_ok=True)
        new_exe = tmp_dir / "SystemCleanerPro_new.exe"

        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()

        total = int(r.headers.get("content-length", 0))
        downloaded = 0

        with open(new_exe, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb and total > 0:
                        pct = int(downloaded / total * 100)
                        progress_cb(pct, downloaded, total)

        return True, str(new_exe)

    except Exception as e:
        return False, str(e)


def apply_update(new_exe_path: str) -> tuple:
    """
    Ersetzt die aktuelle .exe durch die neue.
    Nutzt ein Batch-Skript das nach App-Ende läuft.
    Returns (success, message).
    """
    try:
        if getattr(sys, "frozen", False):
            # Läuft als EXE
            current_exe = Path(sys.executable)
        else:
            # Läuft als Python-Skript — Update nicht möglich
            return False, "Update nur in EXE-Version möglich"

        # Batch-Skript erstellen
        batch_path = Path(tempfile.gettempdir()) / "cleaner_update.bat"
        batch_content = f"""@echo off
chcp 65001 >nul
title Cleaner Pro Update

echo.
echo ================================================
echo   Cleaner Pro - Update wird installiert...
echo ================================================
echo.

REM Warte bis App beendet ist
timeout /t 3 /nobreak >nul

REM Alte EXE löschen
:retry_delete
del "{current_exe}" 2>nul
if exist "{current_exe}" (
    timeout /t 2 /nobreak >nul
    goto retry_delete
)

REM Neue EXE kopieren
copy /Y "{new_exe_path}" "{current_exe}"
if errorlevel 1 (
    echo FEHLER beim Kopieren!
    pause
    exit /b 1
)

echo.
echo Update erfolgreich! Starte App neu...
timeout /t 2 /nobreak >nul

REM Neue Version starten
start "" "{current_exe}"

REM Aufräumen
del "%~f0"
"""
        batch_path.write_text(batch_content, encoding="utf-8")

        # Batch ausführen und App beenden
        subprocess.Popen(
            ["cmd.exe", "/c", str(batch_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        return True, "Update wird installiert. App startet neu..."

    except Exception as e:
        return False, str(e)


def get_download_size(url: str) -> int:
    """Holt Dateigröße ohne Download."""
    if not HAS_REQUESTS:
        return 0
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        return int(r.headers.get("content-length", 0))
    except Exception:
        return 0


def format_bytes(b: int) -> str:
    """Formatiert Bytes in lesbare Größe."""
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"