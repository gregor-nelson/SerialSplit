# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python PyQt6 GUI application called "Serial Port Splitter" that provides a user-friendly interface for managing virtual serial ports using `com0com` and `hub4com`. The application allows users to create virtual serial port pairs and route data between multiple ports, serving as an alternative to commercial serial port splitting tools.

## Commands

### Running the Application
```bash
# Run the main application
python3 main.py
```

### Building Executable
```bash
# Build using PyInstaller (requires PyInstaller to be installed)
# Console version with admin privileges
pyinstaller Hub4comLauncher.spec

# GUI version with icon and UI assets
pyinstaller "Serial Port Splitter.spec"
```

## Architecture

### Core Components (`main.py`)
- **Entry Point**: `main.py` launches the PyQt6 GUI with system tray functionality
- **System Tray Integration**: The app minimizes to system tray instead of closing
- **Icon Generation**: Programmatically creates application icons

### Business Logic (`core/components.py`)
- **ResponsiveWindowManager**: Handles adaptive UI sizing
- **PortScanner**: Scans Windows registry for available serial ports, with special handling for Moxa devices
- **Hub4comProcess**: Manages the `hub4com.exe` subprocess for port routing
- **Com0comProcess**: Manages `com0com` `setupc.exe` commands for virtual port creation
- **Data Classes**: `SerialPortInfo`, `Com0comPortPair`, `PortConfig`, `WindowConfig`

### UI Layer
- **Main GUI** (`ui/gui.py`): Primary application interface with comprehensive port management
- **Dialogs** (`ui/dialogs/`): Modal dialogs for port scanning, pair creation, help, and configuration
- **Widgets** (`ui/widgets/`): Reusable UI components like output port widgets
- **Theming** (`ui/theme/`): Complete theming system with customizable colors, fonts, and styles

### Key Features
- Creates/removes `com0com` virtual port pairs (CNCA0/CNCB0, etc.)
- Routes data from one incoming port to multiple outgoing ports with different baud rates
- Windows registry-based port detection and classification
- CTS handshaking control and command preview functionality

## Dependencies

### Required
- **PyQt6**: GUI framework
- **winreg**: Windows Registry access (Windows only)
- **subprocess**: External executable management
- **pathlib**: Path handling

### External Executables
- **hub4com.exe**: Port routing utility (included in repo)
- **setupc.exe**: com0com setup utility (included in repo)

## Platform Requirements

This application is Windows-specific due to:
- Windows Registry scanning for port detection
- Integration with Windows-specific `com0com` and `hub4com` utilities
- System-level COM port management requiring Windows APIs

## File Structure Notes

- Binary executables (`.exe`, `.sys`, `.inf`, `.cat`) are Windows COM port drivers and utilities
- The application uses PyInstaller with UAC admin privileges (`uac_admin=True`)
- Custom Inter font files are included in `ui/fonts/` for consistent typography
- Two PyInstaller spec files: `Hub4comLauncher.spec` (console) and `Serial Port Splitter.spec` (GUI)
- No test files present - testing is manual through the GUI

## Development Notes

- Entry point includes system tray functionality and SVG icon generation
- UI components use a modular theming system with customizable colors and fonts
- Port detection relies on Windows Registry scanning with special Moxa device handling
- All subprocess management (hub4com.exe, setupc.exe) includes proper process lifecycle handling