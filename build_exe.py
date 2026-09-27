"""
System Cleaner Pro - EXE Builder (ONE-FOLDER MODE)
Keine Temp-Warnings, sauberer Start.
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
    print("[1/5] Räume auf...")
    for d in (DIST, BUILD):
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
    if SPEC.exists():
        SPEC.unlink()


def install_pyinstaller():
    print("[2/5] Prüfe PyInstaller...")
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
    print("[3/5] Prüfe Abhängigkeiten...")
    deps = [
        "qtawesome", "cryptography", "send2trash",
        "psutil", "pywin32", "wmi", "requests", "certifi",
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
    print("[4/5] Baue EXE im ONE-FOLDER-Modus (dauert 2-4 Minuten)...")
    print("      Bitte warten.")
    print()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        # KEIN --onefile! → One-Folder-Modus
        "--windowed",                           # keine Konsole
        "--name", EXE_NAME,
        "--add-data", f"data{DATA_SEP}data",
        "--add-data", f"version.txt{DATA_SEP}.",
        # Hidden Imports
        "--hidden-import", "winreg",
        "--hidden-import", "wmi",
        "--hidden-import", "send2trash",
        "--hidden-import", "qtawesome",
        "--hidden-import", "cryptography",
        "--hidden-import", "cryptography.fernet",
        "--hidden-import", "cryptography.hazmat.primitives.hashes",
        "--hidden-import", "cryptography.hazmat.primitives.kdf.pbkdf2",
        "--hidden-import", "certifi",
        # Collect-All
        "--collect-all", "PyQt6",
        "--collect-all", "qtawesome",
        "--collect-all", "send2trash",
        "--collect-all", "certifi",
        "--collect-data", "certifi",
        # Excludes
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


def copy_extras():
    """Kopiert version.txt + data/ in den App-Ordner."""
    print("[5/5] Kopiere Zusatzdateien...")

    app_dir = DIST / EXE_NAME  # dist/SystemCleanerPro/

    if not app_dir.exists():
        print(f"      ⚠️  {app_dir} fehlt!")
        return

    # version.txt
    src_version = ROOT / "version.txt"
    if src_version.exists():
        shutil.copy2(src_version, app_dir / "version.txt")
        print(f"      ✅ version.txt → {app_dir}")

    # data/
    src_data = ROOT / "data"
    dst_data = app_dir / "data"
    if src_data.exists():
        if dst_data.exists():
            shutil.rmtree(dst_data, ignore_errors=True)
        shutil.copytree(src_data, dst_data)
        print(f"      ✅ data/ → {app_dir}")


def report():
    print()
    print("=" * 60)
    print("  ✅ BUILD ERFOLGREICH")
    print("=" * 60)

    app_dir = DIST / EXE_NAME
    exe = app_dir / f"{EXE_NAME}.exe"

    if exe.exists():
        print(f"  📁 App-Ordner:  {app_dir}")
        print(f"  📁 EXE:         {exe}")

        # Gesamtgröße
        total = sum(f.stat().st_size for f in app_dir.rglob("*") if f.is_file())
        print(f"  📊 Gesamtgröße: {total / (1024*1024):.1f} MB")
    else:
        print(f"  ❌ EXE fehlt: {exe}")

    version_file = app_dir / "version.txt"
    if version_file.exists():
        version = version_file.read_text(encoding="utf-8").strip()
        print(f"  🏷️  Version:     {version}")

    print()
    print("  🚀 Starten mit:")
    print(f"      {exe}")
    print()
    print("  ℹ️  Der Ordner 'dist/SystemCleanerPro' muss")
    print("      KOMPLETT weitergegeben werden (EXE + _internal/ + data/).")


def main():
    print("=" * 60)
    print(f"  {EXE_NAME} - EXE Builder (ONE-FOLDER)")
    print("=" * 60)
    print()

    clean()
    install_pyinstaller()
    install_missing_deps()
    build()
    copy_extras()
    report()


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build fehlgeschlagen: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Abgebrochen.")
        sys.exit(1)