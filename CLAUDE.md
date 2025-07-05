# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

SerialSplit is a Python PyQt6 GUI application for managing virtual serial ports using `com0com` and `hub4com`. It provides a user-friendly interface for creating virtual serial port pairs and routing data between multiple ports, similar to commercial products like FabulaTech's Serial Port Splitter.

## Key Commands

### Running the Application
```bash
# Run the main application
python main.py
```

### Building Executable
```bash
# Build Windows executable using PyInstaller
pyinstaller "Serial Port Splitter.spec"
```

The application uses PyInstaller with the following configuration:
- Entry point: `main.py`
- Includes UI assets from `ui/` directory
- Admin privileges required (`uac_admin=True`)
- Windows GUI application (no console)
- Uses `icon.ico` for application icon

## Architecture

### Core Components

**main.py** - Application entry point that:
- Initializes PyQt6 application with dark theme
- Creates system tray functionality
- Embeds SVG icon data directly in code
- Manages application lifecycle

**core/core.py** - Business logic layer containing:
- `ResponsiveWindowManager`: Adaptive UI sizing for different screen sizes
- `PortScanner`: Windows registry scanner for serial port detection
- `Hub4comProcess`: Manages `hub4com.exe` subprocess execution
- `Com0comProcess`: Manages `com0com` setupc.exe commands for virtual port creation
- `SerialPortMonitor`: Real-time port monitoring with statistics
- `SerialPortTester`: Port testing and diagnostics
- Data classes for port configuration and window management

### UI Layer Structure

**ui/gui.py** - Main GUI window with comprehensive port management interface

**ui/dialogs/** - Modal dialogs:
- `PortScanDialog`: Registry-based port scanning
- `PairCreationDialog`: Virtual port pair creation
- `ConfigurationSummaryDialog`: Configuration overview
- `LaunchDialog`: Application startup dialog
- `HelpDialog`: Contextual help system

**ui/widgets/** - Reusable UI components:
- `OutputPortWidget`: Individual port configuration
- `TabManagerWidget`: Serial port management tabs
- `PortTestWidget`: Port testing functionality
- `PortMonitorWidget`: Real-time monitoring display

**ui/theme/** - Theming system:
- `ThemeManager`: Global dark theme management
- `AppStyles`, `AppFonts`, `AppDimensions`, `AppColors`: Style constants
- `IconManager`: SVG icon management
- `ui/theme/icons/icons.py`: SVG icon definitions

**ui/windows/** - Window utilities:
- `CommandFormatter`: Hub4com command formatting
- `OutputFormatter`: Process output formatting

### Key Dependencies

The application requires:
- **PyQt6**: GUI framework
- **PyQt6-SVG**: SVG rendering support
- **winreg**: Windows registry access (Windows only)
- **pyserial**: Serial port communication (optional for monitoring)
- **subprocess**: External process management

### External Tools Integration

The application integrates with:
- **com0com**: Virtual serial port driver (`setupc.exe`)
- **hub4com**: Serial port routing utility (`hub4com.exe`)

Default installation paths:
- com0com: `C:\Program Files (x86)\com0com\setupc.exe`
- hub4com: `hub4com.exe` (bundled with application)

### Default Configuration

The application automatically creates default virtual port pairs:
- CNCA31 <-> CNCB31 (COM131 <-> COM132)
- CNCA41 <-> CNCB41 (COM141 <-> COM142)

Both pairs are configured with:
- Baud rate timing emulation (`EmuBR=yes`)
- Buffer overrun protection (`EmuOverrun=yes`)
- Default baud rate: 115200

### Cross-Platform Considerations

- Windows-specific features: Registry scanning, com0com integration
- Graceful degradation on non-Windows platforms
- Font loading uses system fonts as fallback
- Responsive design adapts to different screen sizes

## Development Notes

### Code Style
- Uses dataclasses for configuration objects
- Implements PyQt6 threading for non-blocking operations
- Follows PyQt6 signal/slot pattern for event handling
- Uses pathlib for file path management

### Error Handling
- Graceful fallback when optional dependencies unavailable
- Comprehensive error reporting for serial port operations
- Timeout handling for subprocess operations
- Registry access error handling

### UI Responsiveness
- Small screen detection and adaptive sizing
- Threaded operations for port scanning and process management
- Real-time status updates via Qt signals
- System tray integration for background operation