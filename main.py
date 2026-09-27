"""Entry point — Admin-Start, Lizenz-Check, Auto-Update."""
import sys
import os
import ctypes
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════
# RAM-CLEANER HELPER-MODUS (muss VOR Admin-Check stehen!)
# ═══════════════════════════════════════════════════════════════
def _run_ram_cleaner_helper():
    try:
        from src.modules.ram_cleaner import _worker_run
        import json
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
    except Exception as e:
        try:
            print(f'{{"success": false, "error": "{e}"}}')
        except Exception:
            pass
    sys.exit(0)


if "--ram-cleaner-helper" in sys.argv:
    _run_ram_cleaner_helper()


# ═══════════════════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════════════════
def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    try:
        script = str(Path(sys.argv[0]).resolve())
        params = " ".join(sys.argv[1:])
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            f'"{script}" {params}',
            str(PROJECT_ROOT), 1
        )
        return ret > 32
    except Exception as e:
        print(f"Fehler beim Admin-Start: {e}")
        return False


def _cleanup_temp_on_start():
    if not getattr(sys, "frozen", False):
        return
    try:
        from src.modules.cleanup_temp import cleanup_old_mei
        removed = cleanup_old_mei(max_age_hours=6)
        if removed > 0:
            print(f"[Cleanup] {removed} alte _MEI-Ordner gelöscht")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    # ─── Admin-Check ───
    if not is_admin():
        print("Starte mit Administrator-Rechten...")
        if run_as_admin():
            sys.exit(0)
        else:
            print("⚠️  Admin-Start abgelehnt — starte normal")

    _cleanup_temp_on_start()

    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import QTimer

    from src.core.config import APP_NAME, APP_VERSION

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setQuitOnLastWindowClosed(False)

    # ═══════════════════════════════════════════════════════════
    # LIZENZ-CHECK
    # ═══════════════════════════════════════════════════════════
    try:
        from src.modules.license import get_license_status
        from src.ui.license_dialog import LicenseDialog

        status = get_license_status()

        if status["status"] == "expired":
            # Trial abgelaufen → Aktivierung erzwingen
            dialog = LicenseDialog(force_activation=True)
            dialog.exec()
            if not dialog.activated:
                print("Lizenz nicht aktiviert — beende App")
                sys.exit(0)

        elif status["status"] == "missing":
            # Kein Status → Aktivierung erzwingen
            dialog = LicenseDialog(force_activation=True)
            dialog.exec()
            if not dialog.activated:
                sys.exit(0)

        elif status["status"] == "trial":
            # Trial läuft — bei wenig Restzeit warnen
            days = status.get("trial_days_left", 0)
            if days <= 3:
                reply = QMessageBox.question(
                    None,
                    f"Testversion — noch {days} Tage",
                    f"Deine Testversion läuft am "
                    f"{status.get('trial_expires', '?')} ab.\n\n"
                    f"Möchtest du jetzt einen Lizenz-Key eingeben?",
                    QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    LicenseDialog().exec()
    except Exception as e:
        print(f"[Lizenz-Fehler] {e}")

    # ═══════════════════════════════════════════════════════════
    # THEME
    # ═══════════════════════════════════════════════════════════
    from src.ui.settings_dialog import load_settings
    from src.ui.theme import set_theme
    settings = load_settings()
    set_theme(settings.get("theme", "slate"))

    # ═══════════════════════════════════════════════════════════
    # AUTO-UPDATE-CHECK
    # ═══════════════════════════════════════════════════════════
    if settings.get("auto_check_updates", True):
        try:
            from src.modules.updater import check_for_update
            print("[Auto-Update] Prüfe auf neue Version...")
            update_info = check_for_update(timeout=8)
            if update_info.get("update_available"):
                msg = QMessageBox()
                msg.setWindowTitle("Update verfügbar")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText(
                    f"Neue Version verfügbar!\n\n"
                    f"Aktuell:  v{update_info['current_version']}\n"
                    f"Neu:       v{update_info['latest_version']}"
                )
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No
                )
                if msg.exec() == QMessageBox.StandardButton.Yes:
                    app.setProperty("open_update_page", True)
            elif update_info.get("error"):
                print(f"[Auto-Update] {update_info['error']}")
        except Exception as e:
            print(f"[Auto-Update] Fehler: {e}")

    # ═══════════════════════════════════════════════════════════
    # SPLASH + MAIN WINDOW
    # ═══════════════════════════════════════════════════════════
    if settings.get("show_splash", True):
        try:
            from src.ui.splash import SplashScreen
            splash = SplashScreen()
            splash.show()
            app.processEvents()

            fallback = QTimer()
            fallback.setSingleShot(True)
            launched = {"done": False}

            def launch_main():
                if launched["done"]:
                    return
                launched["done"] = True
                try:
                    from src.ui.main_window import MainWindow
                    window = MainWindow()
                    window.show()

                    if app.property("open_update_page"):
                        try:
                            window.open_update_page()
                        except Exception:
                            pass

                    try:
                        splash.finish(window)
                    except Exception:
                        pass
                except Exception as e:
                    print(f"[FEHLER] {e}")
                    import traceback
                    traceback.print_exc()

            splash.finished.connect(launch_main)
            fallback.timeout.connect(launch_main)
            fallback.start(8000)
        except Exception as e:
            print(f"[Splash-Fehler] {e} — starte direkt")
            from src.ui.main_window import MainWindow
            window = MainWindow()
            window.show()
            if app.property("open_update_page"):
                try:
                    window.open_update_page()
                except Exception:
                    pass
    else:
        from src.ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        if app.property("open_update_page"):
            try:
                window.open_update_page()
            except Exception:
                pass

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())