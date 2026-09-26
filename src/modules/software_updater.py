"""Software-Updater via winget."""
import subprocess
import json
import re
from typing import Callable


def is_winget_available() -> bool:
    """Prüft ob winget installiert ist."""
    try:
        r = subprocess.run(
            ["winget", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return r.returncode == 0
    except Exception:
        return False


def _run_winget(args: list, timeout: int = 60) -> tuple:
    """Führt winget-Befehl aus. Returns (success, stdout, stderr)."""
    try:
        r = subprocess.run(
            ["winget"] + args,
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace"
        )
        return r.returncode == 0, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def list_installed() -> list:
    """Listet alle installierten Programme."""
    success, out, err = _run_winget(["list", "--accept-source-agreements"])
    if not success:
        return []

    programs = []
    lines = out.split("\n")
    # Überspringe Header (erste 2-3 Zeilen)
    in_list = False
    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith("---") or line.startswith("Name"):
            header_end = i + 1
            in_list = True
            break

    if not in_list:
        return []

    for line in lines[header_end:]:
        line = line.rstrip()
        if not line or line.startswith("-"):
            continue

        # Spalten sind normalerweise: Name, Id, Version, Available, Source
        # Wir splitten an 2+ Leerzeichen
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) >= 3:
            programs.append({
                "name": parts[0].strip(),
                "id": parts[1].strip() if len(parts) > 1 else "",
                "version": parts[2].strip() if len(parts) > 2 else "",
                "available": parts[3].strip() if len(parts) > 3 else "",
            })

    return programs


def list_upgradable() -> list:
    """Listet Programme mit verfügbaren Updates."""
    success, out, err = _run_winget([
        "upgrade", "--include-unknown",
        "--accept-source-agreements"
    ])
    if not success:
        return []

    programs = []
    lines = out.split("\n")
    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith("---"):
            header_end = i + 1
            break

    for line in lines[header_end:]:
        line = line.rstrip()
        if not line or line.startswith("-"):
            continue
        if "upgrades available" in line.lower():
            continue
        if "package(s)" in line.lower():
            continue

        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) >= 4:
            programs.append({
                "name": parts[0].strip(),
                "id": parts[1].strip(),
                "current": parts[2].strip(),
                "available": parts[3].strip(),
            })

    return programs


def upgrade_package(package_id: str,
                    progress_cb: Callable = None) -> tuple:
    """Führt Update für ein Paket aus."""
    if progress_cb:
        progress_cb(f"Update: {package_id}")

    success, out, err = _run_winget([
        "upgrade", "--id", package_id, "--silent",
        "--accept-package-agreements",
        "--accept-source-agreements",
        "--disable-interactivity"
    ], timeout=600)

    if success:
        return True, f"✅ {package_id} aktualisiert"
    return False, f"❌ {package_id}: {err or out[:200]}"


def upgrade_all(progress_cb: Callable = None) -> tuple:
    """Führt alle Updates aus."""
    if progress_cb:
        progress_cb("Aktualisiere alle Pakete...")

    success, out, err = _run_winget([
        "upgrade", "--all", "--include-unknown", "--silent",
        "--accept-package-agreements",
        "--accept-source-agreements",
        "--disable-interactivity"
    ], timeout=3600)

    if success:
        return True, "✅ Alle Updates installiert"
    return False, f"❌ Fehler: {err or out[:500]}"


def uninstall_package(package_id: str,
                      progress_cb: Callable = None) -> tuple:
    """Deinstalliert ein Paket."""
    if progress_cb:
        progress_cb(f"Deinstalliere: {package_id}")

    success, out, err = _run_winget([
        "uninstall", "--id", package_id, "--silent",
        "--disable-interactivity"
    ], timeout=300)

    if success:
        return True, f"✅ {package_id} deinstalliert"
    return False, f"❌ {package_id}: {err or out[:200]}"


def search_package(query: str) -> list:
    """Sucht Pakete in winget-Repo."""
    success, out, err = _run_winget([
        "search", query, "--accept-source-agreements"
    ], timeout=30)
    if not success:
        return []

    results = []
    lines = out.split("\n")
    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith("---"):
            header_end = i + 1
            break

    for line in lines[header_end:]:
        line = line.rstrip()
        if not line or line.startswith("-"):
            continue
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) >= 2:
            results.append({
                "name": parts[0].strip(),
                "id": parts[1].strip(),
                "version": parts[2].strip() if len(parts) > 2 else "",
            })
    return results[:50]