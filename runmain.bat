@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed. Installing Python...
    start https://www.python.org/downloads/
    pause
    goto :checkpython
) else (
    echo Python is already installed.
)

:checkpython
:: Check if Python is installed again
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Please install Python manually and rerun this script.
    exit /b 1
)

:: Install PRAW using pip
echo Installing PRAW...
pip install praw

:: Check if PRAW was installed successfully
pip show praw >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Failed to install PRAW. Please check your Python and pip installations.
    exit /b 1
) else (
    echo PRAW installed successfully.
)

:: Run main.py
echo Running main.py...
python main.py

:: Pause the script to keep the window open
pause