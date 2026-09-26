"""Privacy-Score mit Registry-Checks + Auto-Fix."""
import winreg
from typing import Any

from src.core.config_loader import load_json

HIVES = {
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
}


def _load_checks() -> list[dict]:
    return load_json("privacy_checks.json").get("checks", [])


def _read(hive, path: str, value_name: str):
    try:
        with winreg.OpenKey(hive, path) as key:
            v, _ = winreg.QueryValueEx(key, value_name)
            return v
    except FileNotFoundError:
        return None
    except OSError:
        return None


def calculate_privacy_score() -> tuple[int, list[dict]]:
    """Gibt (Score 0-100, Details-Liste) zurück."""
    checks = _load_checks()
    if not checks:
        return 0, []

    total_weight = sum(c.get("weight", 1) for c in checks)
    score = 0
    details = []

    for c in checks:
        hive = HIVES.get(c.get("hive", "HKLM"))
        if hive is None:
            continue
        actual = _read(hive, c["path"], c["value"])
        ok = actual == c["expected"]
        if ok:
            score += c.get("weight", 1)

        details.append({
            "id": c.get("id", "?"),
            "name": c.get("name", "?"),
            "description": c.get("description", ""),
            "ok": ok,
            "actual": actual,
            "expected": c["expected"],
            "weight": c.get("weight", 1),
            "fix": c.get("fix"),
            "hive_key": c.get("hive", "HKLM"),
            "path": c["path"],
            "value": c["value"],
        })

    pct = int(score / total_weight * 100) if total_weight else 0
    return pct, details


def apply_fix(check: dict) -> tuple[bool, str]:
    """Wendet den Fix eines Checks an. Returns (erfolg, meldung)."""
    fix = check.get("fix")
    if not fix:
        return False, "Kein Fix definiert"

    hive = HIVES.get(check["hive_key"])
    if hive is None:
        return False, "Unbekannte Hive"

    try:
        # Key öffnen oder erstellen
        key = winreg.CreateKeyEx(hive, check["path"], 0,
                                 winreg.KEY_SET_VALUE)
        action = fix.get("action", "set_dword")
        value = fix["value"]

        if action == "set_dword":
            winreg.SetValueEx(key, check["value"], 0,
                              winreg.REG_DWORD, int(value))
        elif action == "set_string":
            winreg.SetValueEx(key, check["value"], 0,
                              winreg.REG_SZ, str(value))
        elif action == "set_qword":
            winreg.SetValueEx(key, check["value"], 0,
                              winreg.REG_QWORD, int(value))
        else:
            winreg.CloseKey(key)
            return False, f"Unbekannte Aktion: {action}"

        winreg.CloseKey(key)
        return True, "OK"
    except PermissionError:
        return False, "Zugriff verweigert (App als Admin starten?)"
    except Exception as e:
        return False, str(e)


def apply_all_fixes() -> tuple[int, int, list[str]]:
    """Wendet alle Fixes an. Returns (erfolge, fehler, meldungen)."""
    _, details = calculate_privacy_score()
    failed_checks = [c for c in details if not c["ok"]]
    ok = 0
    errors = []
    for c in failed_checks:
        success, msg = apply_fix(c)
        if success:
            ok += 1
        else:
            errors.append(f"{c['name']}: {msg}")
    return ok, len(failed_checks) - ok, errors