@echo off
title Osu Watcher Installation
color 0b 

echo =================================
echo  Osu Watcher Installation 
echo =================================
echo.
set /p install="Do you want to install Osu Watcher? (Y/N): "

if /i "%install%"=="y" goto install
if /i "%install%"=="n" goto end
goto end

:install
echo.
echo Installing Osu Watcher...

echo  [1/2] Installation de Python via winget...
winget install --id Python.Python.3.13 --source winget --accept-package-agreements --accept-source-agreements

echo.
echo  [2/2] Installation des librairies via pip...
python -m pip install PyQt6 pillow pystray win10toast

mkdir "%ProgramFiles%\Osu Watcher" > nul 2>&1
copy osu_watcher.py "%ProgramFiles%\Osu Watcher" > nul 2>&1
copy launch.bat "%ProgramFiles%\Osu Watcher" > nul 2>&1




echo Installation completed successfully!
echo =========================================================================================
echo For more information, visit the GitHub repository: https://github.com/Mish4ry/OSU-Watcher
echo =========================================================================================
echo For launch use: launch.bat
echo Exiting installer. Press any key to close.

pause >nul
exit