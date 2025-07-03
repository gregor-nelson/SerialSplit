# Serial Port Splitter

![Git Screenshot](https://github.com/user-attachments/assets/6c6aea1b-2b3d-4ad0-81f4-0a9b8f3df953)

This Python GUI application provides a user-friendly interface for managing virtual serial ports using `com0com` and `hub4com`. The application allows users to create virtual serial port pairs and route data between multiple ports. It is designed to offer similar functionality to commercial products like FabulaTech's Serial Port Splitter, which allows sharing of a single serial port among multiple applications by creating virtual COM ports.

## Key Features

### Virtual Port Management

* **Create and remove `com0com` virtual port pairs**: The application can create virtual serial port pairs such as `CNCA0`/`CNCB0`, `CNCA1`/`CNCB1`, etc.
* **Real-time port pair listing and status monitoring**: Users can view the status of all created virtual port pairs.

### Port Routing with `hub4com`

* **Data Routing**: Route data from one incoming port to multiple outgoing ports.
* **Differing Baud Rates**: Supports different baud rates for each port.
* **Handshake Control**: Offers CTS handshaking control.
* **Command Preview**: Allows users to preview the command before starting the `hub4com` process.

### Port Detection

* **Windows Registry Scanning**: The application scans the Windows registry to detect all available serial ports.
* **Port Classification**: It can classify ports as either physical or virtual.

## Architecture

### Core Components

* **`main.py`**: The application's entry point, which launches the PyQt6 GUI.
* **`core/components.py`**: Contains the core business logic, including:
    * `ResponsiveWindowManager`: Manages the adaptive UI sizing.
    * `PortScanner`: Scans the Windows registry for available serial ports.
    * `Hub4comProcess`: Manages the `hub4com.exe` subprocess.
    * `Com0comProcess`: Manages `com0com` `setupc.exe` commands.
    * Data classes for port configuration and window management.

### UI Layer

* **`ui/gui.py`**: The main GUI window that provides a comprehensive interface for port management.
* **`ui/dialogs/`**: Contains modal dialogs for port scanning, pair creation, and help.
* **`ui/widgets/`**: Includes reusable UI components like output port widgets.
* **`ui/theme/`**: A theming system with customizable colors, fonts, and styles.

## Dependencies

* **PyQt6**: Used for the GUI framework.
* **`winreg`**: The `winreg` module is used for port detection via Windows Registry access.
* **`subprocess`**: This module is used to manage external executables like `hub4com.exe` and `setupc.exe`.

## Running the Application

```bash
# Run the main application
python3 main.py
