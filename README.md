# ⚡ SystemCleanerPro

**Modernes Windows-System-Tool mit 15 Seiten, 5 Themes und Auto-Updater**

[![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)](https://github.com/vdnoez/SystemCleanerPro/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D4.svg)](https://github.com/vdnoez/SystemCleanerPro)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📖 Über das Projekt

**SystemCleanerPro** ist ein modernes Windows-System-Tool, das **Wartung, Sicherheit und Analyse** in einer einzigen App vereint. Es wurde mit **Python 3.11+ und PyQt6** entwickelt und bietet eine moderne Oberfläche mit 5 umschaltbaren Themes.

Im Gegensatz zu CCleaner, Auslogics und Wise Cleaner legt SystemCleanerPro Wert auf:
- 🚀 **Modernes Design** — Dark-UI mit Akzentfarben
- 🔒 **Privacy-First** — keine Telemetrie, keine Cloud
- 🎮 **Gaming-Fokus** — Prozess-Booster für Spiele
- 💻 **Developer-Tools** — Cleanup für Dev-Ordner

---

## ✨ Features

### 📊 Übersicht
| Seite | Beschreibung |
|-------|--------------|
| 🩺 **Health-Check** | 13 Systemprüfungen in einem Durchlauf |
| 📊 **Dashboard** | Live-Metriken + System-Score + Quick-Actions |
| 🖥️ **System-Info** | CPU, RAM, GPU, OS, Mainboard, Disks |
| ⚙️ **Prozesse** | Top 30 nach RAM mit Kill-Funktion |
| 🌐 **Netzwerk** | Live-Auslastung + aktive Verbindungen |

### 🧹 Wartung
| Seite | Beschreibung |
|-------|--------------|
| 🧹 **Cleaner** | Windows Temp + Dev-Ordner (node_modules, __pycache__) |
| 📦 **Software-Updater** | Updates via winget für installierte Programme |
| 💾 **RAM-Cleaner** | Working Sets leeren — crashsicher via Sub-Prozess |
| 🔥 **Shredder** | Sicheres Löschen nach DoD 5220.22-M |
| 🚀 **Autostart** | Startprogramme aktivieren/deaktivieren |
| 🔄 **App-Update** | Auto-Update via GitHub Releases |

### 🔐 Sicherheit
| Seite | Beschreibung |
|-------|--------------|
| 🔐 **Passwort-Manager** | AES-256 verschlüsselter Vault mit Master-Passwort |

### 🔍 Analyse
| Seite | Beschreibung |
|-------|--------------|
| 🔍 **BSOD-Analyzer** | Analysiert Bluescreen-Minidumps |
| 📥 **Downloads** | Download-Statistik via GitHub API |

### 🎮 Spiele
| Seite | Beschreibung |
|-------|--------------|
| 🎮 **Games-Booster** | Erkennt Spiele und boostet Prozess-Priorität |

---

## 🚀 Installation

### Option 1: Fertige EXE (Empfohlen)

1. Gehe zu [**Releases**](https://github.com/vdnoez/SystemCleanerPro/releases/latest)
2. Lade **`SystemCleanerPro.exe`** herunter
3. Doppelklick → **Fertig!**

**Keine Installation nötig.** Die App startet sich selbst als Administrator.

### Option 2: Aus dem Quellcode

```bash
git clone https://github.com/vdnoez/SystemCleanerPro.git
cd SystemCleanerPro
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py