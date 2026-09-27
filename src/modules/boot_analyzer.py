"""Boot-Time-Analyzer — mit Encoding-Fix."""
import subprocess
import json
from datetime import datetime


def _run_ps(cmd: str, timeout: int = 30) -> str:
    """Führt PowerShell aus mit Encoding-Fix."""
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        return (r.stdout or "").strip()
    except Exception:
        return ""


def get_boot_events_powershell() -> list:
    ps_cmd = (
        'Get-WinEvent -FilterHashtable '
        '@{LogName="Microsoft-Windows-Diagnostics-Performance/Operational";'
        'ID=100} -MaxEvents 30 -ErrorAction SilentlyContinue | '
        'Select-Object TimeCreated, '
        '@{Name="BootTime";Expression={$_.Properties[3].Value}}, '
        '@{Name="MainPathBootTime";Expression={$_.Properties[2].Value}}, '
        '@{Name="BootPostBootTime";Expression={$_.Properties[4].Value}} | '
        'ConvertTo-Json -Compress'
    )

    output = _run_ps(ps_cmd, timeout=30)
    if not output or output == "null":
        return []

    try:
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]

        events = []
        for ev in data:
            try:
                events.append({
                    "time": ev.get("TimeCreated", ""),
                    "boot_ms": ev.get("BootTime", 0) or 0,
                    "main_path_ms": ev.get("MainPathBootTime", 0) or 0,
                    "post_boot_ms": ev.get("BootPostBootTime", 0) or 0,
                })
            except Exception:
                continue
        return events
    except json.JSONDecodeError:
        return []


def format_ms(ms: int) -> str:
    if ms <= 0:
        return "—"
    total_sec = ms / 1000
    if total_sec < 60:
        return f"{total_sec:.1f} Sek"
    minutes = int(total_sec // 60)
    seconds = total_sec % 60
    return f"{minutes} Min {seconds:.0f} Sek"


def get_boot_summary() -> dict:
    events = get_boot_events_powershell()

    if not events:
        return {
            "total": 0, "events": [],
            "avg_ms": 0, "fastest_ms": 0,
            "slowest_ms": 0, "latest_ms": 0,
        }

    times = [e["boot_ms"] for e in events if e["boot_ms"] > 0]

    if not times:
        return {
            "total": len(events), "events": events,
            "avg_ms": 0, "fastest_ms": 0,
            "slowest_ms": 0, "latest_ms": 0,
        }

    return {
        "total": len(events),
        "events": events,
        "avg_ms": int(sum(times) / len(times)),
        "fastest_ms": min(times),
        "slowest_ms": max(times),
        "latest_ms": times[0],
    }