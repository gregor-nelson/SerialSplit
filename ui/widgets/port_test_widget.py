#!/usr/bin/env python3
"""
Serial Port Test Widget - Provides comprehensive port testing functionality
Integrates with main GUI port selection (no internal dropdown)
"""

from typing import Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame, QScrollArea, QSizePolicy, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, QThread, pyqtSlot, pyqtSignal, QTimer
from PyQt6.QtGui import QTransform, QPainter, QResizeEvent, QColor

from core.core import SerialPortInfo, SerialPortTester
from ui.theme.theme import (
    ThemeManager, AppDimensions, AppColors, AppFonts, AppStyles 
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
        
        # Results table for Windows-native feel
        self.results_table = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface with theme integration"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(2)  # Reduced spacing between sections
        
        # Header section (hideable for compact results view)
        self.header_widget = QWidget()
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
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
        
        main_layout.addWidget(self.header_widget)
        
        # Separator - matches help dialog separators (hideable with header)
        self.header_separator = ThemeManager.create_separator("horizontal")
        main_layout.addWidget(self.header_separator)
        
        # Results area - use table for better Windows-native feel
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.results_scroll.setStyleSheet(AppStyles.scroll_area())
        
        # Create container widget that can hold either status cards OR results table
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins for compactness
        self.results_layout.setSpacing(2)  # Tight spacing for compactness
        
        # Results table for test data (initially hidden)
        self.results_table = self._create_results_table()
        self.results_table.setVisible(False)
        self.results_layout.addWidget(self.results_table)
        
        self.results_scroll.setWidget(self.results_widget)
        main_layout.addWidget(self.results_scroll)
        
        # Track status widgets for loading/testing states
        self.status_widgets = []
    
    def _create_results_table(self) -> QTableWidget:
        """Create Windows-native style results table"""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Property", "Value"])
        
        # Apply Windows-native table styling with compact layout
        table.setStyleSheet(f"""
            QTableWidget {{
                border: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BACKGROUND_WHITE};
                color: {AppColors.TEXT_DEFAULT};
                gridline-color: {AppColors.BORDER_LIGHT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.SMALL_SIZE};
                outline: none;
                selection-background-color: {AppColors.SELECTION_BG};
                selection-color: {AppColors.SELECTION_TEXT};
            }}
            QTableWidget::item {{
                padding: 2px 4px;
                border: none;
                border-bottom: 1px solid {AppColors.BORDER_LIGHT};
                height: 18px;
            }}
            QTableWidget::item:selected {{
                background-color: {AppColors.SELECTION_BG};
                color: {AppColors.SELECTION_TEXT};
            }}
            QHeaderView::section {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
                padding: 2px 4px;
                border: none;
                border-right: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {AppColors.BORDER_DEFAULT};
                border-bottom: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {AppColors.BORDER_DEFAULT};
                font-weight: {AppFonts.BOLD_WEIGHT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.SMALL_SIZE};
                height: 20px;
            }}
        """)
        
        # Configure table behavior
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Compact row heights for maximum density
        table.verticalHeader().setDefaultSectionSize(20)  # Compact row height
        table.verticalHeader().setMinimumSectionSize(18)   # Minimum row height
        table.setShowGrid(True)  # Show gridlines for better separation in compact view
        
        # Optimize for small screens
        table.setMinimumHeight(80)  # Reduced minimum height
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        return table
    
    def _hide_header_for_results(self):
        """Hide header and separator to maximize results view"""
        self.header_widget.setVisible(False)
        self.header_separator.setVisible(False)
    
    def _show_header_for_testing(self):
        """Show header and separator for port selection and testing"""
        self.header_widget.setVisible(True)
        self.header_separator.setVisible(True)
    
    def _add_section_header(self, section_name: str):
        """Add a compact section header row to the table"""
        current_row = self.results_table.rowCount()
        self.results_table.insertRow(current_row)
        
        # Create section header item that spans both columns
        header_item = QTableWidgetItem(section_name)
        header_item.setBackground(QColor(AppColors.BACKGROUND_LIGHT))
        header_item.setForeground(QColor(AppColors.TEXT_DEFAULT))
        
        # Make section header bold and compact
        font = header_item.font()
        font.setBold(True)
        font.setPointSize(8)  # Smaller font for compactness
        header_item.setFont(font)
        
        self.results_table.setItem(current_row, 0, header_item)
        self.results_table.setSpan(current_row, 0, 1, 2)  # Span both columns
        
        # Set compact height for section header
        self.results_table.setRowHeight(current_row, 22)
    
    def _add_property_row(self, property_name: str, value: str):
        """Add a compact property row to the table"""
        current_row = self.results_table.rowCount()
        self.results_table.insertRow(current_row)
        
        # Property name with compact font
        name_item = QTableWidgetItem(property_name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        name_font = name_item.font()
        name_font.setPointSize(8)  # Compact font size
        name_item.setFont(name_font)
        
        # Property value with compact monospace font
        value_item = QTableWidgetItem(str(value))
        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        value_font = value_item.font()
        value_font.setFamily(AppFonts.CONSOLE.family())
        value_font.setPointSize(8)  # Compact font size
        value_item.setFont(value_font)
        
        self.results_table.setItem(current_row, 0, name_item)
        self.results_table.setItem(current_row, 1, value_item)
        
        # Set compact height for property row
        self.results_table.setRowHeight(current_row, 20)
    
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
        
        # Show header when user selects a port (for testing interface)
        self._show_header_for_testing()
        
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
        
        # Clear status widgets
        for widget in self.status_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.status_widgets.clear()
        
        # Clear and hide table
        self.results_table.setRowCount(0)
        self.results_table.setVisible(False)
    
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
        # Insert loading card above the table
        table_index = self.results_layout.indexOf(self.results_table)
        self.results_layout.insertWidget(table_index, loading_card)
        self.status_widgets.append(loading_card)
    
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
        # Insert testing card above the table
        table_index = self.results_layout.indexOf(self.results_table)
        self.results_layout.insertWidget(table_index, testing_card)
        self.status_widgets.append(testing_card)
        
        # Create progress info
        progress_text = [
            "• Checking port availability",
            "• Testing port configuration", 
            "• Verifying modem status",
            "• Checking buffer status"
        ]
        
        progress_card = self._create_info_card("Test Progress", progress_text)
        # Insert progress card above the table as well
        table_index = self.results_layout.indexOf(self.results_table)
        self.results_layout.insertWidget(table_index, progress_card)
        self.status_widgets.append(progress_card)
    
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
                    font-size: {AppFonts.CAPTION_SIZE};
                    font-weight: {AppFonts.BOLD_WEIGHT};
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
                font-size: {AppFonts.CAPTION_SIZE};
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
        layout.setContentsMargins(2, 2, 2, 2)  # Compact info card margins
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
    
    def _create_modern_card(self, title: str, icon_name: str, content: dict, card_type: str = "info") -> QWidget:
        """Create a modern Windows 10-style card with proper spacing and visual hierarchy"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.BACKGROUND_WHITE};
                padding: 0px;
                margin: 2px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 6, 6, 6)  # Windows 10 standard padding
        layout.setSpacing(8)
        
        # Card header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel()
        icon_svg = self._get_section_icon(icon_name)
        icon_color = self._get_section_color(card_type)
        
        from ui.theme.theme import IconManager
        icon_pixmap = IconManager.create_svg_icon(icon_svg, icon_color, 16).pixmap(16, 16)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(16, 16)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                background: transparent;
            }}
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Content area with key-value pairs
        for key, value in content.items():
            prop_layout = QHBoxLayout()
            prop_layout.setContentsMargins(0, 0, 0, 0)
            prop_layout.setSpacing(8)
            
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
            key_label.setFixedWidth(90)
            key_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            prop_layout.addWidget(key_label)
            
            # Property value
            value_label = QLabel(str(value))
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-family: {AppFonts.CONSOLE.family()};
                    font-size: {AppFonts.SMALL_SIZE};
                    background: transparent;
                    font-weight: {AppFonts.BOLD_WEIGHT};
                }}
            """)
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            prop_layout.addWidget(value_label)
            prop_layout.addStretch()
            
            layout.addLayout(prop_layout)
        
        return card
    
    def _get_section_icon(self, icon_name: str) -> str:
        """Get appropriate icon for each section"""
        icons = {
            "settings": AppIcons.SETTINGS,
            "flow": AppIcons.FLOW_CONTROL,
            "signal": AppIcons.SIGNAL,
            "buffer": AppIcons.BUFFER,
            "timeout": AppIcons.CLOCK,
            "config": AppIcons.SETTINGS
        }
        return icons.get(icon_name, AppIcons.INFO)
    
    def _get_section_color(self, card_type: str) -> str:
        """Get section-specific colors"""
        colors = {
            "config": AppColors.ACCENT_BLUE,
            "control": AppColors.ACCENT_GREEN,
            "status": AppColors.ACCENT_ORANGE,
            "info": AppColors.ACCENT_TEAL,
            "error": AppColors.ACCENT_RED
        }
        return colors.get(card_type, AppColors.ACCENT_BLUE)
    
    def _format_boolean(self, value: bool) -> str:
        """Format boolean values with visual indicators"""
        if value:
            return "✓ Enabled"
        else:
            return "✗ Disabled"
    
    def _format_signal_status(self, value) -> str:
        """Format modem signal status with indicators"""
        if value == True:
            return "🟢 Active"
        elif value == False:
            return "🔴 Inactive"
        else:
            return "⚪ Unknown"
    
    def _create_port_config_card(self, details: dict) -> QWidget:
        """Create Port Configuration card with proper formatting"""
        config_data = {
            "Data Bits": details.get('bytesize', 'N/A'),
            "Parity": details.get('parity', 'N/A'),
            "Stop Bits": details.get('stopbits', 'N/A'),
            "Timeout": f"{details.get('timeout', 'N/A')}s"
        }
        return self._create_modern_card("Port Configuration", "config", config_data, "config")
    
    def _create_flow_control_card(self, details: dict) -> QWidget:
        """Create Flow Control card with status indicators"""
        flow_data = {
            "XON/XOFF": self._format_boolean(details.get('xonxoff', False)),
            "RTS/CTS": self._format_boolean(details.get('rtscts', False)),
            "DSR/DTR": self._format_boolean(details.get('dsrdtr', False))
        }
        return self._create_modern_card("Flow Control", "flow", flow_data, "control")
    
    def _create_modem_status_card(self, details: dict) -> QWidget:
        """Create Modem Status card with signal indicators"""
        modem_status = details.get("modem_status", {})
        if isinstance(modem_status, dict):
            status_data = {
                signal: self._format_signal_status(value) 
                for signal, value in modem_status.items()
            }
            return self._create_modern_card("Modem Status", "signal", status_data, "status")
        else:
            return self._create_modern_card("Modem Status", "signal", 
                                           {"Status": "Not available"}, "status")
    
    def _create_buffer_status_card(self, details: dict) -> QWidget:
        """Create Buffer Status card with byte counts"""
        buffer_data = {}
        if "in_waiting" in details:
            buffer_data["Input Buffer"] = f"{details['in_waiting']} bytes"
        if details.get("out_waiting") != 'N/A':
            buffer_data["Output Buffer"] = f"{details['out_waiting']} bytes"
        
        return self._create_modern_card("Buffer Status", "buffer", buffer_data, "info")
    
    def _display_test_results_modern(self, results: dict):
        """Display test results using Windows-native table"""
        if not results:
            self._show_error_message("No test results received")
            return
        
        status = results.get('status', 'Unknown')
        message = results.get('message', 'No message provided')
        details = results.get('details', {})
        is_success = status == 'Available'
        
        self._clear_results()
        
        # Status header card (keep existing)
        if is_success:
            self._update_status_indicator("success")
            status_card = self._create_status_card(
                "success", 
                "Port Available",
                "All diagnostics completed successfully",
                AppColors.SUCCESS_PRIMARY
            )
        else:
            self._update_status_indicator("error")
            error_msg = details.get('error', 'Unknown error')
            status_card = self._create_status_card(
                "error",
                "Port Error", 
                error_msg,
                AppColors.ERROR_PRIMARY
            )
        
        # Insert status card above the table for proper visual hierarchy
        table_index = self.results_layout.indexOf(self.results_table)
        self.results_layout.insertWidget(table_index, status_card)
        self.status_widgets.append(status_card)
        
        # Show and populate table for successful tests
        if is_success and details:
            # Show table after status card for proper ordering
            self.results_table.setVisible(True)
            
            # Port Configuration section
            self._add_section_header("⚙️ Port Configuration")
            self._add_property_row("Data Bits", details.get('bytesize', 'N/A'))
            self._add_property_row("Parity", details.get('parity', 'N/A'))
            self._add_property_row("Stop Bits", details.get('stopbits', 'N/A'))
            self._add_property_row("Timeout", f"{details.get('timeout', 'N/A')}s")
            
            # Flow Control section
            self._add_section_header("🔄 Flow Control")
            self._add_property_row("XON/XOFF", self._format_boolean(details.get('xonxoff', False)))
            self._add_property_row("RTS/CTS", self._format_boolean(details.get('rtscts', False)))
            self._add_property_row("DSR/DTR", self._format_boolean(details.get('dsrdtr', False)))
            
            # Modem Status section
            modem_status = details.get("modem_status", {})
            if isinstance(modem_status, dict) and modem_status:
                self._add_section_header("📡 Modem Status")
                for signal, value in modem_status.items():
                    self._add_property_row(signal, self._format_signal_status(value))
            
            # Buffer Status section
            if "in_waiting" in details or details.get("out_waiting") != 'N/A':
                self._add_section_header("📊 Buffer Status")
                if "in_waiting" in details:
                    self._add_property_row("Input Buffer", f"{details['in_waiting']} bytes")
                if details.get("out_waiting") != 'N/A':
                    self._add_property_row("Output Buffer", f"{details['out_waiting']} bytes")
            
            # Advanced Timeouts section
            if (details.get("write_timeout") != 'N/A' or 
                details.get("inter_byte_timeout") != 'N/A'):
                self._add_section_header("⏱️ Advanced Timeouts")
                if details.get("write_timeout") != 'N/A':
                    self._add_property_row("Write Timeout", f"{details['write_timeout']}s")
                if details.get("inter_byte_timeout") != 'N/A':
                    self._add_property_row("Inter-byte Timeout", f"{details['inter_byte_timeout']}s")
        
        # Hide header after successful test completion to maximize results view
        if is_success and details:
            self._hide_header_for_results()
    
    def _display_test_results(self, results: dict):
        """Display test results using modern card-based approach"""
        # Use the new modern card system
        self._display_test_results_modern(results)
    
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
        # Insert error card above the table
        table_index = self.results_layout.indexOf(self.results_table)
        self.results_layout.insertWidget(table_index, error_card)
        self.status_widgets.append(error_card)
        
        # Keep header visible for errors so user can easily retry