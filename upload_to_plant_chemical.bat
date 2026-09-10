@echo off
title GitHub ga Yuklash (mohinurmutalibova945)
cd /d "%~dp0"

echo =========================================================
echo   mohinurmutalibova945 / plant-chemical ga yuklash
echo =========================================================
echo.
echo Brauzerda GitHub ochiladi, mohinurmutalibova945 bilan kiring.
echo.

git push https://github.com/mohinurmutalibova945/plant-chemical.git main -f

if errorlevel 1 (
    echo.
    echo [XATO] Yuklash amalga oshmadi.
) else (
    echo.
    echo =========================================================
    echo   MUVAFFAQIYATLI YUKLANDI! Render o'zi ishga tushadi.
    echo =========================================================
)

echo.
pause
