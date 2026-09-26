"""
System Cleaner Pro - EXE Builder
Erstellt eine standalone .exe mit allen Features.
"""
import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
SPEC = ROOT / "SystemCleanerPro.spec"
EXE_NAME = "SystemCleanerPro"
ENTRY = "main.py"
DATA_SEP = ";" if sys.platform == "win32" else ":"


def clean():
    print("[1/6] Räume auf...")
    for d in (DIST, BUILD):
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
    if SPEC.exists():
        SPEC.unlink()


def install_pyinstaller():
    print("[2/6] Prüfe PyInstaller...")
    try:
        import PyInstaller  # noqa
        print("      ✅ PyInstaller vorhanden.")
    except ImportError:
        print("      Installiere PyInstaller...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            check=True
        )


def install_missing_deps():
    print("[3/6] Prüfe Abhängigkeiten...")
    deps = [
        "qtawesome",
        "cryptography",
        "send2trash",
        "psutil",
        "pywin32",
        "wmi",
        "requests",
    ]
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            print(f"      Installiere {dep}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                check=False
            )


def build():
    print("[4/6] Baue EXE (dauert 2-5 Minuten)...")
    print("      Bitte warten, keine Eingabe nötig.")
    print()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",                          # keine Konsole
        "--name", EXE_NAME,
        "--add-data", f"data{DATA_SEP}data",   # data/ neben EXE
        # Hidden Imports
        "--hidden-import", "winreg",
        "--hidden-import", "wmi",
        "--hidden-import", "send2trash",
        "--hidden-import", "qtawesome",
        "--hidden-import", "cryptography",
        "--hidden-import", "cryptography.fernet",
        "--hidden-import", "cryptography.hazmat.primitives.hashes",
        "--hidden-import", "cryptography.hazmat.primitives.kdf.pbkdf2",
        # PyQt6 komplett einsammeln
        "--collect-all", "PyQt6",
        "--collect-all", "qtawesome",
        "--collect-all", "send2trash",
        # Exclude unnötige Riesen-Module
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "pandas",
        "--exclude-module", "scipy",
        "--exclude-module", "tkinter",
        "--exclude-module", "PyQt5",
        "--exclude-module", "PySide2",
        "--exclude-module", "PySide6",
        ENTRY,
    ]

    subprocess.run(cmd, cwd=ROOT, check=True)


def copy_data_folder():
    """Kopiert data/ neben die EXE für editierbare Configs."""
    print("[5/6] Kopiere data/-Ordner neben EXE...")
    src = ROOT / "data"
    dst = DIST / "data"

    if not src.exists():
        print("      ⚠️  data/ fehlt — erstelle leeren Ordner")
        dst.mkdir(parents=True, exist_ok=True)
        return

    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)
    print(f"      ✅ {dst}")


def report():
    print("[6/6] Fertig!")
    exe = DIST / f"{EXE_NAME}.exe"
    if exe.exists():
        size_mb = exe.stat().st_size / (1024 * 1024)
        print()
        print("=" * 60)
        print("  ✅ EXE ERFOLGREICH ERSTELLT")
        print("=" * 60)
        print(f"  📁 Pfad:   {exe}")
        print(f"  📊 Größe:  {size_mb:.1f} MB")
        print()
        print(f"  📂 Configs: {DIST / 'data'}")
        print()
        print("  🚀 Doppelklick auf die EXE zum Starten!")
        print()
        print("  ⚠️  WICHTIG: Der 'data'-Ordner muss IMMER")
        print("      neben der EXE liegen, sonst findet die App")
        print("      ihre Einstellungen nicht.")
    else:
        print("❌ EXE nicht gefunden — Build fehlgeschlagen.")
        sys.exit(1)


def main():
    print("=" * 60)
    print(f"  {EXE_NAME} - EXE Builder")
    print("=" * 60)
    print()

    clean()
    install_pyinstaller()
    install_missing_deps()
    build()
    copy_data_folder()
    report()


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build fehlgeschlagen: {e}")
        print("Prüfe die Ausgabe oben für Details.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Abgebrochen.")
        sys.exit(1)