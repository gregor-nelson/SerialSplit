#!/usr/bin/env python3
"""
Serial Port Test Widget - Comprehensive port testing and diagnostics
Provides visual testing results using SerialPortTester from core.py
"""

from typing import Optional, Dict

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSizePolicy, QScrollArea,
                             QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTransform

from core.core import SerialPortInfo, SerialPortTester
from ui.theme.theme import (
    ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts
)
from ui.theme.icons.icons import AppIcons
from ui.theme.theme import IconManager


class AnimatedSpinnerWidget(QLabel):
    """Animated spinner widget that rotates continuously"""
    
    def __init__(self, color: str, size: int = 18):
        super().__init__()
        self.color = color
        self.size = size
        self.rotation_angle = 0
        
        # Create the base icon without animation
        spinner_svg = f"""
        <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
            <circle cx="8" cy="8" r="6" 
                    fill="none" stroke="{color}" stroke-width="2" 
                    stroke-linecap="round" stroke-dasharray="28" 
                    stroke-dashoffset="28" opacity="0.3"/>
            <circle cx="8" cy="8" r="6" 
                    fill="none" stroke="{color}" stroke-width="2" 
                    stroke-linecap="round" stroke-dasharray="8" 
                    stroke-dashoffset="0"/>
        </svg>
        """
        
        self.base_icon = IconManager.create_svg_icon(
            spinner_svg,
            color,
            IconManager.get_scaled_size(size)
        )
        
        # Setup widget properties
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(24, 24)
        
        # Setup animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._rotate_icon)
        self.animation_timer.start(50)  # 50ms = 20 FPS
        
        # Initial render
        self._update_pixmap()
    
    def _rotate_icon(self):
        """Rotate the icon by 18 degrees (360/20 for smooth animation)"""
        self.rotation_angle = (self.rotation_angle + 18) % 360
        self._update_pixmap()
    
    def _update_pixmap(self):
        """Update the pixmap with rotation applied"""
        # Get the base pixmap
        base_pixmap = self.base_icon.pixmap(self.size, self.size)
        
        # Create transform for rotation
        transform = QTransform()
        transform.translate(self.size / 2, self.size / 2)
        transform.rotate(self.rotation_angle)
        transform.translate(-self.size / 2, -self.size / 2)
        
        # Apply rotation
        rotated_pixmap = base_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        
        # Set the pixmap
        self.setPixmap(rotated_pixmap)
    
    def stop_animation(self):
        """Stop the spinning animation"""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
    
    def start_animation(self):
        """Start the spinning animation"""
        if not self.animation_timer.isActive():
            self.animation_timer.start(50)
    
    def __del__(self):
        """Clean up timer when widget is destroyed"""
        if hasattr(self, 'animation_timer') and self.animation_timer.isActive():
            self.animation_timer.stop()


class PortTestWorker(QThread):
    """Worker thread for port testing to prevent UI blocking"""
    
    test_completed = pyqtSignal(dict)
    
    def __init__(self, port_name: str):
        super().__init__()
        self.port_name = port_name
        self.tester = SerialPortTester()
    
    def run(self):
        """Run the port test in background thread with artificial delay"""
        try:
            # Add artificial delay to show loading state (1-2 seconds)
            self.msleep(1500)  # 1.5 seconds delay
            
            results = self.tester.test_port(self.port_name)
            self.test_completed.emit(results)
        except Exception as e:
            error_result = {
                "status": "Error",
                "message": f"Test failed: {str(e)}",
                "details": {"error": str(e)}
            }
            self.test_completed.emit(error_result)


class SerialPortTestWidget(QWidget):
    """
    Serial port testing widget with comprehensive diagnostics display.
    Follows the same design patterns as terminal and monitor widgets.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_port: Optional[SerialPortInfo] = None
        self.test_worker: Optional[PortTestWorker] = None
        self.last_test_results: Optional[Dict] = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface with theme integration"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section - matching terminal/monitor widget style
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(28)  # Match other widgets
        self.header_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
            }}
        """)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_SMALL,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_SMALL
        )
        header_layout.setSpacing(AppDimensions.SPACING_LARGE)
        
        # Port info section (left) - matching other widgets
        port_section = QHBoxLayout()
        port_section.setSpacing(AppDimensions.SPACING_SMALL)
        port_section.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Port status indicator (small colored bar)
        self.status_indicator = QFrame()
        self.status_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.TEXT_DISABLED};
                border: none;
            }}
        """)
        port_section.addWidget(self.status_indicator, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Port name and type
        self.port_label = QLabel("No port selected")
        self.port_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                background: transparent;
                border: none;
            }}
        """)
        self.port_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        port_section.addWidget(self.port_label)
        
        # Set status indicator height to match port label font height
        label_font_metrics = self.port_label.fontMetrics()
        label_height = label_font_metrics.height()
        self.status_indicator.setFixedSize(3, label_height)
        
        header_layout.addLayout(port_section)
        header_layout.addStretch()
        
        # Control section (right)
        control_section = QHBoxLayout()
        control_section.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Test button
        self.test_btn = QPushButton()
        self.test_btn.setFixedSize(24, 24)
        self.test_btn.setToolTip("Test selected port")
        self.test_btn.clicked.connect(self.run_port_test)
        self.test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_HOVER};
                border: 1px solid {AppColors.BORDER_DEFAULT};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: transparent;
            }}
        """)
        self._update_test_button_icon()
        control_section.addWidget(self.test_btn)
        
        header_layout.addLayout(control_section)
        
        main_layout.addWidget(self.header_widget)
        
        # Separator line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BORDER_DEFAULT};
                border: none;
                max-height: 1px;
            }}
        """)
        main_layout.addWidget(self.separator)
        
        # Test results display area
        self.create_results_area()
        main_layout.addWidget(self.results_scroll_area)
        
        # Initially hide everything
        self.hide_all()
    
    def create_results_area(self):
        """Create the scrollable test results display area"""
        # Create scroll area
        self.results_scroll_area = QScrollArea()
        self.results_scroll_area.setWidgetResizable(True)
        self.results_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {AppColors.BACKGROUND_WHITE};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {AppColors.BORDER_DEFAULT};
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {AppColors.BORDER_ACTIVE};
            }}
        """)
        
        # Create content widget
        self.results_widget = QWidget()
        self.results_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
            }}
        """)
        
        # Create layout for results
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_MEDIUM
        )
        self.results_layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # Add placeholder message
        self.placeholder_label = QLabel("Select a port and click the test button to run diagnostics")
        self.placeholder_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                background: transparent;
                border: none;
                padding: 8px;
            }}
        """)
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.addWidget(self.placeholder_label)
        self.results_layout.addStretch()
        
        self.results_scroll_area.setWidget(self.results_widget)
    
    def _update_test_button_icon(self):
        """Update test button icon"""
        from ui.theme.theme import IconManager
        
        icon = IconManager.create_svg_icon(
            AppIcons.REFRESH,  # Using refresh icon for test
            AppColors.TEXT_DEFAULT,
            IconManager.get_scaled_size(14)
        )
        self.test_btn.setIcon(icon)
        self.test_btn.setIconSize(IconManager.get_scaled_size(14))
    
    def _apply_status_style(self, style_type: str):
        """Apply the status indicator color"""
        status_colors = {
            "available": AppColors.SUCCESS_PRIMARY,
            "in_use": AppColors.WARNING_PRIMARY,
            "unavailable": AppColors.ERROR_PRIMARY,
            "virtual": AppColors.ACCENT_BLUE,
            "moxa": AppColors.ACCENT_ORANGE,
            "testing": AppColors.ACCENT_YELLOW,
            "error": AppColors.ERROR_PRIMARY,
            "info": AppColors.TEXT_DISABLED
        }
        
        color = status_colors.get(style_type, AppColors.TEXT_DISABLED)
        
        self.status_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
            }}
        """)
    
    def set_current_port(self, port_name: str, port_info: Optional[SerialPortInfo] = None):
        """Set the current port for testing"""
        self.current_port = port_info
        
        if port_name and port_name != "No ports available":
            # Update label to show current port
            if port_info:
                display_text = f"{port_name}"
                if port_info.description and port_info.description != "N/A":
                    desc = port_info.description[:30] + "..." if len(port_info.description) > 30 else port_info.description
                    display_text += f" - {desc}"
                
                # Update status indicator based on port type
                if port_info.is_moxa:
                    style_type = "moxa"
                elif port_info.port_type == "Physical":
                    style_type = "available"
                else:
                    style_type = "virtual"
                
                self._apply_status_style(style_type)
            else:
                display_text = f"{port_name}"
                self._apply_status_style("info")
            
            self.port_label.setText(display_text)
            self.header_widget.setVisible(True)
            self.separator.setVisible(True)
            self.results_scroll_area.setVisible(True)
            
            # Enable test button
            self.test_btn.setEnabled(True)
            
            # Clear previous results if port changed
            if not self.last_test_results or self.last_test_results.get('port') != port_name:
                self.clear_results()
        else:
            self.hide_all()
    
    def run_port_test(self):
        """Run port test in background thread"""
        if not self.current_port:
            return
        
        # Disable test button and show testing status
        self.test_btn.setEnabled(False)
        self._apply_status_style("testing")
        
        # Show testing message
        self.show_testing_message()
        
        # Start test worker
        self.test_worker = PortTestWorker(self.current_port.port_name)
        self.test_worker.test_completed.connect(self.on_test_completed)
        self.test_worker.start()
    
    def show_testing_message(self):
        """Show testing in progress message with animated spinner"""
        self.clear_results()
        
        # Create container for spinner and text
        loading_container = QWidget()
        loading_layout = QHBoxLayout(loading_container)
        loading_layout.setContentsMargins(0, 0, 0, 0)
        loading_layout.setSpacing(AppDimensions.SPACING_SMALL)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add animated spinner
        self.spinner = AnimatedSpinnerWidget(AppColors.ACCENT_BLUE, 18)
        loading_layout.addWidget(self.spinner)
        
        # Add testing message
        testing_label = QLabel("Testing port... Please wait")
        testing_label.setStyleSheet(f"""
            QLabel {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.NORMAL_WEIGHT};
                background: transparent;
                border: none;
                padding: 8px;
            }}
        """)
        loading_layout.addWidget(testing_label)
        
        # Center the loading container
        center_layout = QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(loading_container)
        center_layout.addStretch()
        
        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        self.results_layout.addWidget(center_widget)
    
    @pyqtSlot(dict)
    def on_test_completed(self, results: Dict):
        """Handle test completion"""
        self.last_test_results = results
        if self.current_port:
            self.last_test_results['port'] = self.current_port.port_name
        
        # Stop spinner animation if it exists
        if hasattr(self, 'spinner'):
            self.spinner.stop_animation()
        
        # Re-enable test button
        self.test_btn.setEnabled(True)
        
        # Update status indicator based on results
        if results['status'] == 'Available':
            self._apply_status_style("available")
        elif results['status'] == 'Error':
            self._apply_status_style("error")
        else:
            self._apply_status_style("info")
        
        # Display results
        self.display_test_results(results)
        
        # Clean up worker
        if self.test_worker:
            self.test_worker.deleteLater()
            self.test_worker = None
    
    def display_test_results(self, results: Dict):
        """Display comprehensive test results"""
        self.clear_results()
        
        # Main status section
        self.create_status_section(results)
        
        # If we have detailed results, show them
        if results.get('details') and results['status'] != 'Error':
            self.create_configuration_section(results['details'])
            self.create_flow_control_section(results['details'])
            self.create_modem_status_section(results['details'])
            self.create_buffer_section(results['details'])
            self.create_advanced_section(results['details'])
        elif results['status'] == 'Error':
            self.create_error_section(results)
        
        # Add stretch to push content to top
        self.results_layout.addStretch()
    
    def create_status_section(self, results: Dict):
        """Create the main status section"""
        status_group = QGroupBox("Port Status")
        status_group.setStyleSheet(f"""
            QGroupBox {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                color: {AppColors.TEXT_DEFAULT};
                border: 1px solid {AppColors.BORDER_DEFAULT};
                margin-top: 8px;
                padding-top: 4px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
        """)
        
        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL, 
                                       AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL)
        
        # Status message with color coding
        status_color = AppColors.SUCCESS_PRIMARY if results['status'] == 'Available' else AppColors.ERROR_PRIMARY
        
        status_label = QLabel(results['message'])
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                background: transparent;
                border: none;
                padding: 2px;
            }}
        """)
        status_layout.addWidget(status_label)
        
        self.results_layout.addWidget(status_group)
    
    def create_configuration_section(self, details: Dict):
        """Create port configuration section"""
        config_group = QGroupBox("Port Configuration")
        config_group.setStyleSheet(f"""
            QGroupBox {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                color: {AppColors.TEXT_DEFAULT};
                border: 1px solid {AppColors.BORDER_DEFAULT};
                margin-top: 8px;
                padding-top: 4px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
        """)
        
        config_layout = QGridLayout(config_group)
        config_layout.setContentsMargins(AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL,
                                       AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL)
        config_layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Configuration items
        config_items = [
            ("Data Bits:", str(details.get('bytesize', 'N/A'))),
            ("Parity:", str(details.get('parity', 'N/A'))),
            ("Stop Bits:", str(details.get('stopbits', 'N/A'))),
            ("Timeout:", f"{details.get('timeout', 'N/A')}s")
        ]
        
        for i, (label_text, value_text) in enumerate(config_items):
            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            config_layout.addWidget(label, i, 0)
            
            # Value
            value = QLabel(value_text)
            value.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.ACCENT_BLUE};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            config_layout.addWidget(value, i, 1)
        
        self.results_layout.addWidget(config_group)
    
    def create_flow_control_section(self, details: Dict):
        """Create flow control section"""
        flow_group = QGroupBox("Flow Control")
        flow_group.setStyleSheet(f"""
            QGroupBox {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                color: {AppColors.TEXT_DEFAULT};
                border: 1px solid {AppColors.BORDER_DEFAULT};
                margin-top: 8px;
                padding-top: 4px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
        """)
        
        flow_layout = QGridLayout(flow_group)
        flow_layout.setContentsMargins(AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL,
                                     AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL)
        flow_layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Flow control items
        flow_items = [
            ("XON/XOFF:", "Enabled" if details.get('xonxoff') else "Disabled"),
            ("RTS/CTS:", "Enabled" if details.get('rtscts') else "Disabled"),
            ("DSR/DTR:", "Enabled" if details.get('dsrdtr') else "Disabled")
        ]
        
        for i, (label_text, value_text) in enumerate(flow_items):
            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            flow_layout.addWidget(label, i, 0)
            
            # Value with color coding
            value_color = AppColors.SUCCESS_PRIMARY if "Enabled" in value_text else AppColors.TEXT_DISABLED
            value = QLabel(value_text)
            value.setStyleSheet(f"""
                QLabel {{
                    color: {value_color};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            flow_layout.addWidget(value, i, 1)
        
        self.results_layout.addWidget(flow_group)
    
    def create_modem_status_section(self, details: Dict):
        """Create modem status section"""
        modem_status = details.get('modem_status')
        if not modem_status or modem_status == "Not available":
            return
        
        modem_group = QGroupBox("Modem Status")
        modem_group.setStyleSheet(f"""
            QGroupBox {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                color: {AppColors.TEXT_DEFAULT};
                border: 1px solid {AppColors.BORDER_DEFAULT};
                margin-top: 8px;
                padding-top: 4px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
        """)
        
        modem_layout = QGridLayout(modem_group)
        modem_layout.setContentsMargins(AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL,
                                      AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL)
        modem_layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Modem status items
        for i, (signal, status) in enumerate(modem_status.items()):
            # Signal name
            signal_label = QLabel(f"{signal}:")
            signal_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            modem_layout.addWidget(signal_label, i, 0)
            
            # Status with color coding
            if status == 'N/A':
                status_color = AppColors.TEXT_DISABLED
            elif status:
                status_color = AppColors.SUCCESS_PRIMARY
            else:
                status_color = AppColors.ERROR_PRIMARY
            
            status_label = QLabel(str(status))
            status_label.setStyleSheet(f"""
                QLabel {{
                    color: {status_color};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            modem_layout.addWidget(status_label, i, 1)
        
        self.results_layout.addWidget(modem_group)
    
    def create_buffer_section(self, details: Dict):
        """Create buffer status section"""
        if details.get('in_waiting') == 'N/A' and details.get('out_waiting') == 'N/A':
            return
        
        buffer_group = QGroupBox("Buffer Status")
        buffer_group.setStyleSheet(f"""
            QGroupBox {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                color: {AppColors.TEXT_DEFAULT};
                border: 1px solid {AppColors.BORDER_DEFAULT};
                margin-top: 8px;
                padding-top: 4px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
        """)
        
        buffer_layout = QGridLayout(buffer_group)
        buffer_layout.setContentsMargins(AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL,
                                       AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL)
        buffer_layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Buffer items
        buffer_items = []
        if details.get('in_waiting') != 'N/A':
            buffer_items.append(("Input Buffer:", f"{details.get('in_waiting', 'N/A')} bytes"))
        if details.get('out_waiting') != 'N/A':
            buffer_items.append(("Output Buffer:", f"{details.get('out_waiting', 'N/A')} bytes"))
        
        for i, (label_text, value_text) in enumerate(buffer_items):
            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            buffer_layout.addWidget(label, i, 0)
            
            # Value
            value = QLabel(value_text)
            value.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.ACCENT_BLUE};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            buffer_layout.addWidget(value, i, 1)
        
        self.results_layout.addWidget(buffer_group)
    
    def create_advanced_section(self, details: Dict):
        """Create advanced timeouts section"""
        if details.get('write_timeout') == 'N/A' and details.get('inter_byte_timeout') == 'N/A':
            return
        
        advanced_group = QGroupBox("Advanced Timeouts")
        advanced_group.setStyleSheet(f"""
            QGroupBox {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                color: {AppColors.TEXT_DEFAULT};
                border: 1px solid {AppColors.BORDER_DEFAULT};
                margin-top: 8px;
                padding-top: 4px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
        """)
        
        advanced_layout = QGridLayout(advanced_group)
        advanced_layout.setContentsMargins(AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL,
                                         AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL)
        advanced_layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Advanced timeout items
        advanced_items = []
        if details.get('write_timeout') != 'N/A':
            advanced_items.append(("Write Timeout:", f"{details.get('write_timeout', 'N/A')}s"))
        if details.get('inter_byte_timeout') != 'N/A':
            advanced_items.append(("Inter-byte Timeout:", f"{details.get('inter_byte_timeout', 'N/A')}s"))
        
        for i, (label_text, value_text) in enumerate(advanced_items):
            # Label
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            advanced_layout.addWidget(label, i, 0)
            
            # Value
            value = QLabel(value_text)
            value.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.ACCENT_BLUE};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            advanced_layout.addWidget(value, i, 1)
        
        self.results_layout.addWidget(advanced_group)
    
    def create_error_section(self, results: Dict):
        """Create error details section"""
        error_group = QGroupBox("Error Details")
        error_group.setStyleSheet(f"""
            QGroupBox {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                color: {AppColors.ERROR_PRIMARY};
                border: 1px solid {AppColors.ERROR_PRIMARY};
                margin-top: 8px;
                padding-top: 4px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
        """)
        
        error_layout = QVBoxLayout(error_group)
        error_layout.setContentsMargins(AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL,
                                      AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL)
        
        # Error details
        error_details = results.get('details', {})
        error_text = error_details.get('error', 'Unknown error')
        
        error_label = QLabel(error_text)
        error_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.ERROR_PRIMARY};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                background: transparent;
                border: none;
                padding: 4px;
            }}
        """)
        error_label.setWordWrap(True)
        error_layout.addWidget(error_label)
        
        self.results_layout.addWidget(error_group)
    
    def clear_results(self):
        """Clear all test results"""
        # Remove all widgets except the layout
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def hide_all(self):
        """Hide all test information"""
        self.header_widget.setVisible(False)
        self.separator.setVisible(False)
        self.results_scroll_area.setVisible(False)
        self.test_btn.setEnabled(False)
        self.clear_results()
        
        # Reset placeholder
        self.placeholder_label = QLabel("Select a port and click the test button to run diagnostics")
        self.placeholder_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                background: transparent;
                border: none;
                padding: 8px;
            }}
        """)
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.addWidget(self.placeholder_label)
        self.results_layout.addStretch()
    
    def get_current_port(self) -> Optional[str]:
        """Get the currently set port name"""
        return self.current_port.port_name if self.current_port else None