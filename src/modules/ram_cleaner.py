"""RAM-Cleaner — sicher via Sub-Prozess."""
import ctypes
import gc
import os
import subprocess
import sys
import json
from ctypes import wintypes


PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_SET_QUOTA = 0x0100


# Prozesse die NIEMALS angefasst werden
PROTECTED_NAMES = {
    "system", "system idle process", "registry", "memory compression",
    "csrss.exe", "wininit.exe", "winlogon.exe", "services.exe",
    "lsass.exe", "smss.exe", "svchost.exe", "dwm.exe",
    "audiodg.exe", "fontdrvhost.exe", "wlanext.exe",
    "securityhealthservice.exe", "msmpeng.exe", "nissrv.exe",
    "searchindexer.exe", "spoolsv.exe", "taskhostw.exe",
    "runtimebroker.exe", "shellexperiencehost.exe",
    "startmenuexperiencehost.exe", "searchhost.exe",
    "textinputhost.exe", "applicationframehost.exe",
}


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def get_memory_status() -> dict:
    try:
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return {}
        return {
            "percent": stat.dwMemoryLoad,
            "total_gb": stat.ullTotalPhys / (1024**3),
            "avail_gb": stat.ullAvailPhys / (1024**3),
            "used_gb": (stat.ullTotalPhys - stat.ullAvailPhys) / (1024**3),
            "pagefile_total_gb": stat.ullTotalPageFile / (1024**3),
            "pagefile_avail_gb": stat.ullAvailPageFile / (1024**3),
        }
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════
# Diese Funktion läuft im SUB-PROZESS (isoliert)
# ═══════════════════════════════════════════════════════════════
def _worker_run() -> dict:
    """Läuft im Sub-Prozess. Wenn dieser crasht, merkt das der Parent."""
    try:
        import psutil
    except ImportError:
        return {"success": False, "error": "psutil fehlt"}

    before = get_memory_status()
    if not before:
        return {"success": False, "error": "RAM-Status nicht lesbar"}

    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    cleared = 0
    skipped = 0
    failed = 0

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            pid = proc.info["pid"]
            name = (proc.info["name"] or "").lower()
            if name in PROTECTED_NAMES or pid == os.getpid():
                skipped += 1
                continue
            try:
                handle = kernel32.OpenProcess(
                    PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA,
                    False, pid
                )
                if handle:
                    try:
                        psapi.EmptyWorkingSet(handle)
                        cleared += 1
                    except Exception:
                        failed += 1
                    finally:
                        kernel32.CloseHandle(handle)
                else:
                    failed += 1
            except Exception:
                failed += 1
        except Exception:
            continue

    try:
        gc.collect()
    except Exception:
        pass

    after = get_memory_status()
    return {
        "success": True,
        "processes_cleared": cleared,
        "processes_skipped": skipped,
        "processes_failed": failed,
        "freed_gb": max(0, after.get("avail_gb", 0) - before.get("avail_gb", 0)),
    }


# ═══════════════════════════════════════════════════════════════
# Public API — läuft im HAUPT-Prozess
# ═══════════════════════════════════════════════════════════════
def empty_working_sets() -> dict:
    """
    Führt den Cleaner in einem Sub-Prozess aus.
    Wenn der Sub-Prozess crasht → App läuft weiter.
    """
    # Wenn wir im Worker-Prozess sind → direkt ausführen
    if os.environ.get("RAM_CLEANER_WORKER") == "1":
        return _worker_run()

    # Sonst: Sub-Prozess starten
    script_path = os.path.abspath(__file__)
    env = os.environ.copy()
    env["RAM_CLEANER_WORKER"] = "1"

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Worker hat JSON in stdout geprintet
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        # Kein JSON → Crash im Worker
        return {
            "success": False,
            "error": "Cleaner-Prozess abgestürzt (Windows-API-Fehler)",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Cleaner dauerte zu lange (>30s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Wenn diese Datei direkt ausgeführt wird → Worker-Modus
if __name__ == "__main__":
    result = _worker_run()
    print(json.dumps(result))