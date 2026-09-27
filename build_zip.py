"""
Erstellt eine portable ZIP-Datei (OHNE Lizenz!).
Packt den kompletten dist/SystemCleanerPro/-Ordner.
"""
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
APP_FOLDER = DIST / "SystemCleanerPro"
VERSION_FILE = ROOT / "version.txt"


def get_version() -> str:
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    return "unknown"


def check_no_license() -> bool:
    """Prüft dass keine Lizenz-Datei in dist/ ist."""
    print("[1/4] Prüfe ob Lizenz-Datei vorhanden...")
    license_files = list(DIST.rglob("license.json"))

    if license_files:
        print()
        print("  ⚠️  WARNUNG: Lizenz-Datei(en) gefunden!")
        for f in license_files:
            print(f"     → {f}")
        print()
        print("  Diese Datei würde in die ZIP kommen!")
        print("  Andere könnten deine Lizenz nutzen.")
        print()
        response = input("  Trotzdem fortfahren? (j/n): ").strip().lower()
        return response == "j"

    print("      ✅ Keine Lizenz-Datei gefunden.")
    return True


def check_app_folder() -> bool:
    """Prüft ob dist/SystemCleanerPro/ existiert."""
    print()
    print("[2/4] Prüfe Projekt-Ordner...")

    if not APP_FOLDER.exists():
        print(f"      ❌ Ordner nicht gefunden: {APP_FOLDER}")
        print()
        print("      Bitte erst build_exe.bat ausführen!")
        return False

    # Anzahl Dateien zählen
    file_count = sum(1 for _ in APP_FOLDER.rglob("*") if _.is_file())
    print(f"      ✅ Ordner gefunden ({file_count} Dateien)")
    return True


def create_zip() -> Path:
    version = get_version()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    zip_name = f"SystemCleanerPro_v{version}_portable_{timestamp}.zip"
    zip_path = DIST / zip_name

    if zip_path.exists():
        zip_path.unlink()

    print()
    print("[3/4] Packe ZIP (kann 1-2 Min dauern)...")
    print(f"      Ziel: {zip_name}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in APP_FOLDER.rglob("*"):
            if file.is_file():
                # Relativer Pfad: "SystemCleanerPro/SystemCleanerPro.exe"
                arcname = file.relative_to(DIST)
                zf.write(file, arcname)

    return zip_path


def report(zip_path: Path):
    print()
    print("[4/4] Fertig!")
    print()

    if not zip_path or not zip_path.exists():
        print("❌ ZIP nicht erstellt.")
        return

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    version = get_version()

    print("=" * 60)
    print("  ✅ ZIP ERFOLGREICH ERSTELLT")
    print("=" * 60)
    print(f"  📁 Datei:    {zip_path.name}")
    print(f"  📊 Größe:    {size_mb:.1f} MB")
    print(f"  🏷️  Version:  {version}")
    print(f"  📂 Pfad:     {zip_path}")
    print()
    print("  🚀 Upload auf GitHub Release:")
    print(f"      {zip_path}")
    print()
    print("  ℹ️  Nutzer:")
    print("      1. ZIP herunterladen")
    print("      2. Entpacken")
    print("      3. SystemCleanerPro.exe starten")


def main():
    print("=" * 60)
    print("  SystemCleanerPro — Portable ZIP Builder")
    print("=" * 60)
    print()

    if not check_no_license():
        print("Abgebrochen.")
        return

    if not check_app_folder():
        return

    zip_path = create_zip()
    report(zip_path)


if __name__ == "__main__":
    main()