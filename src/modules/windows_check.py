"""Windows-Health-Check — 13 Checks mit Encoding-Fix."""
import os
import platform
import subprocess
from pathlib import Path

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def _run_ps(cmd: str, timeout: int = 20) -> str:
    """PowerShell mit Encoding-Fix."""
    try:
        ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        if not os.path.exists(ps_path):
            ps_path = "powershell.exe"
        r = subprocess.run(
            [ps_path, "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        return (r.stdout or "").strip()
    except Exception:
        return ""


def _fmt_gb(b: float) -> str:
    return f"{b:.1f} GB"


# ═══════════════════════════════════════════════════════════════
def check_windows_version() -> dict:
    try:
        ver = platform.version()
        release = platform.release()
        build = int(ver.split(".")[-1]) if "." in ver else 0

        if "11" in release or build >= 22000:
            edition = "Windows 11"
        elif "10" in release:
            edition = "Windows 10"
        else:
            edition = release

        is_current = build >= 22000 if "11" in edition else build >= 19045

        if is_current:
            return {"id": "win_version", "status": "ok",
                    "name": "Windows-Version",
                    "detail": f"{edition}  ·  Build {build}", "fix": None}
        return {"id": "win_version", "status": "warn",
                "name": "Windows-Version",
                "detail": f"{edition}  ·  Build {build} (veraltet?)",
                "fix": None}
    except Exception as e:
        return {"id": "win_version", "status": "error",
                "name": "Windows-Version",
                "detail": f"Fehler: {e}", "fix": None}


def check_windows_update() -> dict:
    try:
        out = _run_ps(
            "(New-Object -ComObject Microsoft.Update.AutoUpdate)."
            "Results.LastSearchSuccessDate"
        )
        if not out or "null" in out.lower():
            return {"id": "win_update", "status": "warn",
                    "name": "Windows Update",
                    "detail": "Kein Update-Verlauf gefunden", "fix": None}

        from datetime import datetime
        days_ago = None
        for fmt in ("%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
                    "%d.%m.%Y %H:%M:%S"):
            try:
                dt = datetime.strptime(out[:19], fmt)
                days_ago = (datetime.now() - dt).days
                break
            except ValueError:
                continue

        if days_ago is None:
            return {"id": "win_update", "status": "ok",
                    "name": "Windows Update",
                    "detail": f"Letzte Suche: {out[:19]}", "fix": None}

        if days_ago <= 7:
            return {"id": "win_update", "status": "ok",
                    "name": "Windows Update",
                    "detail": f"Letzte Suche vor {days_ago} Tagen",
                    "fix": None}
        return {"id": "win_update", "status": "warn",
                "name": "Windows Update",
                "detail": f"Letzte Suche vor {days_ago} Tagen — prüfen!",
                "fix": {"action": "open_url",
                        "value": "ms-settings:windowsupdate"}}
    except Exception as e:
        return {"id": "win_update", "status": "error",
                "name": "Windows Update",
                "detail": f"Fehler: {e}", "fix": None}


def check_disk_space() -> dict:
    try:
        if not HAS_PSUTIL:
            return {"id": "disk", "status": "error",
                    "name": "Festplattenplatz",
                    "detail": "psutil fehlt", "fix": None}

        du = psutil.disk_usage("C:/")
        free_gb = du.free / (1024 ** 3)
        free_pct = 100 - du.percent

        if free_pct >= 20:
            status = "ok"
        elif free_pct >= 10:
            status = "warn"
        else:
            status = "error"

        return {"id": "disk", "status": status,
                "name": "Festplattenplatz (C:)",
                "detail": f"{_fmt_gb(free_gb)} frei ({free_pct:.1f}%)",
                "fix": None}
    except Exception as e:
        return {"id": "disk", "status": "error",
                "name": "Festplattenplatz",
                "detail": f"Fehler: {e}", "fix": None}


def check_defender() -> dict:
    try:
        out = _run_ps(
            "Get-MpComputerStatus | "
            "Select-Object AntivirusEnabled,RealTimeProtectionEnabled,"
            "AntivirusSignatureLastUpdated | ConvertTo-Json -Compress"
        )
        if not out:
            return {"id": "defender", "status": "warn",
                    "name": "Windows Defender",
                    "detail": "Status nicht abrufbar (Admin nötig)",
                    "fix": None}

        import json
        data = json.loads(out)
        av_on = data.get("AntivirusEnabled", False)
        rt_on = data.get("RealTimeProtectionEnabled", False)
        sig_update = data.get("AntivirusSignatureLastUpdated", "")

        if av_on and rt_on:
            detail = "✅ Aktiv mit Echtzeitschutz"
            if sig_update:
                detail += f"  ·  Signaturen: {sig_update[:10]}"
            return {"id": "defender", "status": "ok",
                    "name": "Windows Defender",
                    "detail": detail, "fix": None}

        problems = []
        if not av_on:
            problems.append("Virenschutz AUS")
        if not rt_on:
            problems.append("Echtzeitschutz AUS")

        return {"id": "defender", "status": "error",
                "name": "Windows Defender",
                "detail": "⚠️  " + ", ".join(problems),
                "fix": {"action": "open_url",
                        "value": "windowsdefender://threat"}}
    except Exception as e:
        return {"id": "defender", "status": "warn",
                "name": "Windows Defender",
                "detail": f"Fehler: {e}", "fix": None}


def check_firewall() -> dict:
    try:
        out = _run_ps(
            "Get-NetFirewallProfile | "
            "Select-Object Name,Enabled | ConvertTo-Json -Compress"
        )
        if not out:
            return {"id": "firewall", "status": "warn",
                    "name": "Firewall",
                    "detail": "Status nicht abrufbar", "fix": None}

        import json
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]

        enabled = [p for p in data if p.get("Enabled")]
        total = len(data)

        if len(enabled) == total and total > 0:
            return {"id": "firewall", "status": "ok",
                    "name": "Firewall",
                    "detail": f"✅ Aktiv für alle {total} Profile",
                    "fix": None}
        return {"id": "firewall", "status": "error",
                "name": "Firewall",
                "detail": f"⚠️  Nur {len(enabled)}/{total} Profile aktiv",
                "fix": {"action": "open_url",
                        "value": "ms-settings:windowsdefender"}}
    except Exception as e:
        return {"id": "firewall", "status": "warn",
                "name": "Firewall",
                "detail": f"Fehler: {e}", "fix": None}


def check_dotnet() -> dict:
    try:
        out = _run_ps(
            "Get-ChildItem 'HKLM:\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP' "
            "-ErrorAction SilentlyContinue | "
            "Select-Object -ExpandProperty PSChildName"
        )
        if out:
            versions = [v for v in out.split("\n") if v.strip()]
            return {"id": "dotnet", "status": "ok",
                    "name": ".NET Framework",
                    "detail": f"✅ {len(versions)} Versionen installiert "
                              f"({', '.join(versions[-3:])})",
                    "fix": None}
        return {"id": "dotnet", "status": "warn",
                "name": ".NET Framework",
                "detail": "Keine Version gefunden", "fix": None}
    except Exception as e:
        return {"id": "dotnet", "status": "warn",
                "name": ".NET Framework",
                "detail": f"Fehler: {e}", "fix": None}


def check_vcredist() -> dict:
    try:
        out = _run_ps(
            "Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\"
            "CurrentVersion\\Uninstall\\*' -ErrorAction SilentlyContinue | "
            "Where-Object { $_.DisplayName -like '*Visual C++*' } | "
            "Measure-Object | Select-Object -ExpandProperty Count"
        )
        count = int(out) if out.strip().isdigit() else 0

        if count >= 5:
            return {"id": "vcredist", "status": "ok",
                    "name": "Visual C++ Redistributables",
                    "detail": f"✅ {count} Versionen installiert",
                    "fix": None}
        if count >= 2:
            return {"id": "vcredist", "status": "warn",
                    "name": "Visual C++ Redistributables",
                    "detail": f"Nur {count} Versionen (empfohlen: 5+)",
                    "fix": None}
        return {"id": "vcredist", "status": "error",
                "name": "Visual C++ Redistributables",
                "detail": f"Nur {count} Version(en) — viele fehlen",
                "fix": None}
    except Exception as e:
        return {"id": "vcredist", "status": "warn",
                "name": "Visual C++ Redistributables",
                "detail": f"Fehler: {e}", "fix": None}


def check_driver_problems() -> dict:
    try:
        out = _run_ps(
            "Get-WmiObject Win32_PnPEntity | "
            "Where-Object { $_.ConfigManagerErrorCode -ne 0 } | "
            "Measure-Object | Select-Object -ExpandProperty Count"
        )
        count = int(out) if out.strip().isdigit() else 0

        if count == 0:
            return {"id": "drivers", "status": "ok",
                    "name": "Treiber-Probleme",
                    "detail": "✅ Keine Probleme erkannt", "fix": None}
        return {"id": "drivers", "status": "error",
                "name": "Treiber-Probleme",
                "detail": f"⚠️  {count} Geräte mit Problemen",
                "fix": {"action": "open_url", "value": "devmgmt.msc"}}
    except Exception as e:
        return {"id": "drivers", "status": "warn",
                "name": "Treiber-Probleme",
                "detail": f"Fehler: {e}", "fix": None}


def check_temp_size() -> dict:
    try:
        import tempfile
        td = Path(tempfile.gettempdir())
        total = 0
        try:
            for f in td.rglob("*"):
                try:
                    if f.is_file():
                        total += f.stat().st_size
                except OSError:
                    continue
        except Exception:
            pass

        gb = total / (1024 ** 3)

        if gb < 2:
            status = "ok"
        elif gb < 5:
            status = "warn"
        else:
            status = "error"

        return {"id": "temp", "status": status,
                "name": "Temp-Ordner",
                "detail": f"{_fmt_gb(gb)} in {td}",
                "fix": {"action": "open_folder", "value": str(td)}}
    except Exception as e:
        return {"id": "temp", "status": "warn",
                "name": "Temp-Ordner",
                "detail": f"Fehler: {e}", "fix": None}


def check_autostart_count() -> dict:
    try:
        count = 0
        if HAS_WINREG:
            for hive, path in [
                (winreg.HKEY_CURRENT_USER,
                 r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE,
                 r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ]:
                try:
                    with winreg.OpenKey(hive, path) as key:
                        i = 0
                        while True:
                            try:
                                winreg.EnumValue(key, i)
                                count += 1
                                i += 1
                            except OSError:
                                break
                except FileNotFoundError:
                    continue

        if count <= 10:
            status = "ok"
        elif count <= 20:
            status = "warn"
        else:
            status = "error"

        return {"id": "autostart", "status": status,
                "name": "Autostart-Programme",
                "detail": f"{count} Programme starten beim Boot",
                "fix": None}
    except Exception as e:
        return {"id": "autostart", "status": "warn",
                "name": "Autostart-Programme",
                "detail": f"Fehler: {e}", "fix": None}


def check_smart_status() -> dict:
    try:
        out = _run_ps(
            "Get-PhysicalDisk | "
            "Select-Object FriendlyName,HealthStatus,OperationalStatus | "
            "ConvertTo-Json -Compress",
            timeout=20
        )
        if not out:
            return {"id": "smart", "status": "warn",
                    "name": "Disk-Gesundheit (SMART)",
                    "detail": "Status nicht abrufbar", "fix": None}

        import json
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]

        problems = []
        for d in data:
            health = d.get("HealthStatus", "")
            op = d.get("OperationalStatus", "")
            name = d.get("FriendlyName", "?")[:20]
            if health != "Healthy" or op != "OK":
                problems.append(f"{name}: {health}/{op}")

        if not problems:
            return {"id": "smart", "status": "ok",
                    "name": "Disk-Gesundheit (SMART)",
                    "detail": f"✅ {len(data)} Disks gesund", "fix": None}
        return {"id": "smart", "status": "error",
                "name": "Disk-Gesundheit (SMART)",
                "detail": "⚠️  " + "  ·  ".join(problems[:3]), "fix": None}
    except Exception as e:
        return {"id": "smart", "status": "warn",
                "name": "Disk-Gesundheit (SMART)",
                "detail": f"Fehler: {e}", "fix": None}


def check_bitlocker() -> dict:
    try:
        out = _run_ps(
            "Get-BitLockerVolume -ErrorAction SilentlyContinue | "
            "Where-Object { $_.MountPoint -eq 'C:' } | "
            "Select-Object ProtectionStatus | ConvertTo-Json -Compress"
        )
        if not out or "null" in out.lower():
            return {"id": "bitlocker", "status": "warn",
                    "name": "BitLocker",
                    "detail": "Nicht verfügbar (Home-Edition?)", "fix": None}

        import json
        data = json.loads(out)
        if isinstance(data, dict):
            status = data.get("ProtectionStatus", "")
        else:
            status = data[0].get("ProtectionStatus", "") if data else ""

        if status == "On":
            return {"id": "bitlocker", "status": "ok",
                    "name": "BitLocker (C:)",
                    "detail": "✅ Aktiviert", "fix": None}
        return {"id": "bitlocker", "status": "warn",
                "name": "BitLocker (C:)",
                "detail": "⚠️  Aus — Festplatte nicht verschlüsselt",
                "fix": None}
    except Exception:
        return {"id": "bitlocker", "status": "warn",
                "name": "BitLocker (C:)",
                "detail": "Nicht verfügbar (Home-Edition?)", "fix": None}


def check_dns() -> dict:
    try:
        out = _run_ps(
            "Get-DnsClientServerAddress -AddressFamily IPv4 | "
            "Where-Object {$_.ServerAddresses.Count -gt 0} | "
            "Select-Object -First 1 -ExpandProperty ServerAddresses"
        )
        if not out:
            return {"id": "dns", "status": "warn",
                    "name": "DNS-Server",
                    "detail": "Keine DNS-Server konfiguriert", "fix": None}

        servers = [s.strip() for s in out.split("\n") if s.strip()]
        return {"id": "dns", "status": "ok",
                "name": "DNS-Server",
                "detail": f"✅ {len(servers)} Server: "
                          f"{', '.join(servers[:3])}",
                "fix": None}
    except Exception as e:
        return {"id": "dns", "status": "warn",
                "name": "DNS-Server",
                "detail": f"Fehler: {e}", "fix": None}


# ═══════════════════════════════════════════════════════════════
ALL_CHECKS = [
    check_windows_version,
    check_windows_update,
    check_disk_space,
    check_defender,
    check_firewall,
    check_dotnet,
    check_vcredist,
    check_driver_problems,
    check_temp_size,
    check_autostart_count,
    check_smart_status,
    check_bitlocker,
    check_dns,
]


def run_all_checks(progress_cb=None) -> dict:
    results = []
    total = len(ALL_CHECKS)

    for i, check_fn in enumerate(ALL_CHECKS):
        name = check_fn.__name__.replace("check_", "").replace("_", " ").title()
        if progress_cb:
            progress_cb(f"Prüfe {name}... ({i+1}/{total})")
        try:
            r = check_fn()
        except Exception as e:
            r = {"id": check_fn.__name__, "status": "error",
                 "name": name, "detail": f"Fehler: {e}", "fix": None}
        results.append(r)

    weights = {"ok": 100, "warn": 50, "error": 0}
    if results:
        score = int(sum(weights.get(r["status"], 0) for r in results)
                    / len(results))
    else:
        score = 0

    ok_count = sum(1 for r in results if r["status"] == "ok")
    warn_count = sum(1 for r in results if r["status"] == "warn")
    err_count = sum(1 for r in results if r["status"] == "error")

    return {
        "score": score,
        "results": results,
        "ok": ok_count,
        "warn": warn_count,
        "error": err_count,
        "total": len(results),
    }