"""System-Informationen sammeln (CPU, RAM, GPU, Disk, OS)."""
import os
import platform
import subprocess
import re
from datetime import datetime


def _run_ps(cmd: str, timeout: int = 20) -> str:
    """PowerShell ausführen (64-Bit)."""
    try:
        ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        if not os.path.exists(ps_path):
            ps_path = "powershell.exe"
        r = subprocess.run(
            [ps_path, "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        return r.stdout.strip()
    except Exception:
        return ""


def _run_cmd(args: list, timeout: int = 15) -> str:
    """Cmd ausführen."""
    try:
        r = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        return r.stdout.strip()
    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════════
# CPU
# ═══════════════════════════════════════════════════════════════
def get_cpu_info() -> dict:
    try:
        import psutil
        name = platform.processor() or "Unbekannt"

        # Besserer Name via PowerShell
        out = _run_ps(
            "(Get-CimInstance Win32_Processor | "
            "Select-Object -First 1 -ExpandProperty Name)"
        )
        if out:
            name = out.strip()

        cores_physical = psutil.cpu_count(logical=False) or 0
        cores_logical = psutil.cpu_count(logical=True) or 0
        freq = psutil.cpu_freq()
        freq_current = f"{freq.current:.0f} MHz" if freq else "?"
        freq_max = f"{freq.max:.0f} MHz" if freq and freq.max else "?"

        # Architektur
        arch = platform.machine()

        return {
            "name": name,
            "cores_physical": cores_physical,
            "cores_logical": cores_logical,
            "freq_current": freq_current,
            "freq_max": freq_max,
            "arch": arch,
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# RAM
# ═══════════════════════════════════════════════════════════════
def get_ram_info() -> dict:
    try:
        import psutil
        vm = psutil.virtual_memory()
        total_gb = vm.total / (1024 ** 3)

        # RAM-Typ & Speed via PowerShell
        out = _run_ps(
            "(Get-CimInstance Win32_PhysicalMemory | "
            "Select-Object -First 1 -Property Speed,MemoryType,Manufacturer | "
            "ConvertTo-Json -Compress)"
        )

        speed = "?"
        ram_type = "?"
        if out:
            try:
                import json
                data = json.loads(out)
                if isinstance(data, list):
                    data = data[0]
                speed_val = data.get("Speed", 0)
                if speed_val:
                    speed = f"{speed_val} MHz"
                type_id = data.get("MemoryType", 0)
                type_map = {
                    20: "DDR", 21: "DDR2", 22: "DDR2 FB-DIMM",
                    24: "DDR3", 26: "DDR4", 34: "DDR5",
                }
                ram_type = type_map.get(type_id, "DDR")
            except Exception:
                pass

        # Slots
        out2 = _run_ps(
            "(Get-CimInstance Win32_PhysicalMemory | Measure-Object).Count"
        )
        slots_used = int(out2) if out2.strip().isdigit() else 0

        out3 = _run_ps(
            "(Get-CimInstance Win32_PhysicalMemoryArray | "
            "Select-Object -First 1 -ExpandProperty MemoryDevices)"
        )
        slots_total = int(out3) if out3.strip().isdigit() else 0

        return {
            "total_gb": round(total_gb, 1),
            "available_gb": round(vm.available / (1024 ** 3), 1),
            "percent": vm.percent,
            "speed": speed,
            "type": ram_type,
            "slots_used": slots_used,
            "slots_total": slots_total,
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# GPU
# ═══════════════════════════════════════════════════════════════
def get_gpu_info() -> list:
    try:
        out = _run_ps(
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name,AdapterRAM,DriverVersion,DriverDate | "
            "ConvertTo-Json -Compress"
        )
        if not out:
            return []

        import json
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]

        results = []
        for gpu in data:
            vram_bytes = gpu.get("AdapterRAM", 0) or 0
            vram_gb = vram_bytes / (1024 ** 3) if vram_bytes else 0

            driver_date = gpu.get("DriverDate", "")
            date_str = "?"
            if driver_date and len(str(driver_date)) >= 8:
                try:
                    ds = str(driver_date)[:8]
                    date_str = f"{ds[6:8]}.{ds[4:6]}.{ds[:4]}"
                except Exception:
                    pass

            results.append({
                "name": gpu.get("Name", "?"),
                "vram_gb": round(vram_gb, 1),
                "driver": gpu.get("DriverVersion", "?"),
                "driver_date": date_str,
            })

        return results
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════
# DISKS
# ═══════════════════════════════════════════════════════════════
def get_disk_info() -> list:
    try:
        import psutil
        results = []
        for part in psutil.disk_partitions(all=False):
            if "cdrom" in part.opts or part.fstype == "":
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                results.append({
                    "device": part.device.rstrip("\\"),
                    "mount": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 1),
                    "used_gb": round(usage.used / (1024 ** 3), 1),
                    "free_gb": round(usage.free / (1024 ** 3), 1),
                    "percent": usage.percent,
                })
            except (PermissionError, OSError):
                continue
        return results
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════
# OS
# ═══════════════════════════════════════════════════════════════
def get_os_info() -> dict:
    try:
        name = platform.system()
        release = platform.release()
        version = platform.version()

        # Build-Nummer
        build = version.split(".")[-1] if "." in version else "?"

        # Windows-Edition
        out = _run_ps(
            "(Get-CimInstance Win32_OperatingSystem | "
            "Select-Object Caption,Version,BuildNumber,OSArchitecture | "
            "ConvertTo-Json -Compress)"
        )

        caption = f"{name} {release}"
        arch = platform.machine()
        version_str = version

        if out:
            try:
                import json
                data = json.loads(out)
                caption = data.get("Caption", caption)
                version_str = data.get("Version", version_str)
                build = data.get("BuildNumber", build)
                arch = data.get("OSArchitecture", arch)
            except Exception:
                pass

        # Aktivierungs-Status
        out2 = _run_ps(
            "(Get-CimInstance SoftwareLicensingProduct | "
            "Where-Object {$_.PartialProductKey -and "
            "$_.Name -like '*Windows*'} | "
            "Select-Object -First 1 -ExpandProperty LicenseStatus)"
        )
        activated = out2.strip() == "1"

        # Hostname
        hostname = platform.node()

        return {
            "name": caption,
            "version": version_str,
            "build": build,
            "arch": arch,
            "activated": activated,
            "hostname": hostname,
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# MAINBOARD
# ═══════════════════════════════════════════════════════════════
def get_motherboard_info() -> dict:
    try:
        out = _run_ps(
            "(Get-CimInstance Win32_BaseBoard | "
            "Select-Object Manufacturer,Product | ConvertTo-Json -Compress)"
        )
        out2 = _run_ps(
            "(Get-CimInstance Win32_BIOS | "
            "Select-Object Manufacturer,SMBIOSBIOSVersion,ReleaseDate | "
            "ConvertTo-Json -Compress)"
        )

        board = {}
        bios = {}

        import json
        if out:
            try:
                data = json.loads(out)
                board = {
                    "manufacturer": data.get("Manufacturer", "?"),
                    "product": data.get("Product", "?"),
                }
            except Exception:
                pass

        if out2:
            try:
                data = json.loads(out2)
                date_str = "?"
                release = str(data.get("ReleaseDate", ""))
                if len(release) >= 8:
                    date_str = f"{release[6:8]}.{release[4:6]}.{release[:4]}"
                bios = {
                    "manufacturer": data.get("Manufacturer", "?"),
                    "version": data.get("SMBIOSBIOSVersion", "?"),
                    "date": date_str,
                }
            except Exception:
                pass

        return {"board": board, "bios": bios}
    except Exception:
        return {"board": {}, "bios": {}}


# ═══════════════════════════════════════════════════════════════
# ALLES
# ═══════════════════════════════════════════════════════════════
def get_all_info() -> dict:
    """Sammelt alle Infos."""
    return {
        "cpu": get_cpu_info(),
        "ram": get_ram_info(),
        "gpu": get_gpu_info(),
        "disks": get_disk_info(),
        "os": get_os_info(),
        "board": get_motherboard_info(),
    }