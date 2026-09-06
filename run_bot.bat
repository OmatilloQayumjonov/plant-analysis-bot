@echo off
title Plant Chemical Analysis - Telegram Bot
cd /d "%~dp0"

echo ====================================================
echo   Plant Chemical Analysis - DPPH / IC50 Bot
echo ====================================================
echo.

set "PYTHON=C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe"

if not exist "%PYTHON%" (
    where py >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON=py -3"
    ) else (
        set "PYTHON=python"
    )
)

echo Python: %PYTHON%
echo.

"%PYTHON%" main.py

if errorlevel 1 (
    echo.
    echo [DIQQAT] Bot to'xtadi yoki xatolik yuz berdi.
)

echo.
pause
