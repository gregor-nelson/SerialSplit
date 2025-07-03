#!/usr/bin/env python3
"""
Serial Port Test Widget - Provides comprehensive port testing functionality
Integrates with main GUI port selection (no internal dropdown)
"""

from typing import Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSlot, pyqtSignal, QTimer

from core.core import SerialPortInfo, SerialPortTester
from ui.theme.theme import (
    ThemeManager, AppDimensions, AppColors, AppFonts
)
from ui.theme.icons.icons import AppIcons


class PortTestWorker(QThread):
    """Worker thread for testing serial ports without blocking UI"""
    
    test_completed = pyqtSignal(dict)
    
    def __init__(self, port_name: str):
        super().__init__()
        self.port_name = port_name
        self.tester = SerialPortTester()
    
    def run(self):
        """Run the port test in a separate thread"""
        results = self.tester.test_port(self.port_name)
        self.test_completed.emit(results)


class SerialPortTestWidget(QWidget):
    """Widget for testing serial ports with comprehensive diagnostics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_port_name: Optional[str] = None
        self.current_port_info: Optional[SerialPortInfo] = None
        self.tester = SerialPortTester()
        self.test_worker: Optional[PortTestWorker] = None
        self.loading_timer = QTimer()
        self.loading_timer.setSingleShot(True)
        self.loading_timer.timeout.connect(self._start_actual_test)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface with theme integration"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            AppDimensions.SPACING_LARGE,
            AppDimensions.SPACING_MEDIUM, 
            AppDimensions.SPACING_LARGE,
            AppDimensions.SPACING_MEDIUM
        )
        main_layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # Header section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # Port status indicator (colored bar) - matches monitor widget
        self.status_indicator = QFrame()
        self.status_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.TEXT_DISABLED};
                border: none;
            }}
        """)
        header_layout.addWidget(self.status_indicator, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Current port display - matches monitor widget styling
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
        self.port_label.setMinimumWidth(200)
        
        # Set status indicator height to match port label font height
        label_font_metrics = self.port_label.fontMetrics()
        label_height = label_font_metrics.height()
        self.status_indicator.setFixedSize(3, label_height)
        
        header_layout.addWidget(self.port_label)
        
        header_layout.addStretch()
        
        # Test button - icon button matching monitor widget style
        self.test_button = QPushButton()
        self.test_button.setFixedSize(24, 24)
        self.test_button.setToolTip("Start port test")
        self.test_button.clicked.connect(self.test_current_port)
        self.test_button.setStyleSheet(f"""
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
        """)
        self._update_test_button_icon(False)
        self.test_button.setEnabled(False)
        header_layout.addWidget(self.test_button)
        
        main_layout.addLayout(header_layout)
        
        # Separator - matches help dialog separators
        separator = ThemeManager.create_separator("horizontal")
        main_layout.addWidget(separator)
        
        # Results area - scrollable container for property cards
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.results_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border: none;
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {AppColors.BORDER_DEFAULT};
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {AppColors.TEXT_DISABLED};
            }}
        """)
        
        # Results container widget
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_MEDIUM
        )
        self.results_layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.results_scroll.setWidget(self.results_widget)
        main_layout.addWidget(self.results_scroll)
    
    def _update_test_button_icon(self, is_testing: bool):
        """Update test button icon matching monitor widget style"""
        from ui.theme.theme import IconManager
        
        if is_testing:
            icon = IconManager.create_svg_icon(
                AppIcons.STOP,
                AppColors.TEXT_DEFAULT,
                IconManager.get_scaled_size(14)
            )
            self.test_button.setToolTip("Stop test")
        else:
            icon = IconManager.create_svg_icon(
                AppIcons.PLAY,
                AppColors.TEXT_DEFAULT,
                IconManager.get_scaled_size(14)
            )
            self.test_button.setToolTip("Start test")
        
        self.test_button.setIcon(icon)
        self.test_button.setIconSize(IconManager.get_scaled_size(14))
    
    def set_current_port(self, port_name: str, port_info: Optional[SerialPortInfo] = None):
        """Set the current port to test from external source (main GUI)"""
        self.current_port_name = port_name
        self.current_port_info = port_info
        
        if port_name and port_name != "No ports available":
            # Update label to show current port
            if port_info:
                display_text = f"{port_name}"
                if port_info.description and port_info.description != "N/A":
                    display_text += f" - {port_info.description[:30]}"
                if port_info.port_type and port_info.port_type != "Unknown":
                    display_text += f" ({port_info.port_type})"
                    
                # Update status indicator based on port type
                self._update_status_indicator(port_info.port_type)
            else:
                display_text = f"{port_name}"
                self._update_status_indicator("unknown")
                
            self.port_label.setText(display_text)
            self.port_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    background: transparent;
                    border: none;
                }}
            """)
            
            # Enable test button if not currently testing
            self.test_button.setEnabled(not self._is_testing())
            
            # Clear previous results
            self._clear_results()
        else:
            self.test_button.setEnabled(False)
            self._clear_results()
            self._update_status_indicator("none")
    
    def test_current_port(self):
        """Test the currently set port (from main GUI selection)"""
        if self._is_testing():
            return
            
        if not self.current_port_name:
            return
        
        # Disable button and show immediate loading state
        self.test_button.setEnabled(False)
        self._update_test_button_icon(True)
        self._show_loading_message()
        
        # Start loading timer for visual consistency (750ms delay)
        self.loading_timer.start(750)
    
    def _start_actual_test(self):
        """Start the actual test after loading delay"""
        if not self.current_port_name:
            return
            
        # Show testing message
        self._show_testing_message()
        
        # Start test in worker thread
        self.test_worker = PortTestWorker(self.current_port_name)
        self.test_worker.test_completed.connect(self.on_test_completed)
        self.test_worker.finished.connect(self.on_test_finished)
        self.test_worker.start()
    
    @pyqtSlot(dict)
    def on_test_completed(self, results: dict):
        """Handle completed port test"""
        # Display results in clean format
        self._display_test_results(results)
    
    @pyqtSlot()
    def on_test_finished(self):
        """Handle test worker finishing (success or failure)"""
        # Stop loading timer if still active
        if self.loading_timer.isActive():
            self.loading_timer.stop()
            
        # Reset UI state
        self.test_button.setEnabled(bool(self.current_port_name))
        self._update_test_button_icon(False)
        
        # Clean up worker
        if self.test_worker:
            self.test_worker.deleteLater()
            self.test_worker = None
    
    def get_current_port(self) -> Optional[str]:
        """Get the currently set port name"""
        return self.current_port_name
    
    def _is_testing(self) -> bool:
        """Check if a test is currently running"""
        return (self.test_worker is not None and self.test_worker.isRunning()) or self.loading_timer.isActive()
    
    def _update_status_indicator(self, port_type: str):
        """Update the status indicator color based on port type/status"""
        status_colors = {
            "Physical": AppColors.SUCCESS_PRIMARY,
            "Virtual COM0COM": AppColors.ACCENT_BLUE,
            "Virtual": AppColors.ACCENT_BLUE,
            "testing": AppColors.WARNING_PRIMARY,
            "success": AppColors.SUCCESS_PRIMARY,
            "error": AppColors.ERROR_PRIMARY,
            "unknown": AppColors.TEXT_DISABLED,
            "none": AppColors.TEXT_DISABLED
        }
        
        color = status_colors.get(port_type, AppColors.TEXT_DISABLED)
        self.status_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
            }}
        """)
    
    def _clear_results(self):
        """Clear all results from the display"""
        # Clear all widgets from results layout
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _show_loading_message(self):
        """Show initial loading state"""
        self._update_status_indicator("testing")
        self._clear_results()
        
        # Create loading message card
        loading_card = self._create_status_card(
            "⏳", 
            "Initializing Test...",
            "Preparing port diagnostics",
            AppColors.ACCENT_BLUE
        )
        self.results_layout.addWidget(loading_card)
    
    def _show_testing_message(self):
        """Show testing in progress message"""
        self._update_status_indicator("testing")
        self._clear_results()
        
        # Create testing message card
        testing_card = self._create_status_card(
            "●", 
            f"Testing port {self.current_port_name}...",
            "Running comprehensive port diagnostics",
            AppColors.WARNING_PRIMARY
        )
        self.results_layout.addWidget(testing_card)
        
        # Create progress info
        progress_text = [
            "• Checking port availability",
            "• Testing port configuration", 
            "• Verifying modem status",
            "• Checking buffer status"
        ]
        
        progress_card = self._create_info_card("Test Progress", progress_text)
        self.results_layout.addWidget(progress_card)
    
    def _create_status_card(self, icon: str, title: str, subtitle: str, color: str) -> QWidget:
        """Create a large status header card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                padding: 0px;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(
            AppDimensions.SPACING_LARGE,
            AppDimensions.SPACING_LARGE,
            AppDimensions.SPACING_LARGE,
            AppDimensions.SPACING_LARGE
        )
        layout.setSpacing(AppDimensions.SPACING_LARGE)
        
        # Status icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 20pt;
                font-weight: bold;
                background: transparent;
            }}
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(32, 32)
        layout.addWidget(icon_label)
        
        # Text section
        text_layout = QVBoxLayout()
        text_layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.CONSOLE_LARGE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                background: transparent;
            }}
        """)
        text_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                background: transparent;
            }}
        """)
        text_layout.addWidget(subtitle_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return card
    
    def _create_property_card(self, title: str, properties: dict) -> QWidget:
        """Create a property card with key-value pairs"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                padding: 0px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            AppDimensions.SPACING_LARGE,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_LARGE,
            AppDimensions.SPACING_MEDIUM
        )
        layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Card title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                background: transparent;
                padding-bottom: 4px;
            }}
        """)
        layout.addWidget(title_label)
        
        # Properties grid
        for key, value in properties.items():
            prop_layout = QHBoxLayout()
            prop_layout.setContentsMargins(0, 0, 0, 0)
            prop_layout.setSpacing(AppDimensions.SPACING_MEDIUM)
            
            # Property name
            key_label = QLabel(f"{key}:")
            key_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.SMALL_SIZE};
                    background: transparent;
                }}
            """)
            key_label.setMinimumWidth(120)
            prop_layout.addWidget(key_label)
            
            # Property value
            value_label = QLabel(str(value))
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.CONSOLE.family()};
                    font-size: {AppFonts.SMALL_SIZE};
                    background: transparent;
                }}
            """)
            prop_layout.addWidget(value_label)
            prop_layout.addStretch()
            
            layout.addLayout(prop_layout)
        
        return card
    
    def _create_info_card(self, title: str, info_list: list) -> QWidget:
        """Create an info card with bullet points"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                padding: 0px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            AppDimensions.SPACING_LARGE,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_LARGE,
            AppDimensions.SPACING_MEDIUM
        )
        layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Card title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                background: transparent;
                padding-bottom: 4px;
            }}
        """)
        layout.addWidget(title_label)
        
        # Info items
        for item in info_list:
            item_label = QLabel(item)
            item_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.SMALL_SIZE};
                    background: transparent;
                    padding-left: 8px;
                }}
            """)
            layout.addWidget(item_label)
        
        return card
    
    def _display_test_results(self, results: dict):
        """Display test results using grouped property cards"""
        # Check if we have valid results
        if not results:
            self._show_error_message("No test results received")
            return
        
        # Get the status from the actual SerialPortTester result structure
        status = results.get('status', 'Unknown')
        message = results.get('message', 'No message provided')
        details = results.get('details', {})
        
        # Determine success based on status
        is_success = status == 'Available'
        self._clear_results()
        
        if is_success:
            self._update_status_indicator("success")
            # Create success status card
            status_card = self._create_status_card(
                "✓", 
                message,
                "All diagnostics completed successfully",
                AppColors.SUCCESS_PRIMARY
            )
            self.results_layout.addWidget(status_card)
            
            # Parse and display detailed results
            formatted_results = self.tester.format_test_results(results)
            self._parse_and_display_results(formatted_results)
        else:
            self._update_status_indicator("error")
            # Create error status card
            error_msg = details.get('error', 'Unknown error')
            status_card = self._create_status_card(
                "✗", 
                message,
                f"Error: {error_msg}",
                AppColors.ERROR_PRIMARY
            )
            self.results_layout.addWidget(status_card)
    
    def _parse_and_display_results(self, formatted_results: str):
        """Parse formatted results and create property cards"""
        lines = formatted_results.split('\n')
        current_section = None
        current_properties = {}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('='): 
                continue
                
            # Check for section headers (lines ending with ':')
            if line.endswith(':') and not line.count(':') > 1:
                # Save previous section if exists
                if current_section and current_properties:
                    card = self._create_property_card(current_section, current_properties)
                    self.results_layout.addWidget(card)
                
                # Start new section
                current_section = line[:-1]  # Remove the colon
                current_properties = {}
            elif ':' in line and current_section:
                # Property line
                key, value = line.split(':', 1)
                current_properties[key.strip()] = value.strip()
        
        # Add the last section
        if current_section and current_properties:
            card = self._create_property_card(current_section, current_properties)
            self.results_layout.addWidget(card)
    
    def _show_error_message(self, error_msg: str):
        """Show error message in results area"""
        self._update_status_indicator("error")
        self._clear_results()
        
        error_card = self._create_status_card(
            "✗", 
            "Test Failed",
            error_msg,
            AppColors.ERROR_PRIMARY
        )
        self.results_layout.addWidget(error_card)