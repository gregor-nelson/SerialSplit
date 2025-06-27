Serial Port Splitter
This Python GUI application provides a user-friendly interface for managing virtual serial ports using COM0COM and HUB4COM. The application allows users to create virtual serial port pairs and route data between multiple ports. It is designed to offer similar functionality to commercial products like FabulaTech's Serial Port Splitter, which allows sharing of a single serial port among multiple applications by creating virtual COM ports.

Key Features
Virtual Port Management
Create and remove COM0COM virtual port pairs: The application can create virtual serial port pairs such as CNCA0/CNCB0, CNCA1/CNCB1, etc.

Real-time port pair listing and status monitoring: Users can view the status of all created virtual port pairs.

Port Routing with HUB4COM
Data Routing: Route data from one incoming port to multiple outgoing ports.

Differing Baud Rates: Supports different baud rates for each port.

Handshake Control: Offers CTS handshaking control.

Command Preview: Allows users to preview the command before starting the hub4com process.

Port Detection
Windows Registry Scanning: The application scans the Windows registry to detect all available serial ports.

Port Classification: It can classify ports as either physical or virtual.

Architecture
Core Components
main.py: The application's entry point, which launches the PyQt6 GUI.

core/components.py: Contains the core business logic, including:

ResponsiveWindowManager: Manages the adaptive UI sizing.

PortScanner: Scans the Windows registry for available serial ports.

Hub4comProcess: Manages the hub4com.exe subprocess.

Com0comProcess: Manages com0com setupc.exe commands.

Data classes for port configuration and window management.

UI Layer
ui/gui.py: The main GUI window that provides a comprehensive interface for port management.

ui/dialogs/: Contains modal dialogs for port scanning, pair creation, and help.

ui/widgets/: Includes reusable UI components like output port widgets.

ui/theme/: A theming system with customizable colors, fonts, and styles.

Dependencies
PyQt6: Used for the GUI framework.

winreg: The winreg module is used for port detection via Windows Registry access.

subprocess: This module is used to manage external executables like hub4com.exe and setupc.exe.

Running the Application
Bash

# Run the main application
python3 main.py
Common Workflows
Creating Virtual Port Pairs
Click the "Create New Pair" button in the Virtual Ports section.

The created ports will appear in the list as CNCA0/CNCB0, CNCA1/CNCB1, and so on.

Setting up Port Routing
Select an incoming port from the list of scanned devices.

Add output ports using the "Add Output Port" button.

Configure the baud rates, which can be different for each port.

Preview the generated command before initiating hub4com.

Troubleshooting
Use the "Scan Ports" feature for a detailed analysis of the ports.

Check the Windows Device Manager for any port conflicts.

Ensure that the COM0COM driver is properly installed.

Development Notes
Windows-Specific Implementation
The application uses the Windows Registry key HKEY_LOCAL_MACHINE\HARDWARE\DEVICEMAP\SERIALCOMM for port detection.

It integrates with the Windows COM0COM driver and the HUB4COM utility.

It handles Windows-specific port naming conventions (e.g., \\.\COMx).

GUI Architecture
The application features a responsive design that adapts to various screen sizes.

Port scanning and subprocess management are handled in separate threads to maintain UI responsiveness.

It includes comprehensive error handling and provides user-friendly feedback.

External Dependencies
Requires the COM0COM driver to be installed.

Utilizes the hub4com.exe and setupc.exe executables.

The application is designed to fall back gracefully if Windows Registry access is unavailable.
