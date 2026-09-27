# Changelog

Alle wichtigen Änderungen an diesem Projekt.

## [1.0.2] - 2026-09-27

### ✨ Hinzugefügt
- **Download-Statistik-Seite** — zeigt Downloads pro Release (via GitHub API)
- **Über-Dialog** mit Besitzer-Angabe: **vdnoez**
- **5 neue Themes:** Slate (Standard), Carbon, Ocean, Forest, Light
- **3D-Effekte** für Circular Progress mit Glow
- **Besitzer-Info** im About-Dialog und in der Statusbar

### 🎨 Geändert
- **Komplett neues Design-System** (ruhiger, luftiger)
- **Sidebar auf 260px verbreitert** — Labels werden nicht mehr abgeschnitten
- **Kategorien mit Emoji-Icons** vor dem Namen
- **Buttons als Outline-Stil** (Akzent bei Hover)
- **Card-Padding auf 24px** standardisiert
- **Konsistente Abstände** (8/16/24/32px Grid)

### 🐛 Behoben
- **Sidebar-Labels** wurden abgeschnitten
- **Doppelter App-Update-Eintrag** entfernt
- **RAM-Cleaner** crasht nicht mehr in der EXE
- **SSL-Fehler** bei HTTPS-Verbindungen in EXE behoben
- **One-Folder-Build** — keine Temp-Warnungen mehr

### 🗑️ Entfernt
- Alte bunte Themes (Sunset, Emerald, Royal, Mono, Cyberpunk)
- VPN-Manager (zu komplexe WMI-Abhängigkeit) — ersetzt durch Info-Seite

---

## [1.0.1] - 2026-09-26

### ✨ Hinzugefügt
- **Software-Updater** (winget)
- **App-Update via GitHub Releases**
- **Auto-Update-Check** beim Start
- **download_stats.py** und **stats_page.py**

### 🐛 Behoben
- Import-Fehler bei `updater_page.py`

---

## [1.0.0] - 2026-09-25

### ✨ Erste Version
- 16 Seiten (Dashboard, Cleaner, RAM, Shredder, Autostart, Passwort, DNS, BSOD, Boot, Games, Health-Check, Prozesse, Netzwerk, VPN-Info, Software-Updater, App-Update)
- Passwort-Manager mit AES-256
- Health-Check mit 13 Prüfungen
- 6 Themes
- Splash-Screen
- Tray-Icon
- Auto-Admin-Start

---

**Besitzer:** vdnoez  
**Repository:** https://github.com/vdnoez/SystemCleanerPro