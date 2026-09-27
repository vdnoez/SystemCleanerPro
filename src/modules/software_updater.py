"""Software-Updater via winget — mit Encoding-Fix."""
import subprocess
import json
import re
import os
from typing import Callable


def _run_winget(args: list, timeout: int = 60) -> tuple:
    """
    Führt winget-Befehl aus.
    Nutzt 'errors=replace' um Encoding-Fehler zu vermeiden.
    """
    try:
        r = subprocess.run(
            ["winget"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",  # ⭐ Fix für Encoding-Fehler
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        return r.returncode == 0, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except FileNotFoundError:
        return False, "", "winget nicht gefunden"
    except Exception as e:
        return False, "", str(e)


def is_winget_available() -> bool:
    try:
        r = subprocess.run(
            ["winget", "--version"],
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        return r.returncode == 0
    except Exception:
        return False


def list_installed() -> list:
    success, out, err = _run_winget(["list", "--accept-source-agreements"])
    if not success:
        return []

    programs = []
    lines = out.split("\n")
    header_end = 0
    in_list = False

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
    return False, f"❌ {package_id}: {(err or out)[:200]}"


def upgrade_all(progress_cb: Callable = None) -> tuple:
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
    return False, f"❌ Fehler: {(err or out)[:500]}"


def uninstall_package(package_id: str,
                      progress_cb: Callable = None) -> tuple:
    if progress_cb:
        progress_cb(f"Deinstalliere: {package_id}")

    success, out, err = _run_winget([
        "uninstall", "--id", package_id, "--silent",
        "--disable-interactivity"
    ], timeout=300)

    if success:
        return True, f"✅ {package_id} deinstalliert"
    return False, f"❌ {package_id}: {(err or out)[:200]}"


def search_package(query: str) -> list:
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