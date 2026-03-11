@echo off
title Launching Application
echo Starting the application...
cd /d "%~dp0"

echo starting server...
start "" pythonw "%~dp0osu_watcher.py"
exit