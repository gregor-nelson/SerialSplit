@echo off
REM Build script for Serial Terminal application using PyInstaller

echo Building Serial Terminal...

REM Navigate to project root (one level up from scripts folder)
cd /d "%~dp0.."

REM Run PyInstaller command
powershell -Command "pyinstaller --onefile --windowed --name 'Serial Terminal' --icon 'assets/terminal_icon.ico' terminal_main.py"

echo.
if %ERRORLEVEL% EQU 0 (
    echo Build successful!
    echo Executable created in: dist\Serial Terminal.exe
) else (
    echo Build failed with error code: %ERRORLEVEL%
)

pause