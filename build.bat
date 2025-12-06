@echo off
REM EDUSCAN Quick Build Script for Windows
REM Run this file to build the Windows installer

cls
echo ============================================================
echo EDUSCAN Windows Installer Builder
echo ============================================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [WARNING] Virtual environment not found
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Create icon if missing
echo.
if not exist "assets\icon.ico" (
    echo Creating application icon...
    python create_icon.py
    if errorlevel 1 (
        echo Warning: Icon creation failed, continuing with default
    )
) else (
    echo [OK] Icon found
)
echo.
echo.
echo Installing build dependencies...
pip install -q --upgrade pip
pip install -q PyInstaller
pip install -q -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Run build script
echo ============================================================
echo Starting build process...
echo ============================================================
echo.

python quick_build.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [SUCCESS] Build completed!
echo ============================================================
echo.
echo Files created in dist/ folder:
echo   - EDUSCAN-Portable.zip
echo   - EDUSCAN\EDUSCAN.exe
echo.
echo You can now share these files or create an installer with NSIS.
echo.
pause
