# Serial Port Splitter

<img width="1366" height="736" alt="serialsplit_screen_01" src="https://github.com/user-attachments/assets/df9b9883-4624-4aae-bc99-fd63e6d38b30" />

<img width="1356" height="732" alt="serialsplit_screen_02" src="https://github.com/user-attachments/assets/8ee71ca9-708f-41b1-a143-f765c842f9ac" />

A Python based PyQt6 GUI application for managing virtual serial ports using `com0com` and `hub4com`. This application provides a interface for creating virtual serial port pairs and routing data between multiple ports, offering similar functionality to commercial products like FabulaTech's Serial Port Splitter.

## Key Features

### Virtual Port Management
- **Automated Setup**: Creates default virtual port pairs (COM131↔COM132, COM141↔COM142) with optimized settings
- **Advanced Configuration**: Baud rate timing emulation and buffer overrun protection
- **Real-time Monitoring**: Live port status and data flow statistics
- **Registry Integration**: Automatic detection of all system serial ports

### Port Routing & Splitting
- **Multi-Port Routing**: Route data from one incoming port to multiple outgoing ports
- **Flexible Baud Rates**: Different baud rates for each port connection
- **Handshake Control**: CTS handshaking and flow control options
- **Command Preview**: Review hub4com commands before execution
- 
### Port Detection & Testing
- **Smart Classification**: Distinguishes between physical, virtual, and Moxa ports
- **Port Testing**: Comprehensive port diagnostics and parameter detection
- **Real-time Statistics**: Monitor RX/TX rates, byte counts, and error rates

## Installation & Setup

### Required External Tools
- **com0com**: Virtual serial port driver (auto-detected at `C:\Program Files (x86)\com0com\setupc.exe`)
- **hub4com**: Serial port routing utility (bundled with application)

## Usage

### Build Executable
```bash
pyinstaller "Serial Port Splitter.spec"
```

### Default Configuration
The application automatically creates optimized virtual port pairs:
- **CNCA31 ↔ CNCB31** (COM131 ↔ COM132)
- **CNCA41 ↔ CNCB41** (COM141 ↔ COM142)

Both pairs include:
- Baud rate timing emulation (`EmuBR=yes`)
- Buffer overrun protection (`EmuOverrun=yes`)
- Default baud rate: 115200

## Architecture

### Core Components
- **`main.py`**: Entry point with system tray integration
- **`core/core.py`**: Logic layer with threading support
  - `ResponsiveWindowManager`: Adaptive UI sizing
  - `PortScanner`: Windows registry-based port detection
  - `Hub4comProcess`: Subprocess management for hub4com
  - `Com0comProcess`: Virtual port pair management
  - `SerialPortMonitor`: Real-time port monitoring

### UI Structure
- **`ui/gui.py`**: Main application window
- **`ui/dialogs/`**: Modal dialogs (port scanning, configuration, help)
- **`ui/widgets/`**: Reusable components (port widgets, tabs, monitoring)
- **`ui/theme/`**: Dark theme system with SVG icon management

## Technical Features

### Cross-Platform Considerations
- Windows-specific features with graceful degradation
- Registry scanning with fallback mechanisms
- Optional dependency handling (pyserial, winreg)

### Performance Optimizations
- Threaded operations for non-blocking UI
- Efficient port scanning and monitoring
- Responsive design with adaptive layouts

### Error Handling
- Comprehensive error reporting
- Timeout handling for subprocess operations
- Graceful fallback when dependencies unavailable

## Use Cases

- **Development**: Test serial applications with multiple virtual ports
- **Industrial**: Route data between different baud rate devices
- **Networking**: Interface with Moxa device servers
- **Testing**: Monitor and log serial communication
- **Integration**: Bridge applications that need shared serial access
