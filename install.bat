@echo off
chcp 65001 >nul 2>&1
title osu! Beatmap Downloader - Install

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║   osu! Beatmap Downloader - Installer     ║
echo  ╚═══════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python tidak ditemukan!
    echo  Silakan install Python dari https://python.org
    echo  Pastikan centang "Add Python to PATH" saat install.
    echo.
    pause
    exit /b 1
)

echo  [INFO] Python ditemukan:
python --version
echo.

:: Install dependencies
echo  [INFO] Menginstall dependencies...
echo.
pip install -r "%~dp0requirements.txt"

if errorlevel 1 (
    echo.
    echo  [ERROR] Gagal menginstall dependencies!
    echo  Coba jalankan ulang sebagai Administrator.
    pause
    exit /b 1
)

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║   ✅ Instalasi Berhasil!                  ║
echo  ║   Jalankan 'run.bat' untuk memulai.       ║
echo  ╚═══════════════════════════════════════════╝
echo.
pause
