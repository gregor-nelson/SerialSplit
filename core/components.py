#!/usr/bin/env python3
"""
Core components for Hub4com GUI Launcher
Contains data classes, managers, and worker threads
"""

import subprocess
import time
import threading
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Try to import winreg, fallback gracefully if not available
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False
    print("Warning: winreg module not available. Port scanning will be limited.")

# Try to import serial, fallback gracefully if not available
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: pyserial module not available. Port monitoring will be disabled.")

from PyQt6.QtCore import QThread, pyqtSignal, QSettings
from PyQt6.QtWidgets import QApplication


@dataclass
class WindowConfig:
    """Configuration for window sizing and layout"""
    width: int
    height: int
    x: int
    y: int
    is_small_screen: bool
    min_width: int = 800
    min_height: int = 600


@dataclass
class SerialPortInfo:
    """Information about a detected serial port"""
    port_name: str
    device_name: str
    port_type: str  # 'Physical', 'Virtual (Moxa)', 'Virtual (Other)'
    registry_key: str
    description: str = ""
    is_moxa: bool = False
    moxa_details: Optional[Dict] = None


@dataclass
class Com0comPortPair:
    """Information about a com0com virtual port pair"""
    port_a: str  # e.g., "CNCA0"
    port_b: str  # e.g., "CNCB0"
    port_a_params: Dict[str, str]  # Parameters like PortName, EmuBR, etc.
    port_b_params: Dict[str, str]


class SettingsManager:
    """Manages application settings using QSettings for cross-platform persistence"""
    
    def __init__(self):
        self.settings = QSettings("SerialSplit", "Hub4com")
    
    def get_show_launch_dialog(self):
        """Get whether to show launch dialog on startup (default: True)"""
        return self.settings.value("ui/show_launch_dialog", True, type=bool)
    
    def set_show_launch_dialog(self, show_dialog):
        """Set whether to show launch dialog on startup"""
        self.settings.setValue("ui/show_launch_dialog", show_dialog)
        self.settings.sync()


class DefaultConfig:
    """Default COM pairs and settings to create on application launch"""
    # Default pairs to create: CNCA31<->CNCB31 (COM131<->COM132) and CNCA41<->CNCB41 (COM141<->COM142)
    default_pairs = [
        {"port_a": "CNCA31", "port_b": "CNCB31", "com_a": "COM131", "com_b": "COM132"},
        {"port_a": "CNCA41", "port_b": "CNCB41", "com_a": "COM141", "com_b": "COM142"}
    ]
    default_baud = "115200"
    # Settings for each port in the pair
    default_settings = {
        "EmuBR": "yes",        # Baud rate timing emulation
        "EmuOverrun": "yes"    # Buffer overrun emulation
    }
    # Output port mapping for GUI pre-population
    output_mapping = [
        {"port": "COM131", "baud": "115200"},
        {"port": "COM141", "baud": "115200"}
    ]


class ResponsiveWindowManager:
    """Manages responsive window sizing and layout decisions"""
    
    SMALL_SCREEN_WIDTH_THRESHOLD = 1024
    SMALL_SCREEN_HEIGHT_THRESHOLD = 768
    SMALL_SCREEN_WIDTH_RATIO = 0.95
    SMALL_SCREEN_HEIGHT_RATIO = 0.90
    LARGE_SCREEN_DEFAULT_WIDTH = 1200
    LARGE_SCREEN_DEFAULT_HEIGHT = 900
    ABSOLUTE_MIN_WIDTH = 800
    ABSOLUTE_MIN_HEIGHT = 600
    
    @classmethod
    def get_screen_info(cls):
        """Get primary screen geometry information"""
        screen = QApplication.primaryScreen()
        if not screen:
            # Fallback if no screen detected
            return 1024, 768, 0, 0
        
        screen_geometry = screen.availableGeometry()
        return (
            screen_geometry.width(),
            screen_geometry.height(),
            screen_geometry.x(),
            screen_geometry.y()
        )
    
    @classmethod
    def is_small_screen(cls, screen_width: int, screen_height: int) -> bool:
        """Determine if screen should be considered small"""
        return (screen_width < cls.SMALL_SCREEN_WIDTH_THRESHOLD or 
                screen_height < cls.SMALL_SCREEN_HEIGHT_THRESHOLD)
    
    @classmethod
    def calculate_main_window_config(cls) -> WindowConfig:
        """Calculate optimal window configuration for main application window"""
        screen_width, screen_height, screen_x, screen_y = cls.get_screen_info()
        is_small = cls.is_small_screen(screen_width, screen_height)
        
        if is_small:
            # Small screen: use most of available space with minimum constraints
            window_width = min(
                max(screen_width * cls.SMALL_SCREEN_WIDTH_RATIO, cls.ABSOLUTE_MIN_WIDTH),
                screen_width
            )
            window_height = min(
                max(screen_height * cls.SMALL_SCREEN_HEIGHT_RATIO, cls.ABSOLUTE_MIN_HEIGHT),
                screen_height
            )
            
            # Center on screen
            x = screen_x + (screen_width - window_width) // 2
            y = screen_y + (screen_height - window_height) // 2
        else:
            # Large screen: use comfortable default size
            window_width = cls.LARGE_SCREEN_DEFAULT_WIDTH
            window_height = cls.LARGE_SCREEN_DEFAULT_HEIGHT
            x = screen_x + 100
            y = screen_y + 100
        
        return WindowConfig(
            width=int(window_width),
            height=int(window_height),
            x=int(x),
            y=int(y),
            is_small_screen=is_small,
            min_width=cls.ABSOLUTE_MIN_WIDTH,
            min_height=cls.ABSOLUTE_MIN_HEIGHT
        )
    
    @classmethod
    def calculate_dialog_config(cls, preferred_width: int = 800, preferred_height: int = 500) -> WindowConfig:
        """Calculate optimal window configuration for dialog windows"""
        screen_width, screen_height, screen_x, screen_y = cls.get_screen_info()
        is_small = cls.is_small_screen(screen_width, screen_height)
        
        if is_small:
            # Small screen: use most of available space
            window_width = min(screen_width * 0.9, preferred_width)
            window_height = min(screen_height * 0.8, preferred_height)
            min_width = 600
            min_height = 400
        else:
            # Large screen: use preferred size
            window_width = preferred_width
            window_height = preferred_height
            min_width = preferred_width // 2
            min_height = preferred_height // 2
        
        # Center the dialog
        x = screen_x + (screen_width - window_width) // 2
        y = screen_y + (screen_height - window_height) // 2
        
        return WindowConfig(
            width=int(window_width),
            height=int(window_height),
            x=int(x),
            y=int(y),
            is_small_screen=is_small,
            min_width=min_width,
            min_height=min_height
        )
    
    @classmethod
    def get_adaptive_font_size(cls, base_size: int, is_small_screen: bool) -> int:
        """Get adaptive font size based on screen size"""
        if is_small_screen:
            return max(base_size - 2, 10)  # Reduce by 2, minimum 10
        return base_size
    
    @classmethod
    def get_adaptive_button_size(cls, is_small_screen: bool) -> tuple:
        """Get adaptive button dimensions (width, height)"""
        if is_small_screen:
            return (60, 30)
        return (70, None)  # None means no height restriction
    
    @classmethod
    def get_adaptive_text_height(cls, base_height: int, is_small_screen: bool) -> dict:
        """Get adaptive text widget height configuration"""
        if is_small_screen:
            return {
                'min_height': max(base_height - 50, 100),
                'max_height': base_height
            }
        return {
            'min_height': base_height,
            'max_height': None
        }


class PortScanner(QThread):
    """Thread for scanning Windows registry for serial ports"""
    scan_completed = pyqtSignal(list)
    scan_progress = pyqtSignal(str)
    
    def run(self):
        try:
            self.scan_progress.emit("Scanning Windows registry...")
            ports = self.scan_registry_ports()
            self.scan_completed.emit(ports)
        except Exception as e:
            self.scan_progress.emit(f"Error scanning ports: {str(e)}")
            # Return empty list on error rather than crashing
            self.scan_completed.emit([])
    
    def scan_registry_ports(self) -> List[SerialPortInfo]:
        """Scan Windows registry for all serial ports"""
        ports = []
        
        if not WINREG_AVAILABLE:
            raise Exception("Windows registry access not available")
        
        try:
            # Check if winreg is available and working
            if not hasattr(winreg, 'OpenKey'):
                raise ImportError("winreg module not properly available")
                
            # Open the SERIALCOMM registry key
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
            
            # Enumerate all values
            i = 0
            while i < 256:  # Reasonable limit to prevent infinite loops
                try:
                    device_name, port_name, _ = winreg.EnumValue(key, i)
                    
                    # Classify the port type
                    port_info = self.classify_port(device_name, port_name)
                    ports.append(port_info)
                    
                    i += 1
                except OSError:
                    # No more values
                    break
                except Exception as e:
                    # Skip this value and continue
                    i += 1
                    continue
            
            winreg.CloseKey(key)
            
        except FileNotFoundError:
            # Registry key doesn't exist - this is normal on some systems
            pass
        except ImportError:
            # winreg not available - fallback
            raise Exception("Windows registry access not available")
        except Exception as e:
            # Other registry errors
            raise Exception(f"Registry scan failed: {str(e)}")
        
        # Sort ports by port name
        ports.sort(key=lambda p: self.port_sort_key(p.port_name))
        return ports
    
    def classify_port(self, device_name: str, port_name: str) -> SerialPortInfo:
        """Classify a port based on its registry device name"""
        
        # Check for Moxa devices (Npdrv pattern)
        if device_name.startswith("Npdrv"):
            moxa_details = self.parse_moxa_device(device_name, port_name)
            return SerialPortInfo(
                port_name=port_name,
                device_name=device_name,
                port_type="Virtual (Moxa)",
                registry_key=device_name,
                description=f"Moxa RealCOM virtual port",
                is_moxa=True,
                moxa_details=moxa_details
            )
        
        # Check for COM0COM devices
        elif "CNCB" in device_name or "CNCA" in device_name:
            return SerialPortInfo(
                port_name=port_name,
                device_name=device_name,
                port_type="Virtual (COM0COM)",
                registry_key=device_name,
                description="COM0COM virtual null-modem pair"
            )
        
        # Check for other virtual port patterns
        elif any(pattern in device_name.lower() for pattern in ["com0com", "virtual", "vspd"]):
            return SerialPortInfo(
                port_name=port_name,
                device_name=device_name,
                port_type="Virtual (Other)",
                registry_key=device_name,
                description="Virtual serial port"
            )
        
        # Physical ports (USB, PCI, etc.)
        else:
            return SerialPortInfo(
                port_name=port_name,
                device_name=device_name,
                port_type="Physical",
                registry_key=device_name,
                description="Physical serial port"
            )
    
    def parse_moxa_device(self, device_name: str, port_name: str) -> Dict:
        """Parse Moxa-specific device information"""
        details = {
            "driver_name": device_name,
            "port_number": port_name.replace("COM", ""),
            "connection_type": "Virtual/Network",
            "recommendations": [
                "Disable CTS handshaking for network serial servers",
                "Check network connectivity to Moxa device",
                "Verify Moxa driver configuration",
                "Consider matching baud rate to source device"
            ]
        }
        return details
    
    def port_sort_key(self, port_name: str) -> tuple:
        """Generate sort key for port names"""
        # Extract number from COM port name for proper sorting
        try:
            if port_name.startswith("COM"):
                num = int(port_name[3:])
                return (0, num)  # COM ports first
            else:
                return (1, port_name)  # Other ports second
        except:
            return (2, port_name)  # Fallback
    


class PortConfig:
    """Configuration for a single port"""
    def __init__(self, port_name="", baud_rate="115200"):
        self.port_name = port_name
        self.baud_rate = baud_rate


class Hub4comProcess(QThread):
    """Thread to run hub4com process"""
    output_received = pyqtSignal(str)
    process_started = pyqtSignal()
    process_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None
        self.should_stop = False
    
    def run(self):
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait a moment to check if process starts successfully
            import time
            time.sleep(1)
            
            if self.process.poll() is not None:
                # Process terminated immediately
                output, _ = self.process.communicate()
                self.error_occurred.emit(f"hub4com exited immediately:\n{output}")
                return
            
            self.process_started.emit()
            
            # Read output line by line
            while self.process.poll() is None and not self.should_stop:
                try:
                    line = self.process.stdout.readline()
                    if line:
                        self.output_received.emit(line.strip())
                except:
                    break
            
            self.process_stopped.emit()
            
        except FileNotFoundError:
            self.error_occurred.emit(f"Could not find hub4com.exe at: {self.command[0]}")
        except Exception as e:
            self.error_occurred.emit(f"Failed to start hub4com: {str(e)}")
    
    def stop_process(self):
        self.should_stop = True
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()


class Com0comProcess(QThread):
    """Thread to execute com0com setupc commands"""
    command_completed = pyqtSignal(bool, str)  # success, output
    command_output = pyqtSignal(str)
    pairs_checked = pyqtSignal(list)  # Emitted with existing pairs list
    
    def __init__(self, command_args, operation_type="command"):
        super().__init__()
        self.setupc_path = r"C:\Program Files (x86)\com0com\setupc.exe"
        self.command_args = command_args
        self.operation_type = operation_type  # "command", "list", "create_default", "check_and_create_default"
        
    def run(self):
        try:
            if self.operation_type == "create_default":
                self._create_default_pairs()
            elif self.operation_type == "check_and_create_default":
                self._check_and_create_default_pairs()
            elif self.operation_type == "list":
                self._list_existing_pairs()
            else:
                self._execute_command()
                
        except subprocess.TimeoutExpired:
            self.command_completed.emit(False, "Command timed out")
        except FileNotFoundError:
            self.command_completed.emit(False, f"setupc.exe not found at {self.setupc_path}")
        except Exception as e:
            self.command_completed.emit(False, f"Error: {str(e)}")
    
    def _execute_command(self):
        """Execute a standard setupc command"""
        cmd = [self.setupc_path] + self.command_args
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        self.command_completed.emit(success, output)
    
    def _list_existing_pairs(self):
        """List existing COM0COM pairs"""
        cmd = [self.setupc_path, "list"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            existing_pairs = self._parse_pairs_output(result.stdout)
            self.pairs_checked.emit(existing_pairs)
        else:
            self.pairs_checked.emit([])
    
    def _create_default_pairs(self):
        """Create default COM pairs if they don't exist"""
        # First, list existing pairs
        list_cmd = [self.setupc_path, "list"]
        list_result = subprocess.run(
            list_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        existing_pairs = []
        if list_result.returncode == 0:
            existing_pairs = self._parse_pairs_output(list_result.stdout)
        
        # Check which default pairs need to be created
        default_config = DefaultConfig()
        created_pairs = []
        
        for pair_config in default_config.default_pairs:
            port_a, port_b = pair_config["port_a"], pair_config["port_b"]
            com_a, com_b = pair_config["com_a"], pair_config["com_b"]
            
            # Check if this pair already exists
            pair_exists = any(
                (p.get("port_a") == port_a and p.get("port_b") == port_b) or
                (p.get("com_a") == com_a and p.get("com_b") == com_b)
                for p in existing_pairs
            )
            
            if not pair_exists:
                # Create the pair with specific settings
                create_cmd = [
                    self.setupc_path, "install",
                    f"PortName={com_a},EmuBR=yes,EmuOverrun=yes",
                    f"PortName={com_b},EmuBR=yes,EmuOverrun=yes"
                ]
                
                create_result = subprocess.run(
                    create_cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if create_result.returncode == 0:
                    created_pairs.append(f"{com_a}<->{com_b}")
        
        if created_pairs:
            success_msg = f"Successfully created virtual COM port pairs: {', '.join(created_pairs)} with baud rate timing and buffer overrun protection enabled"
            self.command_completed.emit(True, success_msg)
        else:
            self.command_completed.emit(True, "Virtual COM port pairs are already configured and ready for marine operations")
    
    def _parse_pairs_output(self, output: str) -> List[Dict]:
        """Parse setupc list output to extract existing pairs"""
        pairs = []
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if 'PortName=' in line:
                # Extract port information from setupc output
                # This is a simplified parser - may need refinement based on actual output format
                if 'COM' in line:
                    # Try to extract COM port number
                    import re
                    com_match = re.search(r'COM(\d+)', line)
                    if com_match:
                        com_num = com_match.group(1)
                        pairs.append({
                            "com_a": f"COM{com_num}",
                            "com_b": "",  # Would need to parse paired port
                            "port_a": "",
                            "port_b": "",
                            "raw_line": line
                        })
        
        return pairs
    
    def _parse_com0com_output(self, output: str) -> Dict:
        """Parse com0com list output to extract existing pairs"""
        pairs = {}
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('command>'):
                parts = line.split(None, 1)
                if len(parts) >= 1:
                    port = parts[0]
                    params = parts[1] if len(parts) > 1 else ""
                    
                    if port.startswith('CNCA'):
                        pair_num = port[4:]  # Extract number after "CNCA"
                        if pair_num not in pairs:
                            pairs[pair_num] = {}
                        pairs[pair_num]['A'] = (port, params)
                    elif port.startswith('CNCB'):
                        pair_num = port[4:]  # Extract number after "CNCB"
                        if pair_num not in pairs:
                            pairs[pair_num] = {}
                        pairs[pair_num]['B'] = (port, params)
        
        return pairs
    
    def _extract_actual_port_name(self, virtual_name: str, params: str) -> str:
        """Extract the actual COM port name from parameters"""
        if not params:
            return virtual_name
        
        if "RealPortName=" in params:
            real_name = params.split("RealPortName=")[1].split(",")[0]
            if real_name and real_name != "-":
                return real_name
        
        if "PortName=" in params:
            port_name = params.split("PortName=")[1].split(",")[0]
            if port_name and port_name not in ["-", "COM#"]:
                return port_name
        
        return virtual_name
    
    def _check_and_create_default_pairs(self):
        """Check which default pairs exist using setupc.exe list and only create missing ones"""
        try:
            # First, get existing pairs using setupc.exe list command
            list_cmd = [self.setupc_path, "list"]
            list_result = subprocess.run(
                list_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            existing_pairs_dict = {}
            existing_com_ports = set()
            
            if list_result.returncode == 0:
                # Parse the existing pairs
                parsed_pairs = self._parse_com0com_output(list_result.stdout)
                
                # Extract COM port names from existing pairs
                for pair_num, pair_data in parsed_pairs.items():
                    if 'A' in pair_data and 'B' in pair_data:
                        port_a, params_a = pair_data['A']
                        port_b, params_b = pair_data['B']
                        
                        # Get actual COM port names
                        com_a = self._extract_actual_port_name(port_a, params_a)
                        com_b = self._extract_actual_port_name(port_b, params_b)
                        
                        existing_com_ports.add(com_a)
                        existing_com_ports.add(com_b)
                        existing_pairs_dict[f"{com_a}<->{com_b}"] = True
            
            # Check which default pairs need to be created
            default_config = DefaultConfig()
            created_pairs = []
            existing_pairs = []
            
            for pair_config in default_config.default_pairs:
                com_a, com_b = pair_config["com_a"], pair_config["com_b"]
                pair_key = f"{com_a}<->{com_b}"
                
                # Check if both COM ports exist
                pair_exists = com_a in existing_com_ports and com_b in existing_com_ports
                
                if pair_exists:
                    existing_pairs.append(pair_key)
                else:
                    # Create the missing pair
                    create_cmd = [
                        self.setupc_path, "install",
                        f"PortName={com_a},EmuBR=yes,EmuOverrun=yes",
                        f"PortName={com_b},EmuBR=yes,EmuOverrun=yes"
                    ]
                    
                    create_result = subprocess.run(
                        create_cmd,
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    if create_result.returncode == 0:
                        created_pairs.append(pair_key)
            
            # Build status message
            messages = []
            if existing_pairs:
                messages.append(f"Found existing virtual COM port pairs: {', '.join(existing_pairs)}")
            if created_pairs:
                messages.append(f"Successfully created new virtual COM port pairs: {', '.join(created_pairs)} with baud rate timing and buffer overrun protection enabled")
            
            if messages:
                final_message = ". ".join(messages) + ". All virtual COM port pairs are now ready for marine operations."
            else:
                final_message = "Virtual COM port configuration completed successfully."
            
            self.command_completed.emit(True, final_message)
            
        except Exception as e:
            # Fallback to original behavior if detection fails
            self._create_default_pairs()


# ============================================================================
# SERIAL PORT MONITORING
# ============================================================================

class SerialPortMonitor(QThread):
    """
    Serial port monitoring class for real-time statistics and data flow observation.
    """
    # Signals
    stats_updated = pyqtSignal(dict)  # Emits updated port statistics
    data_received = pyqtSignal(bytes)  # Emits raw data received
    error_occurred = pyqtSignal(str)  # Emits error messages
    
    def __init__(self, port_name, baudrate=9600):
        """
        Initialize the serial port monitor.
        
        Args:
            port_name: Serial port name
            baudrate: Baud rate for monitoring
        """
        super().__init__()
        
        self.port_name = port_name
        self.baudrate = baudrate
        
        # Statistics
        self.stats = {
            "rx_bytes": 0,
            "tx_bytes": 0,
            "rx_rate": 0.0,  # bytes per second
            "tx_rate": 0.0,  # bytes per second
            "errors": 0,
            "start_time": None,
            "running_time": 0.0,
            "is_monitoring": False
        }
        
        # Rate calculation windows
        self.rx_window = []  # List of (timestamp, bytes) tuples
        self.tx_window = []  # List of (timestamp, bytes) tuples
        self.window_size = 2  # seconds for rate calculation
        
        # Operation flags
        self.monitoring = False
        self.ser = None
        
    def start_monitoring(self):
        """Start monitoring the serial port."""
        if not SERIAL_AVAILABLE:
            self.error_occurred.emit("pyserial module not available for port monitoring")
            return False
            
        if self.monitoring:
            return True
            
        try:
            # Reset stats
            self.stats = {
                "rx_bytes": 0,
                "tx_bytes": 0,
                "rx_rate": 0.0,
                "tx_rate": 0.0,
                "errors": 0,
                "start_time": datetime.now(),
                "running_time": 0.0,
                "is_monitoring": True
            }
            
            self.rx_window = []
            self.tx_window = []
            
            # Start the monitor thread
            self.monitoring = True
            self.start()
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error starting monitor for {self.port_name}: {str(e)}")
            self.monitoring = False
            return False
    
    def stop_monitoring(self):
        """Stop monitoring the serial port."""
        if not self.monitoring:
            return
            
        self.monitoring = False
        self.stats["is_monitoring"] = False
        
        # Wait for thread to exit
        if self.isRunning():
            self.wait(1000)
        
        # Close the port if open
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except:
                pass
    
    def run(self):
        """Main monitoring loop running in the thread."""
        last_stats_update = time.time()
        
        # Try to open port for monitoring (non-blocking)
        try:
            if SERIAL_AVAILABLE:
                self.ser = serial.Serial()
                self.ser.port = self.port_name
                self.ser.baudrate = self.baudrate
                self.ser.timeout = 0.1
                
                # Try to open the port with enhanced error handling
                try:
                    self.ser.open()
                except serial.SerialException as e:
                    # Provide specific error feedback for different scenarios
                    error_msg = str(e).lower()
                    if "access is denied" in error_msg or "permission denied" in error_msg:
                        self.error_occurred.emit(f"Port {self.port_name} is busy or in use by another application")
                    elif "could not open port" in error_msg:
                        if "moxa" in self.port_name.lower() or "mxser" in error_msg:
                            self.error_occurred.emit(f"Moxa port {self.port_name} network connection unavailable")
                        else:
                            self.error_occurred.emit(f"Port {self.port_name} could not be opened - device may be disconnected")
                    else:
                        self.error_occurred.emit(f"Port {self.port_name} monitoring unavailable: {str(e)}")
                    self.ser = None
                except Exception as e:
                    self.error_occurred.emit(f"Unexpected error opening {self.port_name}: {str(e)}")
                    self.ser = None
                    
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize monitoring for {self.port_name}: {str(e)}")
            self.ser = None
        
        while self.monitoring:
            try:
                # If we have an open serial port, monitor it
                if self.ser and self.ser.is_open:
                    # Check for incoming data
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting)
                        if data:
                            # Update statistics
                            self.stats["rx_bytes"] += len(data)
                            now = time.time()
                            self.rx_window.append((now, len(data)))
                            
                            # Emit the data
                            self.data_received.emit(data)
                
                # Update running time and rates periodically
                now = time.time()
                if now - last_stats_update >= 1.0:  # Update stats every second
                    self._update_rates(now)
                    if self.stats["start_time"]:
                        self.stats["running_time"] = (datetime.now() - self.stats["start_time"]).total_seconds()
                    
                    # Emit updated stats
                    self.stats_updated.emit(self.stats.copy())
                    last_stats_update = now
                
                # Short sleep to prevent CPU thrashing
                time.sleep(0.1)
                
            except Exception as e:
                self.stats["errors"] += 1
                self.error_occurred.emit(f"Monitor error: {str(e)}")
                time.sleep(0.5)  # Wait before retrying
        
        # Ensure port is closed on exit
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except:
                pass
    
    def _update_rates(self, now):
        """
        Update RX and TX rates based on windowed data.
        
        Args:
            now: Current timestamp
        """
        # Remove old data points outside the window
        window_start = now - self.window_size
        self.rx_window = [(ts, sz) for ts, sz in self.rx_window if ts >= window_start]
        self.tx_window = [(ts, sz) for ts, sz in self.tx_window if ts >= window_start]
        
        # Calculate rates
        if self.rx_window:
            total_rx_bytes = sum(sz for _, sz in self.rx_window)
            oldest_ts = min(ts for ts, _ in self.rx_window)
            if now > oldest_ts:
                time_span = now - oldest_ts
                self.stats["rx_rate"] = total_rx_bytes / time_span
            else:
                self.stats["rx_rate"] = 0.0
        else:
            self.stats["rx_rate"] = 0.0
        
        if self.tx_window:
            total_tx_bytes = sum(sz for _, sz in self.tx_window)
            oldest_ts = min(ts for ts, _ in self.tx_window)
            if now > oldest_ts:
                time_span = now - oldest_ts
                self.stats["tx_rate"] = total_tx_bytes / time_span
            else:
                self.stats["tx_rate"] = 0.0
        else:
            self.stats["tx_rate"] = 0.0
    
    def get_formatted_stats(self):
        """
        Get formatted statistics as a string.
        
        Returns:
            str: Formatted statistics string
        """
        if not self.stats["start_time"] or not self.stats["is_monitoring"]:
            return "Not monitoring"
            
        # Format rates
        rx_rate = self.stats["rx_rate"]
        tx_rate = self.stats["tx_rate"]
        
        # Choose appropriate units
        if rx_rate < 1024:
            rx_rate_str = f"{rx_rate:.1f} B/s"
        else:
            rx_rate_str = f"{rx_rate/1024:.1f} KB/s"
            
        if tx_rate < 1024:
            tx_rate_str = f"{tx_rate:.1f} B/s"
        else:
            tx_rate_str = f"{tx_rate/1024:.1f} KB/s"
            
        # Format running time
        seconds = int(self.stats["running_time"])
        running_time = str(timedelta(seconds=seconds))
        
        # Format the statistics string
        stats_str = f"Monitoring: {running_time}\n"
        stats_str += f"RX: {self.stats['rx_bytes']} bytes ({rx_rate_str})\n"
        stats_str += f"TX: {self.stats['tx_bytes']} bytes ({tx_rate_str})\n"
        stats_str += f"Errors: {self.stats['errors']}"
        
        return stats_str


class SerialPortTester:
    """
    Serial port testing functionality for parameter detection and diagnostics.
    """
    
    def __init__(self):
        """Initialize the port tester."""
        self.available = SERIAL_AVAILABLE
    
    def test_port(self, port_name: str) -> Dict:
        """
        Test a serial port and return comprehensive information.
        
        Args:
            port_name (str): Name of the serial port to test
            
        Returns:
            Dict: Dictionary containing test results and port information
        """
        if not self.available:
            return {
                "status": "Error",
                "message": "pyserial module not available",
                "details": {}
            }
        
        try:
            # Try to open the port with minimal configuration
            ser = serial.Serial(port_name, timeout=1)
            
            # Collect basic port information
            port_info = {
                "port": port_name,
                "bytesize": ser.bytesize,
                "parity": ser.parity,
                "stopbits": ser.stopbits,
                "timeout": ser.timeout,
                "xonxoff": ser.xonxoff,
                "rtscts": ser.rtscts,
                "dsrdtr": ser.dsrdtr,
                "write_timeout": getattr(ser, 'write_timeout', 'N/A'),
                "inter_byte_timeout": getattr(ser, 'inter_byte_timeout', 'N/A')
            }
            
            # Get modem status if available
            try:
                modem_status = {
                    "CTS": ser.cts if hasattr(ser, 'cts') else 'N/A',
                    "DSR": ser.dsr if hasattr(ser, 'dsr') else 'N/A',
                    "RI": ser.ri if hasattr(ser, 'ri') else 'N/A',
                    "CD": ser.cd if hasattr(ser, 'cd') else 'N/A'
                }
                port_info["modem_status"] = modem_status
            except Exception:
                port_info["modem_status"] = "Not available"
            
            # Get buffer information if available
            try:
                port_info["in_waiting"] = ser.in_waiting
                port_info["out_waiting"] = ser.out_waiting if hasattr(ser, 'out_waiting') else 'N/A'
            except Exception:
                port_info["in_waiting"] = 'N/A'
                port_info["out_waiting"] = 'N/A'
            
            # Close the port
            ser.close()
            
            return {
                "status": "Available",
                "message": f"Port {port_name} is available and ready",
                "details": port_info
            }
            
        except serial.SerialException as e:
            error_msg = str(e).lower()
            if "access is denied" in error_msg or "permission denied" in error_msg:
                status_msg = f"Port {port_name} is in use by another application"
            elif "file not found" in error_msg or "system cannot find" in error_msg:
                status_msg = f"Port {port_name} does not exist or is not available"
            else:
                status_msg = f"Port {port_name} has an error: {str(e)}"
            
            return {
                "status": "Error",
                "message": status_msg,
                "details": {"error": str(e)}
            }
        except Exception as e:
            return {
                "status": "Error", 
                "message": f"Unexpected error testing port {port_name}",
                "details": {"error": str(e)}
            }
    
    def format_test_results(self, test_results: Dict) -> str:
        """
        Format test results into a readable string.
        
        Args:
            test_results (Dict): Results from test_port()
            
        Returns:
            str: Formatted test results
        """
        if test_results["status"] == "Error":
            return f"{test_results['message']}\n\nError Details:\n{test_results['details'].get('error', 'Unknown error')}"
        
        details = test_results["details"]
        result = f"{test_results['message']}\n\n"
        
        # Basic port configuration
        result += "Port Configuration:\n"
        result += f"Data Bits: {details.get('bytesize', 'N/A')}\n"
        result += f"Parity: {details.get('parity', 'N/A')}\n"
        result += f"Stop Bits: {details.get('stopbits', 'N/A')}\n"
        result += f"Timeout: {details.get('timeout', 'N/A')}s\n\n"
        
        # Flow control
        result += "Flow Control:\n"
        result += f"XON/XOFF: {details.get('xonxoff', 'N/A')}\n"
        result += f"RTS/CTS: {details.get('rtscts', 'N/A')}\n"
        result += f"DSR/DTR: {details.get('dsrdtr', 'N/A')}\n\n"
        
        # Modem status
        if "modem_status" in details and isinstance(details["modem_status"], dict):
            result += "Modem Status:\n"
            for signal, value in details["modem_status"].items():
                result += f"  {signal}: {value}\n"
            result += "\n"
        
        # Buffer status
        if "in_waiting" in details:
            result += "Buffer Status:\n"
            result += f"Input Buffer: {details['in_waiting']} bytes\n"
            if details.get("out_waiting") != 'N/A':
                result += f"  Output Buffer: {details['out_waiting']} bytes\n"
            result += "\n"
        
        # Additional timeouts
        if details.get("write_timeout") != 'N/A' or details.get("inter_byte_timeout") != 'N/A':
            result += "Advanced Timeouts:\n"
            if details.get("write_timeout") != 'N/A':
                result += f"  Write Timeout: {details['write_timeout']}s\n"
            if details.get("inter_byte_timeout") != 'N/A':
                result += f"  Inter-byte Timeout: {details['inter_byte_timeout']}s\n"
        
        return result