#!/usr/bin/env python3
"""
Core components for Hub4com GUI Launcher
Contains data classes, managers, and worker threads
"""

import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional

# Try to import winreg, fallback gracefully if not available
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False
    print("Warning: winreg module not available. Port scanning will be limited.")

from PyQt6.QtCore import QThread, pyqtSignal
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
        elif any(pattern in device_name.lower() for pattern in ["vspe", "virtual", "vspd"]):
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
    
    def __init__(self, command_args):
        super().__init__()
        self.setupc_path = r"C:\Program Files (x86)\com0com\setupc.exe"
        self.command_args = command_args
        
    def run(self):
        try:
            # Build full command
            cmd = [self.setupc_path] + self.command_args
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            self.command_completed.emit(success, output)
            
        except subprocess.TimeoutExpired:
            self.command_completed.emit(False, "Command timed out")
        except FileNotFoundError:
            self.command_completed.emit(False, f"setupc.exe not found at {self.setupc_path}")
        except Exception as e:
            self.command_completed.emit(False, f"Error: {str(e)}")