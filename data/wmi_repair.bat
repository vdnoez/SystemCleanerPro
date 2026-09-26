@echo off
chcp 65001 >nul
title WMI Reparatur
color 0E

echo.
echo =============================================================
echo   WMI-Reparatur fuer VPN-Unterstuetzung
echo =============================================================
echo.

REM Admin-Check
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo FEHLER: Keine Admin-Rechte!
    echo Bitte Rechtsklick -^> "Als Administrator ausfuehren"
    pause
    exit /b 1
)

echo [1/4] Pruefe WMI-Repository...
winmgmt /verifyrepository
echo.

echo [2/4] Erstelle Backup vor Reparatur...
winmgmt /backup
echo.

echo [3/4] Repariere WMI-Repository (kann 1-3 Min dauern)...
winmgmt /salvagerepository
echo.

echo [4/4] Verifiziere Reparatur...
winmgmt /verifyrepository
echo.

echo =============================================================
echo   FERTIG
echo =============================================================
echo.
echo Wenn die Reparatur erfolgreich war, starte deinen PC neu
echo und oeffne Cleaner Pro erneut.
echo.
echo Um zurueckzukehren: winmgmt /restore
echo.

pause
