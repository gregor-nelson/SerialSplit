#!/usr/bin/env python3
"""
Serial Port Test Widget - Provides comprehensive port testing functionality
Integrates with main GUI port selection (no internal dropdown)
"""

from typing import Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame, QScrollArea, QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSlot, pyqtSignal, QTimer
from PyQt6.QtGui import QTransform, QPainter, QResizeEvent

from core.core import SerialPortInfo, SerialPortTester
from ui.theme.theme import (
    ThemeManager, AppDimensions, AppColors, AppFonts
)
from ui.theme.icons.icons import AppIcons


class AnimatedSpinnerWidget(QLabel):
    """Animated spinner widget that rotates continuously"""
    
    def __init__(self, color: str, size: int = 18):
        super().__init__()
        self.color = color
        self.size = size
        self.rotation_angle = 0
        
        # Create the base icon without animation
        from ui.theme.theme import IconManager
        
        # Use a simpler spinner SVG without animation for manual rotation
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
        self.active_spinners = []  # Track active animated spinners for cleanup
        
        # Layout responsiveness  
        self.min_width_for_two_columns = 400  # Minimum width to enable two-column layout (reduced from 600)
        self.is_two_column_layout = True  # Start with two-column as default for 50/50 mode
        self.results_widgets = []  # Track result widgets for layout switching
        self.widget_types = []  # Track widget types (status, property) for layout decisions
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface with theme integration"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 4, 6, 4)  # Tighter main margins
        main_layout.setSpacing(6)  # Reduced spacing between sections
        
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
        self.port_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
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
        
        # Results container widget with grid layout for responsiveness
        self.results_widget = QWidget()
        self.results_layout = QGridLayout(self.results_widget)
        self.results_layout.setContentsMargins(4, 4, 4, 4)  # Minimal margins
        self.results_layout.setSpacing(4)  # Tight spacing between cards
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Set equal column stretching for two-column mode
        self.results_layout.setColumnStretch(0, 1)
        self.results_layout.setColumnStretch(1, 1)
        
        self.results_scroll.setWidget(self.results_widget)
        main_layout.addWidget(self.results_scroll)
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle widget resize to switch between single and two-column layouts"""
        super().resizeEvent(event)
        self._update_layout_based_on_width()
    
    def _update_layout_based_on_width(self):
        """Switch between single and two-column layouts based on available width"""
        current_width = self.width()
        should_use_two_columns = current_width >= self.min_width_for_two_columns
        
        if should_use_two_columns != self.is_two_column_layout:
            self.is_two_column_layout = should_use_two_columns
            self._rearrange_existing_widgets()
    
    def _rearrange_existing_widgets(self):
        """Rearrange existing widgets without rebuilding layout"""
        if not self.results_widgets:
            return
        
        # Remove all widgets from grid positions (but don't delete them)
        for widget in self.results_widgets:
            self.results_layout.removeWidget(widget)
        
        # Re-add widgets in the appropriate arrangement
        current_row = 0
        property_widgets_in_row = 0
        
        for i, (widget, widget_type) in enumerate(zip(self.results_widgets, self.widget_types)):
            if self.is_two_column_layout:
                if widget_type == "status":
                    # Status widgets span entire row
                    if property_widgets_in_row > 0:
                        current_row += 1  # Move to next row if we had property widgets
                        property_widgets_in_row = 0
                    self.results_layout.addWidget(widget, current_row, 0, 1, 2)  # Span both columns
                    current_row += 1
                else:  # property widget
                    # Property widgets use columns
                    col = property_widgets_in_row % 2
                    if col == 0 and property_widgets_in_row > 0:
                        current_row += 1
                    self.results_layout.addWidget(widget, current_row, col)
                    property_widgets_in_row += 1
                    if col == 1:  # Completed a row
                        current_row += 1
                        property_widgets_in_row = 0
            else:
                # Single-column arrangement (all in column 0, spanning both columns)
                self.results_layout.addWidget(widget, i, 0, 1, 2)
    
    def _add_result_widget(self, widget: QWidget, widget_type: str = "property"):
        """Add a widget to results with responsive layout support
        
        Args:
            widget: The widget to add
            widget_type: Either 'status' (spans full row) or 'property' (uses columns)
        """
        self.results_widgets.append(widget)
        self.widget_types.append(widget_type)
        
        # Calculate position based on existing widgets
        if self.is_two_column_layout:
            if widget_type == "status":
                # Status widgets span entire row
                current_row = self._calculate_next_status_row()
                self.results_layout.addWidget(widget, current_row, 0, 1, 2)  # Span both columns
            else:  # property widget
                row, col = self._calculate_next_property_position()
                self.results_layout.addWidget(widget, row, col)
        else:
            # Single-column arrangement (all widgets span both columns)
            widget_index = len(self.results_widgets) - 1
            self.results_layout.addWidget(widget, widget_index, 0, 1, 2)
    
    def _calculate_next_status_row(self) -> int:
        """Calculate the next available row for a status widget"""
        if not self.results_widgets:
            return 0
        
        # Count property widgets that aren't paired (to see if we need an extra row)
        property_count = sum(1 for t in self.widget_types[:-1] if t == "property")
        status_count = sum(1 for t in self.widget_types[:-1] if t == "status")
        
        # Each status takes 1 row, each pair of properties takes 1 row
        used_rows = status_count + (property_count + 1) // 2
        return used_rows
    
    def _calculate_next_property_position(self) -> tuple:
        """Calculate the next position (row, col) for a property widget"""
        # Count widgets before this one
        property_widgets_before = 0
        current_row = 0
        
        for widget_type in self.widget_types[:-1]:  # Exclude the current widget
            if widget_type == "status":
                if property_widgets_before % 2 == 1:  # Odd number, incomplete row
                    current_row += 1  # Complete the row
                current_row += 1  # Status takes its own row
                property_widgets_before = 0  # Reset property count for new section
            else:  # property
                property_widgets_before += 1
                if property_widgets_before % 2 == 0:  # Completed a pair
                    current_row += 1
        
        # Calculate position for the new property widget
        col = property_widgets_before % 2
        if col == 0 and property_widgets_before > 0:
            current_row += 1
            
        return current_row, col
    
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
        # Stop all active spinners before clearing
        for spinner in self.active_spinners:
            if spinner and hasattr(spinner, 'stop_animation'):
                spinner.stop_animation()
        self.active_spinners.clear()
        
        # Clear tracked widgets and types
        self.results_widgets.clear()
        self.widget_types.clear()
        
        # Clear all widgets from results layout
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _show_loading_message(self):
        """Show initial loading state"""
        self._update_status_indicator("testing")
        self._clear_results()
        
        # Create loading message card with animated spinner
        loading_card = self._create_status_card(
            "spinner", 
            "Starting Test...",
            "Preparing diagnostics",
            AppColors.ACCENT_BLUE
        )
        self._add_result_widget(loading_card, "status")
    
    def _show_testing_message(self):
        """Show testing in progress message"""
        self._update_status_indicator("testing")
        self._clear_results()
        
        # Create testing message card
        testing_card = self._create_status_card(
            "spinner", 
            "Testing Port...",
            "Running checks",
            AppColors.WARNING_PRIMARY
        )
        self._add_result_widget(testing_card, "status")
        
        # Create progress info
        progress_text = [
            "• Checking port availability",
            "• Testing port configuration", 
            "• Verifying modem status",
            "• Checking buffer status"
        ]
        
        progress_card = self._create_info_card("Test Progress", progress_text)
        self._add_result_widget(progress_card, "property")
    
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
        layout.setContentsMargins(8, 8, 8, 8)  # Compact status card margins
        layout.setSpacing(8)  # Reduced spacing in status cards
        
        # Status icon - use animated spinner or SVG for custom icons, text for fallback
        if icon == "spinner":
            # Use animated spinner widget
            icon_label = AnimatedSpinnerWidget(color, 18)
            # Track spinner for cleanup
            if hasattr(self, 'active_spinners'):
                self.active_spinners.append(icon_label)
        elif icon in ["success", "error"]:
            from ui.theme.theme import IconManager
            
            icon_label = QLabel()
            
            # Map icon types to SVG definitions
            icon_mapping = {
                "success": AppIcons.CHECKBOX_CHECK,
                "error": AppIcons.ERROR_CROSS
            }
            
            svg_icon = IconManager.create_svg_icon(
                icon_mapping[icon],
                color,
                IconManager.get_scaled_size(18)
            )
            icon_label.setPixmap(svg_icon.pixmap(18, 18))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setFixedSize(24, 24)
        else:
            # Fallback for text icons
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 16pt;
                    font-weight: bold;
                    background: transparent;
                }}
            """)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setFixedSize(24, 24)
        
        layout.addWidget(icon_label)
        
        # Text section
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)  # Minimal spacing between title and subtitle
        
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
        
        # Properties grid with tight spacing
        for key, value in properties.items():
            prop_layout = QHBoxLayout()
            prop_layout.setContentsMargins(0, 0, 0, 0)
            prop_layout.setSpacing(8)  # Fixed gap between columns
            
            # Property name - fixed width for alignment
            key_label = QLabel(f"{key}:")
            key_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.SMALL_SIZE};
                    background: transparent;
                }}
            """)
            key_label.setFixedWidth(100)  # Fixed width for consistent alignment
            key_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            prop_layout.addWidget(key_label)
            
            # Property value - pinned left with stretch after
            value_label = QLabel(str(value))
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.CONSOLE.family()};
                    font-size: {AppFonts.SMALL_SIZE};
                    background: transparent;
                }}
            """)
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            value_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            prop_layout.addWidget(value_label)
            
            # Add stretch to consume extra horizontal space
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
        layout.setContentsMargins(8, 6, 8, 6)  # Compact info card margins
        layout.setSpacing(2)  # Tight spacing between info items
        
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
                "success", 
                message,
                "All diagnostics completed successfully",
                AppColors.SUCCESS_PRIMARY
            )
            self._add_result_widget(status_card, "status")
            
            # Parse and display detailed results
            formatted_results = self.tester.format_test_results(results)
            self._parse_and_display_results(formatted_results)
        else:
            self._update_status_indicator("error")
            # Create error status card
            error_msg = details.get('error', 'Unknown error')
            status_card = self._create_status_card(
                "error", 
                message,
                f"Error: {error_msg}",
                AppColors.ERROR_PRIMARY
            )
            self._add_result_widget(status_card, "status")
    
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
                    self._add_result_widget(card, "property")
                
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
            self._add_result_widget(card, "property")
    
    def _show_error_message(self, error_msg: str):
        """Show error message in results area"""
        self._update_status_indicator("error")
        self._clear_results()
        
        error_card = self._create_status_card(
            "error", 
            "Test Failed",
            error_msg,
            AppColors.ERROR_PRIMARY
        )
        self._add_result_widget(error_card, "status")