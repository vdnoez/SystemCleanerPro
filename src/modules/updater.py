"""Auto-Updater via GitHub Releases — mit Fix für Update-Loop."""
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


# ═══════════════════════════════════════════════════════════════
# SSL-FIX für EXE
# ═══════════════════════════════════════════════════════════════
def _fix_ssl_for_frozen():
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
        for p in [
            exe_dir / "_internal" / "certifi" / "cacert.pem",
            exe_dir / "certifi" / "cacert.pem",
            exe_dir / "cacert.pem",
        ]:
            if p.exists():
                os.environ["SSL_CERT_FILE"] = str(p)
                os.environ["REQUESTS_CA_BUNDLE"] = str(p)
                return
    except Exception:
        pass


_fix_ssl_for_frozen()


# ═══════════════════════════════════════════════════════════════
# VERSION-VERGLEICH
# ═══════════════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════════════
# UPDATE-CHECK
# ═══════════════════════════════════════════════════════════════
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
            result["error"] = "Kein Release gefunden"
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
            if name.endswith(".zip"):
                result["download_url"] = asset.get(
                    "browser_download_url", ""
                )
                break

        if not result["download_url"]:
            result["error"] = "Keine .exe / .zip im Release"
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


# ═══════════════════════════════════════════════════════════════
# DOWNLOAD
# ═══════════════════════════════════════════════════════════════
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
    except Exception as e:
        return False, str(e)[:200]


# ═══════════════════════════════════════════════════════════════
# UPDATE ANWENDEN — Fix für Update-Loop!
# ═══════════════════════════════════════════════════════════════
def apply_update(new_exe_path: str) -> tuple:
    """
    Ersetzt die aktuelle .exe.
    Fix: Killt ALLE laufenden Instanzen + wartet bis Datei frei ist.
    """
    try:
        if getattr(sys, "frozen", False):
            current_exe = Path(sys.executable).resolve()
            current_pid = os.getpid()
        else:
            return False, "Update nur in EXE-Version möglich"

        new_path = Path(new_exe_path).resolve()
        if not new_path.exists():
            return False, f"Update-Datei fehlt: {new_exe_path}"

        # ═══════════════════════════════════════════════════════
        # PowerShell-Skript: killt alte EXE + wartet + ersetzt + startet
        # ═══════════════════════════════════════════════════════
        ps_script = f"""
$ErrorActionPreference = 'SilentlyContinue'
$currentExe = '{current_exe}'
$newExe = '{new_path}'
$currentPid = {current_pid}
$backupExe = "$currentExe.old"

Write-Host ""
Write-Host "================================================"
Write-Host "  Cleaner Pro - Update wird installiert..."
Write-Host "================================================"
Write-Host ""

# ═══ SCHRITT 1: Killt ALLE laufenden Instanzen der aktuellen EXE ═══
Write-Host "[1/6] Beende laufende Cleaner Pro Instanzen..."

# Aktuellen Prozess ausschliessen (der beendet sich selbst)
Get-Process | Where-Object {{
    $_.Path -eq $currentExe -and $_.Id -ne $currentPid
}} | Stop-Process -Force

# Warte bis alle Prozesse weg sind
$waitCount = 0
while ($waitCount -lt 30) {{
    $still = Get-Process | Where-Object {{
        $_.Path -eq $currentExe -and $_.Id -ne $currentPid
    }}
    if (-not $still) {{ break }}
    Start-Sleep -Milliseconds 500
    $waitCount++
}}

# Auch python-Prozesse aus dem gleichen Ordner killen
Get-Process python* | Where-Object {{
    $_.Path -like "*SystemCleanerPro*"
}} | Stop-Process -Force

Write-Host "      OK"
Start-Sleep -Seconds 2

# ═══ SCHRITT 2: Prüfe ob neue EXE existiert ═══
Write-Host "[2/6] Prüfe Update-Datei..."
if (-not (Test-Path $newExe)) {{
    Write-Host "      FEHLER: $newExe fehlt!"
    Read-Host "Enter zum Beenden"
    exit 1
}}
Write-Host "      OK"

# ═══ SCHRITT 3: Alte EXE umbenennen (nicht löschen) ═══
Write-Host "[3/6] Benenne alte Version um..."
if (Test-Path $backupExe) {{
    Remove-Item $backupExe -Force
}}

try {{
    Move-Item -Path $currentExe -Destination $backupExe -Force
    Write-Host "      OK -> $backupExe"
}} catch {{
    Write-Host "      FEHLER: Alte EXE konnte nicht umbenannt werden!"
    Write-Host "      Bitte Cleaner Pro manuell schliessen."
    Read-Host "Enter zum Beenden"
    exit 1
}}

# ═══ SCHRITT 4: Neue EXE kopieren ═══
Write-Host "[4/6] Kopiere neue Version..."
try {{
    Copy-Item -Path $newExe -Destination $currentExe -Force
    Write-Host "      OK"
}} catch {{
    Write-Host "      FEHLER beim Kopieren!"
    # Rollback
    Move-Item -Path $backupExe -Destination $currentExe -Force
    Read-Host "Enter zum Beenden"
    exit 1
}}

# Prüfe ob Kopie erfolgreich
if (-not (Test-Path $currentExe)) {{
    Write-Host "      FEHLER: Kopie nicht angekommen!"
    Move-Item -Path $backupExe -Destination $currentExe -Force
    Read-Host "Enter zum Beenden"
    exit 1
}}

# ═══ SCHRITT 5: Starte neue Version ═══
Write-Host "[5/6] Starte neue Version..."
Start-Sleep -Seconds 1
Start-Process -FilePath $currentExe
Write-Host "      OK"

# ═══ SCHRITT 6: Aufräumen ═══
Write-Host "[6/6] Aufräumen..."
Start-Sleep -Seconds 3
Remove-Item $backupExe -Force
Remove-Item $newExe -Force
Remove-Item $MyInvocation.MyCommand.Path -Force

Write-Host ""
Write-Host "================================================"
Write-Host "  UPDATE FERTIG!"
Write-Host "================================================"
Write-Host ""

# Fenster schliessen
Start-Sleep -Seconds 2
exit 0
"""

        # Skript speichern
        script_path = Path(tempfile.gettempdir()) / "cleaner_update.ps1"
        script_path.write_text(ps_script, encoding="utf-8-sig")

        # PowerShell starten (neues Fenster, damit User es sieht)
        subprocess.Popen(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", str(script_path)
            ],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        return True, (
            "Update wird installiert...\n\n"
            "Ein Fenster öffnet sich und zeigt den Fortschritt.\n"
            "Die App wird jetzt beendet."
        )

    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
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