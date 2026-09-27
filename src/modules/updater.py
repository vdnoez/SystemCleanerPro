"""Auto-Updater via GitHub Releases — mit Encoding-Fix."""
import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from src.core.config import APP_VERSION, GITHUB_API


def _fix_ssl_for_frozen():
    """Setzt SSL_CERT_FILE wenn App als EXE läuft."""
    if not getattr(sys, "frozen", False):
        return
    try:
        import certifi
        cert_path = certifi.where()
        if os.path.exists(cert_path):
            os.environ["SSL_CERT_FILE"] = cert_path
            os.environ["REQUESTS_CA_BUNDLE"] = cert_path
            return
    except Exception:
        pass

    try:
        exe_dir = Path(sys.executable).parent
        candidates = [
            exe_dir / "_internal" / "certifi" / "cacert.pem",
            exe_dir / "certifi" / "cacert.pem",
            exe_dir / "_internal" / "cacert.pem",
            exe_dir / "cacert.pem",
        ]
        for cert_file in candidates:
            if cert_file.exists():
                os.environ["SSL_CERT_FILE"] = str(cert_file)
                os.environ["REQUESTS_CA_BUNDLE"] = str(cert_file)
                return
    except Exception:
        pass


_fix_ssl_for_frozen()


def parse_version(v: str) -> tuple:
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
    return parse_version(latest) > parse_version(current)


def check_for_update(timeout: int = 10) -> dict:
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
        if r.status_code == 401:
            result["error"] = "GitHub-Repo privat oder nicht vorhanden"
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

        assets = data.get("assets", [])
        for asset in assets:
            name = asset.get("name", "").lower()
            if name.endswith(".exe"):
                result["download_url"] = asset.get(
                    "browser_download_url", ""
                )
                break

        if not result["download_url"]:
            result["error"] = "Keine .exe im Release gefunden"
            return result

        result["update_available"] = True
        return result

    except requests.Timeout:
        result["error"] = "Zeitüberschreitung"
        return result
    except requests.exceptions.SSLError as e:
        result["error"] = f"SSL-Fehler: {str(e)[:100]}"
        return result
    except Exception as e:
        result["error"] = str(e)[:150]
        return result


def download_update(url: str, progress_cb: Callable = None) -> tuple:
    if not HAS_REQUESTS:
        return False, "requests fehlt"

    try:
        tmp_dir = Path(tempfile.gettempdir()) / "CleanerProUpdate"
        tmp_dir.mkdir(exist_ok=True)
        new_exe = tmp_dir / "SystemCleanerPro_new.exe"

        if new_exe.exists():
            try:
                new_exe.unlink()
            except Exception:
                pass

        r = requests.get(url, stream=True, timeout=60,
                         allow_redirects=True)
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
    except requests.exceptions.SSLError as e:
        return False, f"SSL-Fehler: {str(e)[:150]}"
    except Exception as e:
        return False, str(e)[:200]


def apply_update(new_exe_path: str) -> tuple:
    try:
        if getattr(sys, "frozen", False):
            current_exe = Path(sys.executable)
        else:
            return False, "Update nur in EXE-Version möglich"

        new_path = Path(new_exe_path)
        if not new_path.exists():
            return False, f"Update-Datei nicht gefunden: {new_exe_path}"

        script_path = Path(tempfile.gettempdir()) / "cleaner_update.ps1"

        cur = str(current_exe).replace("'", "''")
        new = str(new_path).replace("'", "''")

        ps_script = f"""
$ErrorActionPreference = 'SilentlyContinue'
$currentExe = '{cur}'
$newExe = '{new}'
$backupExe = "$currentExe.old"

Write-Host ""
Write-Host "================================================"
Write-Host "  Cleaner Pro - Update wird installiert..."
Write-Host "================================================"
Write-Host ""

Start-Sleep -Seconds 5

if (-not (Test-Path $newExe)) {{
    Write-Host "FEHLER: Neue EXE nicht gefunden:"
    Write-Host $newExe
    Read-Host "Enter zum Beenden"
    exit 1
}}

if (Test-Path $backupExe) {{
    Remove-Item $backupExe -Force -ErrorAction SilentlyContinue
}}

try {{
    Move-Item -Path $currentExe -Destination $backupExe -Force
    Write-Host "  [1/4] Alte Version gesichert"
}} catch {{
    Write-Host "FEHLER: Alte EXE konnte nicht umbenannt werden!"
    Read-Host "Enter zum Beenden"
    exit 1
}}

try {{
    Copy-Item -Path $newExe -Destination $currentExe -Force
    Write-Host "  [2/4] Neue Version kopiert"
}} catch {{
    Write-Host "FEHLER beim Kopieren!"
    Move-Item -Path $backupExe -Destination $currentExe -Force
    Read-Host "Enter zum Beenden"
    exit 1
}}

if (-not (Test-Path $currentExe)) {{
    Write-Host "FEHLER: Neue EXE nicht angekommen!"
    Move-Item -Path $backupExe -Destination $currentExe -Force
    Read-Host "Enter zum Beenden"
    exit 1
}}

Write-Host "  [3/4] Update erfolgreich!"
Write-Host ""
Write-Host "Starte App in 3 Sekunden..."
Start-Sleep -Seconds 3

Start-Process -FilePath $currentExe

Write-Host "  [4/4] App gestartet"
Start-Sleep -Seconds 2

Remove-Item $backupExe -Force -ErrorAction SilentlyContinue
Remove-Item $newExe -Force -ErrorAction SilentlyContinue
Remove-Item $MyInvocation.MyCommand.Path -Force -ErrorAction SilentlyContinue
"""
        script_path.write_text(ps_script, encoding="utf-8-sig")

        subprocess.Popen(
            [
                "powershell.exe", "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", str(script_path)
            ],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        return True, (
            "Update wird installiert.\n\n"
            "1. Update-Fenster öffnet sich\n"
            "2. App wird beendet\n"
            "3. Neue Version startet automatisch"
        )
    except Exception as e:
        return False, str(e)


def get_download_size(url: str) -> int:
    if not HAS_REQUESTS:
        return 0
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        return int(r.headers.get("content-length", 0))
    except Exception:
        return 0


def format_bytes(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"