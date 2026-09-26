"""Entry point — startet als Admin, prüft Updates."""
import sys
import ctypes
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def is_admin() -> bool:
    """Prüft ob App als Admin läuft."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    """Startet die App neu mit Admin-Rechten."""
    try:
        script = str(Path(sys.argv[0]).resolve())
        params = " ".join(sys.argv[1:])

        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            f'"{script}" {params}',
            str(PROJECT_ROOT),
            1
        )
        return ret > 32
    except Exception as e:
        print(f"Fehler beim Admin-Start: {e}")
        return False


def main():
    # ─── Admin-Check ───
    if not is_admin():
        print("Starte mit Administrator-Rechten...")
        if run_as_admin():
            sys.exit(0)
        else:
            print("⚠️  Admin-Start abgelehnt — starte normal")

    # ─── Ab hier normale App ───
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import QTimer

    from src.core.config import APP_NAME, APP_VERSION

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setQuitOnLastWindowClosed(False)

    # Theme laden
    from src.ui.settings_dialog import load_settings
    from src.ui.theme import set_theme
    settings = load_settings()
    set_theme(settings.get("theme", "aurora"))

    # ─── Auto-Update-Check ───
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
                    f"Eine neue Version ist verfügbar!\n\n"
                    f"Aktuell:  v{update_info['current_version']}\n"
                    f"Neu:       v{update_info['latest_version']}\n\n"
                    f"Möchtest du jetzt updaten?"
                )
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No
                )
                msg.setDefaultButton(QMessageBox.StandardButton.Yes)

                reply = msg.exec()

                if reply == QMessageBox.StandardButton.Yes:
                    # Merken → Update-Seite öffnen
                    app.setProperty("open_update_page", True)
            elif update_info.get("error"):
                print(f"[Auto-Update] {update_info['error']}")
            else:
                print(
                    f"[Auto-Update] Aktuell: v{update_info['current_version']}"
                )
        except Exception as e:
            print(f"[Auto-Update] Fehler: {e}")

    # ─── Splash oder direkt ───
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

                    # Update-Seite öffnen falls Update verfügbar
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