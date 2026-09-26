@echo off
chcp 65001 >nul
title SystemCleanerPro - EXE Builder
color 0B

echo.
echo =============================================================
echo   SystemCleanerPro - EXE Builder
echo =============================================================
echo.

cd /d "%~dp0"

REM Prüfe venv
if not exist ".venv\Scripts\python.exe" (
    echo FEHLER: .venv nicht gefunden!
    echo Bitte erst Setup ausfuehren.
    pause
    exit /b 1
)

REM Aktiviere venv
call .venv\Scripts\activate.bat

REM Führe Python-Builder aus
python build_exe.py

if errorlevel 1 (
    echo.
    echo =============================================================
    echo   FEHLER beim Build
    echo =============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo =============================================================
echo   FERTIG
echo =============================================================
echo.

if exist "dist\SystemCleanerPro.exe" (
    echo EXE liegt hier:
    echo   %CD%\dist\SystemCleanerPro.exe
    echo.
    echo Configs liegen hier:
    echo   %CD%\dist\data\
    echo.
    echo ⚠️  Beide zusammen weitergeben!
    echo.
)

REM Optional: Explorer öffnen
choice /C JN /M "dist-Ordner jetzt öffnen"
if errorlevel 2 goto :end
if errorlevel 1 explorer "%CD%\dist"

:end
echo.
pause