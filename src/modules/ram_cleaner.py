"""RAM-Cleaner — crashsicher, mit Encoding-Fix."""
import ctypes
import gc
import os
import sys
import json
import subprocess
import tempfile
from ctypes import wintypes
from pathlib import Path


PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_SET_QUOTA = 0x0100


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


def _worker_run() -> dict:
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


def _get_worker_command() -> list:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--ram-cleaner-helper"]
    else:
        script_path = os.path.abspath(__file__)
        return [sys.executable, script_path]


def empty_working_sets() -> dict:
    if os.environ.get("RAM_CLEANER_WORKER") == "1":
        return _worker_run()
    if "--ram-cleaner-helper" in sys.argv:
        return _worker_run()

    cmd = _get_worker_command()
    env = os.environ.copy()
    env["RAM_CLEANER_WORKER"] = "1"

    result_file = Path(tempfile.gettempdir()) / "ram_cleaner_result.json"
    try:
        if result_file.exists():
            result_file.unlink()
    except Exception:
        pass

    env["RAM_CLEANER_RESULT_FILE"] = str(result_file)

    try:
        proc = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )

        if result_file.exists():
            try:
                data = json.loads(result_file.read_text(encoding="utf-8"))
                result_file.unlink()
                return data
            except Exception:
                pass

        for line in (proc.stdout or "").splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue

        return {
            "success": False,
            "error": "Cleaner-Prozess abgestürzt",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout (>15s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = _worker_run()
    result_file = os.environ.get("RAM_CLEANER_RESULT_FILE")
    if result_file:
        try:
            Path(result_file).write_text(
                json.dumps(result), encoding="utf-8"
            )
        except Exception:
            pass
    print(json.dumps(result))
    sys.exit(0)