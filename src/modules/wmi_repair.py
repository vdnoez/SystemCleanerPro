"""WMI-Reparatur — mit Encoding-Fix."""
import subprocess
import ctypes
import time
from pathlib import Path


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def _run(args: list, timeout: int = 60) -> tuple:
    """Führt Befehl aus mit Encoding-Fix."""
    try:
        r = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return False, str(e)


def verify_repository() -> tuple:
    ok, output = _run(["winmgmt", "/verifyrepository"], timeout=60)
    return ok, output.strip()


def restore_repository() -> tuple:
    if not is_admin():
        return False, "Admin-Rechte erforderlich"
    ok, output = _run(["winmgmt", "/restore"], timeout=180)
    return ok, output.strip()


def full_repair_no_restart() -> tuple:
    if not is_admin():
        return False, "Admin-Rechte erforderlich"

    log = []

    log.append("[1/7] Backup erstellen...")
    _run(["winmgmt", "/backup"], timeout=120)
    log.append("      ✅ Backup OK")

    log.append("[2/7] Repository prüfen...")
    _run(["winmgmt", "/verifyrepository"], timeout=60)
    log.append("      ✅ Verify OK")

    log.append("[3/7] Repository reparieren (1/2)...")
    _run(["winmgmt", "/salvagerepository"], timeout=180)
    log.append("      ✅ Reparatur 1 OK")

    log.append("[4/7] Repository reparieren (2/2)...")
    _run(["winmgmt", "/salvagerepository"], timeout=180)
    log.append("      ✅ Reparatur 2 OK")

    log.append("[5/7] VPN-Klassen registrieren...")
    mof_dir = Path(r"C:\Windows\System32\wbem")
    mof_files = ["VpnClient.mof", "NetAdapterCim.mof",
                 "netmgmt.mof", "NetTCPIP.mof", "netcenter.mof"]
    imported = 0
    for mof in mof_files:
        path = mof_dir / mof
        if path.exists():
            ok, _ = _run(["mofcomp.exe", str(path)], timeout=60)
            if ok:
                imported += 1
    log.append(f"      ✅ {imported} MOF-Dateien registriert")

    log.append("[6/7] WMI-Dienst neu starten...")
    _run(["net", "stop", "winmgmt", "/y"], timeout=90)
    time.sleep(2)
    _run(["net", "start", "winmgmt"], timeout=90)
    time.sleep(3)
    log.append("      ✅ Dienst neu gestartet")

    log.append("[7/7] Warte bis WMI bereit ist...")
    ready = False
    for i in range(15):
        ok, out = _run(["sc", "query", "winmgmt"], timeout=10)
        if "RUNNING" in out:
            ready = True
            break
        time.sleep(2)

    if ready:
        log.append("      ✅ WMI läuft")
    else:
        log.append("      ⚠️  WMI antwortet nicht")

    log.append("")
    log.append("=" * 50)
    log.append("FERTIG — OHNE Neustart!")
    log.append("=" * 50)

    return True, "\n".join(log)


def create_repair_batch() -> str:
    from src.core.config import DATA_DIR
    batch_path = DATA_DIR / "wmi_repair.bat"
    content = r"""@echo off
chcp 65001 >nul
title WMI Reparatur
color 0E

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo FEHLER: Keine Admin-Rechte!
    pause
    exit /b 1
)

echo [1/7] Backup...
winmgmt /backup
echo [2/7] Verify...
winmgmt /verifyrepository
echo [3/7] Reparatur 1/2...
winmgmt /salvagerepository
echo [4/7] Reparatur 2/2...
winmgmt /salvagerepository
echo [5/7] MOF...
mofcomp.exe C:\Windows\System32\wbem\VpnClient.mof >nul 2>&1
mofcomp.exe C:\Windows\System32\wbem\NetAdapterCim.mof >nul 2>&1
mofcomp.exe C:\Windows\System32\wbem\netmgmt.mof >nul 2>&1
mofcomp.exe C:\Windows\System32\wbem\NetTCPIP.mof >nul 2>&1
mofcomp.exe C:\Windows\System32\wbem\netcenter.mof >nul 2>&1
echo [6/7] Dienst...
net stop winmgmt /y >nul 2>&1
timeout /t 3 /nobreak >nul
net start winmgmt
timeout /t 3 /nobreak >nul
echo [7/7] Final...
winmgmt /verifyrepository
echo.
echo FERTIG!
timeout /t 5 /nobreak >nul
"""
    batch_path.write_text(content, encoding="utf-8")
    return str(batch_path)


def run_repair_batch_as_admin() -> tuple:
    try:
        batch_path = create_repair_batch()
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", "cmd.exe",
            f'/c "{batch_path}"',
            None, 1
        )
        if ret <= 32:
            return False, "UAC abgelehnt"
        return True, "Reparatur gestartet"
    except Exception as e:
        return False, str(e)