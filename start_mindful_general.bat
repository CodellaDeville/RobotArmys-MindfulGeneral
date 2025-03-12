@echo off
title Mindful General - Spreading Peace and Understanding
color 0A

:: Change to the script's directory
cd /d "%~dp0"

echo Welcome to Mindful General!
echo This program will help spread peace and understanding.
echo.
echo Starting your peace journey...
echo.

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Oh no! Python isn't installed on this computer.
    echo Please ask a grown-up to help install Python from python.org
    echo.
    pause
    exit /b
)

:: Run the start script
python start.py

echo.
if errorlevel 1 (
    echo If you see any errors above, please ask a grown-up for help.
) else (
    echo Mindful General is running! You're helping make the world more peaceful.
)
echo.
pause 