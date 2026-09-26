"""BSOD-Analyzer — liest Minidumps und erklärt Bluescreens."""
import os
import struct
from datetime import datetime
from pathlib import Path


MINIDUMP_DIRS = [
    Path(r"C:\Windows\Minidump"),
    Path(r"C:\Windows\LiveKernelReports"),
    Path(os.path.expandvars(r"%LOCALAPPDATA%\CrashDumps")),
]


# Stop-Code Übersetzungen
STOP_CODES = {
    0x0000000A: ("IRQL_NOT_LESS_OR_EQUAL",
        "Ein Treiber hat auf Speicher zugegriffen den er nicht darf. "
        "Meist durch veraltete oder fehlerhafte Treiber."),
    0x0000001E: ("KMODE_EXCEPTION_NOT_HANDLED",
        "Ein Kernel-Treiber hat einen unbehandelten Fehler. "
        "Häufig durch defekten RAM oder inkompatible Treiber."),
    0x0000003B: ("SYSTEM_SERVICE_EXCEPTION",
        "Ein Systemdienst ist abgestürzt. Oft durch Grafikkartentreiber."),
    0x00000050: ("PAGE_FAULT_IN_NONPAGED_AREA",
        "Speicherfehler — oft defekter RAM oder fehlerhafte Treiber."),
    0x0000007E: ("SYSTEM_THREAD_EXCEPTION_NOT_HANDLED",
        "Ein System-Thread hatte eine unbehandelte Ausnahme. "
        "Meist durch veraltete Treiber."),
    0x0000007F: ("UNEXPECTED_KERNEL_MODE_TRAP",
        "CPU hat einen unerwarteten Fehler gemeldet. "
        "Oft Hardware-Problem oder Übertaktung."),
    0x0000009F: ("DRIVER_POWER_STATE_FAILURE",
        "Ein Treiber kam mit Energiesparmodus nicht klar. "
        "Häufig bei Netzwerk- oder USB-Treibern."),
    0x000000D1: ("DRIVER_IRQL_NOT_LESS_OR_EQUAL",
        "Ein Treiber hat auf falsche Speicheradresse zugegriffen."),
    0x000000EF: ("CRITICAL_PROCESS_DIED",
        "Ein kritischer Windows-Prozess wurde beendet. "
        "Systemdateien prüfen mit sfc /scannow."),
    0x00000133: ("DPC_WATCHDOG_VIOLATION",
        "Ein Treiber hat zu lange blockiert. Oft SSD-Firmware-Problem."),
    0x00000139: ("KERNEL_SECURITY_CHECK_FAILURE",
        "Sicherheitsüberprüfung fehlgeschlagen. Oft durch Malware oder "
        "inkompatible Sicherheitssoftware."),
    0xC000021A: ("STATUS_SYSTEM_PROCESS_TERMINATED",
        "Ein Systemprozess wurde beendet. Oft nach Windows-Update."),
    0x00000124: ("WHEA_UNCORRECTABLE_ERROR",
        "Hardware-Fehler. CPU/RAM/Netzteil defekt oder zu heiß."),
    0x000000F4: ("CRITICAL_OBJECT_TERMINATION",
        "Kritischer Systemprozess wurde beendet. Oft durch "
        "fehlerhafte Treiber oder Antivirus."),
}


def find_minidumps() -> list[Path]:
    """Findet alle Minidump-Dateien."""
    dumps = []
    for d in MINIDUMP_DIRS:
        if not d.exists():
            continue
        try:
            for f in d.rglob("*.dmp"):
                dumps.append(f)
        except (PermissionError, OSError):
            continue
    return sorted(dumps, key=lambda p: p.stat().st_mtime, reverse=True)


def extract_stop_code(dump_path: Path) -> int | None:
    """
    Versucht den Stop-Code aus dem Minidump zu lesen.
    Das ist eine vereinfachte Version — echte Analyse braucht WinDbg.
    """
    try:
        # Minidump-Format: Stop-Code steht ab Offset 0xF00 (meist)
        with open(dump_path, "rb") as f:
            data = f.read(0x2000)
    except (PermissionError, OSError):
        return None

    # Wir suchen nach typischen Mustern
    # Ein echter Minidump hat eine ExceptionStream oder einen
    # BUGCHECK Code. Wir suchen im Bereich 0x1000-0x2000.
    candidates = []
    for offset in range(0xF00, min(0x2000, len(data) - 4), 4):
        try:
            val = struct.unpack("<I", data[offset:offset+4])[0]
            if val in STOP_CODES:
                candidates.append((val, offset))
        except struct.error:
            break

    if candidates:
        # Nimm den ersten Treffer
        return candidates[0][0]
    return None


def parse_dump(dump_path: Path) -> dict:
    """Parst einen Dump und gibt Infos zurück."""
    stat = dump_path.stat()
    size_kb = stat.st_size / 1024
    mtime = datetime.fromtimestamp(stat.st_mtime)

    stop_code = extract_stop_code(dump_path)

    info = {
        "path": dump_path,
        "filename": dump_path.name,
        "date": mtime.strftime("%d.%m.%Y  %H:%M:%S"),
        "size_kb": size_kb,
        "stop_code": stop_code,
        "stop_code_hex": f"0x{stop_code:08X}" if stop_code else None,
        "name": None,
        "description": None,
        "severity": "unknown",
    }

    if stop_code and stop_code in STOP_CODES:
        name, desc = STOP_CODES[stop_code]
        info["name"] = name
        info["description"] = desc

        # Severity
        critical = {0x00000124, 0x00000133, 0x000000EF, 0x000000F4}
        if stop_code in critical:
            info["severity"] = "critical"
        else:
            info["severity"] = "warning"

    return info


def get_crash_summary() -> dict:
    """Gesamtübersicht über alle Crashes."""
    dumps = find_minidumps()
    crashes = [parse_dump(d) for d in dumps]

    if not crashes:
        return {"total": 0, "crashes": [], "latest": None}

    # Gruppiere nach Stop-Code
    from collections import Counter
    codes = Counter(c["stop_code"] for c in crashes if c["stop_code"])

    return {
        "total": len(crashes),
        "crashes": crashes,
        "latest": crashes[0] if crashes else None,
        "top_codes": codes.most_common(5),
    }