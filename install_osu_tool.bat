@echo off
title osu! Tool - Installation
color 0D

echo.
echo  =========================================
echo    osu! Tool - Installation
echo  =========================================
echo.

echo  [1/2] Installation de Python via winget...
winget install --id Python.Python.3.13 --source winget --accept-package-agreements --accept-source-agreements

echo.
echo  [2/2] Installation des librairies via pip...
python -m pip install PyQt6 pillow pystray win10toast

echo.
echo  =========================================
echo    Installation terminee !
echo    Lance osu_watcher.py pour demarrer.
echo  =========================================
echo.
pause
