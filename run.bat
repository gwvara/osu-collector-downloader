@echo off
chcp 65001 >nul 2>&1
title osu! Beatmap Collection Downloader

:: Run from script directory
cd /d "%~dp0"

:: Check if dependencies are installed
python -c "import rich, requests" >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Dependencies belum terinstall!
    echo  Jalankan 'install.bat' terlebih dahulu.
    echo.
    pause
    exit /b 1
)

:: Run the application
python main.py

:: If python exits with error
if errorlevel 1 (
    echo.
    echo  Aplikasi keluar dengan error.
    pause
)
