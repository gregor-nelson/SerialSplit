# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Serial Port Splitter is a Python GUI application that provides a user-friendly interface for managing virtual serial ports using `com0com` and `hub4com`. It allows users to create virtual serial port pairs and route data between multiple ports, offering functionality similar to commercial serial port splitters.

## Application Architecture

### Core Components (core/components.py)
- **ResponsiveWindowManager**: Handles adaptive UI sizing for different screen sizes
- **PortScanner**: Scans Windows registry for serial ports and classifies them (Physical, Virtual COM0COM, Virtual Moxa, etc.)
- **Hub4comProcess**: Manages the `hub4com.exe` subprocess for port routing
- **Com0comProcess**: Manages `com0com` `setupc.exe` commands for virtual port pair management
- **DefaultConfig**: Defines default virtual port pairs (COM131/132, COM141/142) with baud rate timing

### UI Architecture
- **main.py**: Application entry point with PyQt6 GUI and system tray functionality
- **ui/gui.py**: Main GUI window (Hub4comGUI class) with comprehensive port management interface
- **ui/dialogs/**: Modal dialogs for port scanning, pair creation, configuration summary, launch options, and help
- **ui/widgets/**: Reusable components like OutputPortWidget for port configuration
- **ui/theme/**: Comprehensive theming system with colors, fonts, dimensions, and icon management
- **ui/windows/**: Command formatting and output log formatting utilities

## Running the Application

```bash
# Run the main application
python main.py
```

## Building Executables

The project uses PyInstaller for creating standalone executables:

```bash
# Build with PyInstaller using spec files
pyinstaller "Serial Port Splitter.spec"
pyinstaller "Hub4comLauncher.spec"
```

## Dependencies

- **PyQt6**: GUI framework with SVG support (PyQt6-Svg)
- **winreg**: Windows Registry access for port detection
- **subprocess**: Managing external executables (hub4com.exe, setupc.exe)

## Key Features Implementation

### Virtual Port Management
- Creates/removes com0com virtual port pairs via setupc.exe commands
- Default pairs: CNCA31/CNCB31 (COM131/132) and CNCA41/CNCB41 (COM141/142)
- Automatic pair creation with baud rate timing emulation enabled

### Port Detection & Classification
- Registry scanning to detect all serial ports
- Classifies ports as Physical, Virtual (COM0COM), Virtual (Moxa), or Virtual (Other)
- Special handling for Moxa RealCOM virtual ports with network connectivity recommendations

### Hub4com Integration
- Command line generation for hub4com.exe routing
- Support for different baud rates per port
- CTS handshaking control options
- Real-time process output monitoring

## File Structure Notes

- Batch files (*.bat) provide command-line alternatives for com2tcp operations
- Build artifacts are stored in build/ directory
- UI fonts directory contains Inter and Poppins font families
- System tray functionality with application minimize-to-tray behavior
- Built-in SVG icon rendering for high-quality application icons

## Development Notes

- The application requires Windows for com0com and hub4com integration
- Registry access requires appropriate Windows permissions
- PyInstaller builds require UAC admin privileges (uac_admin=True in spec files)
- Theme system supports adaptive font sizing and responsive layouts for different screen sizes