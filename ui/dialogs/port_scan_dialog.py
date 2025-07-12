#!/usr/bin/env python3
"""
Minimal Port Scan Dialog for Hub4com GUI
Clean, compact design matching terminal dialog aesthetic
"""

from typing import Optional, List

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QListWidget, QListWidgetItem, QWidget, QGroupBox, QSplitter,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QColor, QFont

from core.core import (SerialPortInfo, PortScanner, PortStatus, WINREG_AVAILABLE)
from ui.theme.theme import AppFonts, AppColors, ThemeManager, AppDimensions, AppStyles, IconManager
from ui.theme.icons.icons import AppIcons


class PortScanDialog(QDialog):
    """Minimal port scanner dialog with clean table design"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ports = []
        self.scanner = None
        self.loading_indicators = {}  # Track loading state per column
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI matching primary GUI design language"""
        self.setWindowTitle("Port Scanner")
        
        # Responsive dialog size matching main GUI patterns
        self.setMinimumSize(QSize(600, 450))
        self.resize(800, 500)
        
        # Apply dialog styling consistent with primary GUI
        ThemeManager.style_dialog(self)
        
        # Main layout with standard margins
        main_layout = QVBoxLayout(self)
        margins = ThemeManager.get_standard_margins()
        main_layout.setContentsMargins(*margins)
        main_layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # Create main content using GroupBox pattern like primary GUI
        self.create_main_section(main_layout)
        
        # Auto-scan on startup
        QTimer.singleShot(100, self.scan_ports)
        
    def create_main_section(self, main_layout):
        """Create main section using GroupBox pattern from primary GUI"""
        # Create GroupBox like primary GUI sections
        group, layout = self._create_groupbox_with_layout("Port Discovery")
        
        # Create control panel with buttons (matching primary GUI pattern)
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # Create port display area
        ports_area = self.create_ports_display()
        layout.addWidget(ports_area)
        
        main_layout.addWidget(group)
        
    def _create_groupbox_with_layout(self, title: str, layout_class=QVBoxLayout) -> tuple:
        """Create styled groupbox matching primary GUI pattern"""
        group = ThemeManager.create_groupbox(title)
        
        # Apply same styling as primary GUI groupboxes
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: normal;
                color: {AppColors.TEXT_DEFAULT};
                border: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {AppColors.BORDER_DEFAULT};
                margin-top: 12px;
                padding-top: 2px;
                background-color: {AppColors.BACKGROUND_LIGHT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {AppDimensions.SPACING_LARGE}px;
                padding: 0 {AppDimensions.SPACING_SMALL}px;
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
            }}
        """)
        
        layout = layout_class(group) if layout_class else None
        if layout:
            layout.setSpacing(AppDimensions.SPACING_MEDIUM)
            layout.setContentsMargins(8, 4, 8, 8)
        return group, layout
        
    def create_control_panel(self) -> QWidget:
        """Create control panel with buttons matching primary GUI style"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create single scan button matching primary GUI button style
        self.scan_btn = self._create_gui_style_button("Scan Ports", "REFRESH", self.scan_ports)
        self.scan_btn.setToolTip("Scan for available serial ports with progressive loading")
        
        # Status label for current phase
        self.phase_label = QLabel("Ready")
        self.phase_label.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
        self.phase_label.setStyleSheet(f"color: {AppColors.TEXT_DEFAULT}; font-style: italic;")
        
        layout.addWidget(self.scan_btn)
        layout.addWidget(self.phase_label)
        layout.addStretch()
        
        return panel
        
    def _create_gui_style_button(self, text: str, icon_name: str, callback) -> QPushButton:
        """Create button matching primary GUI style exactly"""
        btn = QPushButton(text)
        
        # Apply same sizing as primary GUI
        btn.setMinimumWidth(AppDimensions.BUTTON_MIN_WIDTH)
        btn.setMaximumWidth(AppDimensions.BUTTON_MAX_WIDTH)
        btn.setMinimumHeight(AppDimensions.BUTTON_HEIGHT_CONTROL)
        btn.setMaximumHeight(AppDimensions.BUTTON_HEIGHT_CONTROL)
        btn.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
        
        # Add SVG icon matching primary GUI pattern
        try:
            icon_template = getattr(AppIcons, icon_name, None)
            if icon_template:
                icon_size = QSize(16, 16)
                icon = IconManager.create_svg_icon(icon_template, AppColors.ICON_DEFAULT, icon_size)
                btn.setIcon(icon)
                btn.setIconSize(icon_size)
        except Exception:
            pass
        
        # Apply primary GUI button styling
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.BUTTON_BLUE_LIGHT};
                border: 1px solid {AppColors.BUTTON_BLUE_BORDER};
                padding: {AppDimensions.PADDING_BUTTON_DETAILED};
                text-align: left;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.FONT_SIZE_SMALL}pt;
                color: {AppColors.CONTROL_PANEL_TEXT};
                line-height: 1.2;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_BLUE_BORDER};
                border-color: {AppColors.BUTTON_BLUE_BORDER_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_BLUE_BORDER_HOVER};
                border-color: {AppColors.BUTTON_BLUE_BORDER_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {AppColors.BUTTON_TRANSPARENT};
                color: {AppColors.TEXT_DISABLED};
                border-color: {AppColors.BUTTON_TRANSPARENT};
            }}
        """)
        
        btn.clicked.connect(callback)
        return btn
        
    def create_ports_display(self) -> QWidget:
        """Create ports display table matching primary GUI patterns"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Create table widget with professional styling
        self.port_table = QTableWidget()
        self.port_table.setColumnCount(8)
        self.port_table.setHorizontalHeaderLabels([
            "Port", "Type", "Manufacturer", "Status", "Location", 
            "Capabilities", "Last Activity", "Parameters"
        ])
        
        # Apply professional table styling
        self.port_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
                border: 1px solid {AppColors.BORDER_DEFAULT};
                selection-background-color: {AppColors.ACCENT_BLUE};
                gridline-color: transparent;
                font-family: "Consolas", monospace;
                font-size: 10pt;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border: none;
                border-bottom: 1px solid {AppColors.BORDER_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
            }}
            QTableWidget::item:selected {{
                background-color: {AppColors.ACCENT_BLUE};
                color: white;
            }}
            QTableWidget::item:hover:!selected {{
                background-color: {AppColors.BUTTON_HOVER};
            }}
            QHeaderView::section {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
                font-weight: 600;
                font-size: 11pt;
                padding: 8px 12px;
                border: none;
                border-bottom: 2px solid {AppColors.BORDER_DEFAULT};
                border-right: 1px solid {AppColors.BORDER_LIGHT};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            {AppStyles.scrollbar()}
        """)
        
        # Configure table columns - auto-resize to content
        header = self.port_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # Hide vertical header and configure selection
        self.port_table.verticalHeader().setVisible(False)
        self.port_table.setShowGrid(False)
        self.port_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.port_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        layout.addWidget(self.port_table)
        return container
        
    
    def scan_ports(self):
        """Start progressive port scanning with automatic complete scan"""
        # Disable scan button during scan
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Scanning...")
        self.phase_label.setText("Initializing...")
        
        # Clear previous results and loading indicators
        self.port_table.setRowCount(0)
        self.loading_indicators.clear()
        self.ports = []
        
        # Show initial loading state
        self.port_table.setRowCount(1)
        loading_item = QTableWidgetItem("Starting scan...")
        loading_item.setForeground(QColor(AppColors.ACCENT_BLUE))
        self.port_table.setItem(0, 0, loading_item)
        self.port_table.setSpan(0, 0, 1, 8)
        
        # Start actual scan after brief delay for UI update
        QTimer.singleShot(100, self.start_actual_scan)
    
    def start_actual_scan(self):
        """Start the actual scanning process with progressive loading"""
        # Check if winreg is available
        if not WINREG_AVAILABLE:
            self.on_scan_completed([])
            return
        
        try:
            # Always perform complete scan with progressive loading
            self.scanner = PortScanner(complete_scan=True)
            
            # Connect progressive loading signals
            self.scanner.port_basic_data.connect(self.on_port_basic_data)
            self.scanner.port_enhanced_data.connect(self.on_port_enhanced_data)
            self.scanner.port_status_data.connect(self.on_port_status_data)
            self.scanner.scan_phase_changed.connect(self.on_scan_phase_changed)
            
            # Connect traditional signals
            self.scanner.scan_completed.connect(self.on_scan_completed)
            self.scanner.scan_progress.connect(self.on_scan_progress)
            self.scanner.finished.connect(lambda: setattr(self, 'scanner', None))
            
            self.scanner.start()
            
        except Exception as e:
            # Show error in table
            self.port_table.setRowCount(1)
            error_item = QTableWidgetItem(f"Scan failed: {str(e)}")
            error_item.setForeground(QColor(AppColors.TEXT_DISABLED))
            self.port_table.setItem(0, 0, error_item)
            self.port_table.setSpan(0, 0, 1, 8)
            self._reset_scan_button()
    
    def on_scan_progress(self, message):
        """Update scan progress in the table"""
        if self.port_table.rowCount() > 0:
            item = self.port_table.item(0, 0)
            if item and "Scanning" in item.text():
                item.setText(f"Scanning... {message}")
    
    def on_port_basic_data(self, row: int, port_info: object):
        """Handle basic port data (Phase 1 - immediate)"""
        try:
            # Ensure we have enough rows and resize ports list
            if len(self.ports) <= row:
                self.ports.extend([None] * (row + 1 - len(self.ports)))
            
            self.ports[row] = port_info
            
            # If this is the first port, setup the table structure
            if row == 0:
                self._setup_progressive_table()
            
            # Populate basic columns (Port, Type) immediately
            self._populate_basic_columns(row, port_info)
            
        except Exception as e:
            print(f"Error handling basic data for row {row}: {str(e)}")
            self._handle_data_error(row, "basic", str(e))
    
    def on_port_enhanced_data(self, row: int, port_info: object):
        """Handle enhanced port data (Phase 2 - quick analysis)"""
        try:
            if row < len(self.ports):
                self.ports[row] = port_info
                self._populate_enhanced_columns(row, port_info)
        except Exception as e:
            print(f"Error handling enhanced data for row {row}: {str(e)}")
            self._handle_data_error(row, "enhanced", str(e))
    
    def on_port_status_data(self, row: int, port_info: object):
        """Handle complete port data (Phase 3 - detailed analysis)"""
        try:
            if row < len(self.ports):
                self.ports[row] = port_info
                self._populate_status_columns(row, port_info)
        except Exception as e:
            print(f"Error handling status data for row {row}: {str(e)}")
            self._handle_data_error(row, "status", str(e))
    
    def on_scan_phase_changed(self, phase: str):
        """Handle scan phase changes with enhanced feedback"""
        # Map phases to more user-friendly descriptions
        phase_map = {
            "Scanning registry...": "📋 Finding ports...",
            "Analyzing capabilities...": "🔍 Analyzing ports...", 
            "Checking port status...": "⚡ Checking status..."
        }
        
        display_phase = phase_map.get(phase, phase)
        self.phase_label.setText(display_phase)
    
    def on_scan_completed(self, ports):
        """Handle completed port scan"""
        self.ports = ports
        self._reset_scan_button()
        
        # Show completion status with port count
        port_count = len(ports) if ports else 0
        if port_count == 0:
            self.phase_label.setText("✅ No ports found")
        elif port_count == 1:
            self.phase_label.setText("✅ 1 port found")
        else:
            self.phase_label.setText(f"✅ {port_count} ports found")
        
    def _reset_scan_button(self):
        """Reset scan button to original state"""
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan Ports")
    
    def _setup_progressive_table(self):
        """Setup table for progressive loading"""
        # Clear any loading messages
        self.port_table.setRowCount(0)
        self.loading_indicators.clear()
    
    def _populate_basic_columns(self, row: int, port_info: object):
        """Populate basic columns (Port, Type) immediately"""
        # Ensure table has enough rows
        if self.port_table.rowCount() <= row:
            self.port_table.setRowCount(row + 1)
        
        # Port name (Column 0)
        port_item = QTableWidgetItem(port_info.port_name)
        port_item.setFont(QFont("Consolas", 10))
        port_item.setData(Qt.ItemDataRole.UserRole, port_info)
        self.port_table.setItem(row, 0, port_item)
        
        # Port type (Column 1)
        type_display = self._get_port_type_display(port_info)
        type_item = QTableWidgetItem(type_display)
        type_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
        self.port_table.setItem(row, 1, type_item)
        
        # Set loading indicators for other columns
        self._set_loading_indicators(row, [2, 3, 4, 5, 6, 7])
    
    def _populate_enhanced_columns(self, row: int, port_info: object):
        """Populate enhanced columns (Manufacturer, Location, Capabilities, Parameters)"""
        # Manufacturer (Column 2)
        manufacturer_item = QTableWidgetItem(port_info.manufacturer)
        manufacturer_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
        self.port_table.setItem(row, 2, manufacturer_item)
        
        # Location (Column 4)
        location_item = QTableWidgetItem(port_info.location)
        location_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
        self.port_table.setItem(row, 4, location_item)
        
        # Capabilities (Column 5)
        capabilities_text = self._format_capabilities(port_info.capabilities)
        capabilities_item = QTableWidgetItem(capabilities_text)
        capabilities_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
        capabilities_item.setToolTip(", ".join(port_info.capabilities))
        self.port_table.setItem(row, 5, capabilities_item)
        
        # Parameters (Column 7)
        params_text = self._get_port_parameters(port_info)
        params_item = QTableWidgetItem(params_text)
        params_item.setFont(QFont("Consolas", 9))
        self.port_table.setItem(row, 7, params_item)
        
        # Set loading indicator for status column (will be updated in phase 3)
        self._set_loading_indicators(row, [3])  # Status still loading
    
    def _populate_status_columns(self, row: int, port_info: object):
        """Populate status column - complete scan only"""
        # Status with color coding (Column 3)
        status_text, status_color = self._get_enhanced_port_status(port_info)
        status_item = QTableWidgetItem(status_text)
        status_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
        status_item.setForeground(QColor(status_color))
        self.port_table.setItem(row, 3, status_item)
    
    
    def _set_loading_indicators(self, row: int, columns: list):
        """Set loading indicators for specified columns"""
        for col in columns:
            loading_item = QTableWidgetItem("...")
            loading_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
            loading_item.setForeground(QColor(AppColors.ACCENT_BLUE))
            loading_item.setToolTip("Loading...")
            self.port_table.setItem(row, col, loading_item)
    
    def _handle_data_error(self, row: int, phase: str, error_msg: str):
        """Handle errors during progressive data loading"""
        try:
            # Ensure table has enough rows
            if self.port_table.rowCount() <= row:
                self.port_table.setRowCount(row + 1)
            
            # Show error indicator based on phase
            if phase == "basic":
                # Critical error - show in port name column
                error_item = QTableWidgetItem(f"Error (Row {row})")
                error_item.setForeground(QColor("#dc3545"))
                error_item.setToolTip(f"Basic scan failed: {error_msg}")
                self.port_table.setItem(row, 0, error_item)
                
                # Fill other columns with error indicators
                for col in range(1, 8):
                    err_item = QTableWidgetItem("Error")
                    err_item.setForeground(QColor("#dc3545"))
                    err_item.setToolTip(f"Data unavailable due to scan error: {error_msg}")
                    self.port_table.setItem(row, col, err_item)
                    
            elif phase == "enhanced":
                # Non-critical error - show partial data
                for col in [2, 4, 5, 7]:  # Manufacturer, Location, Capabilities, Parameters
                    err_item = QTableWidgetItem("Error")
                    err_item.setForeground(QColor("#ffa500"))
                    err_item.setToolTip(f"Enhanced data failed: {error_msg}")
                    self.port_table.setItem(row, col, err_item)
                    
            elif phase == "status":
                # Status error - show as unavailable
                err_item = QTableWidgetItem("N/A")
                err_item.setForeground(QColor("#6c757d"))
                err_item.setToolTip(f"Status data failed: {error_msg}")
                self.port_table.setItem(row, 3, err_item)  # Status column only
                    
        except Exception as e:
            print(f"Error in error handler for row {row}, phase {phase}: {str(e)}")
    
    def populate_table(self):
        """Populate the table with professional port information"""
        self.port_table.setRowCount(len(self.ports))
        
        if not self.ports:
            # Show professional message when no ports detected
            self.port_table.setRowCount(1)
            item = QTableWidgetItem("No ports available")
            item.setForeground(QColor(AppColors.TEXT_DISABLED))
            item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL, italic=True))
            self.port_table.setItem(0, 0, item)
            self.port_table.setSpan(0, 0, 1, 8)
            return
        
        # Populate table with enhanced port information
        for row, port in enumerate(self.ports):
            # Port name (Column 0)
            port_item = QTableWidgetItem(port.port_name)
            port_item.setFont(QFont("Consolas", 10))
            self.port_table.setItem(row, 0, port_item)
            
            # Port type (Column 1)
            type_short = self._get_port_type_display(port)
            type_item = QTableWidgetItem(type_short)
            type_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
            self.port_table.setItem(row, 1, type_item)
            
            # Manufacturer (Column 2)
            manufacturer_item = QTableWidgetItem(port.manufacturer)
            manufacturer_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
            self.port_table.setItem(row, 2, manufacturer_item)
            
            # Status with color coding (Column 3)
            status_text, status_color = self._get_enhanced_port_status(port)
            status_item = QTableWidgetItem(status_text)
            status_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
            status_item.setForeground(QColor(status_color))
            self.port_table.setItem(row, 3, status_item)
            
            # Location (Column 4)
            location_item = QTableWidgetItem(port.location)
            location_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
            self.port_table.setItem(row, 4, location_item)
            
            # Capabilities (Column 5)
            capabilities_text = self._format_capabilities(port.capabilities)
            capabilities_item = QTableWidgetItem(capabilities_text)
            capabilities_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
            capabilities_item.setToolTip(", ".join(port.capabilities))
            self.port_table.setItem(row, 5, capabilities_item)
            
            # Last Activity (Column 6)
            activity_text = self._format_last_activity(port.last_activity)
            activity_item = QTableWidgetItem(activity_text)
            activity_item.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
            activity_item.setForeground(QColor(AppColors.TEXT_DEFAULT))
            self.port_table.setItem(row, 6, activity_item)
            
            # Parameters (Column 7)
            params_text = self._get_port_parameters(port)
            params_item = QTableWidgetItem(params_text)
            params_item.setFont(QFont("Consolas", 9))
            params_item.setForeground(QColor(AppColors.TEXT_DEFAULT))
            self.port_table.setItem(row, 7, params_item)
            
            # Store port data for later use
            port_item.setData(Qt.ItemDataRole.UserRole, port)
    
    def get_selected_port(self) -> Optional[str]:
        """Get the currently selected port name"""
        current_row = self.port_table.currentRow()
        if 0 <= current_row < self.port_table.rowCount():
            port_item = self.port_table.item(current_row, 0)  # Port name is in column 0
            if port_item:
                port_data = port_item.data(Qt.ItemDataRole.UserRole)
                if port_data:
                    return port_data.port_name
        return None
        
    def _get_port_type_display(self, port: SerialPortInfo) -> str:
        """Get short port type for display"""
        if port.port_type == "Physical":
            return "Hardware"
        elif "COM0COM" in port.port_type:
            return "com0com"
        elif "Moxa" in port.port_type:
            return "Moxa"
        elif "Virtual" in port.port_type:
            return "Virtual"
        else:
            return "Other"
    
    def _get_enhanced_port_status(self, port: SerialPortInfo) -> tuple[str, str]:
        """Get enhanced status text and color for port"""
        if port.status == PortStatus.AVAILABLE:
            return "Available", AppColors.SUCCESS_PRIMARY
        elif port.status == PortStatus.IN_USE:
            return "In Use", "#ff8c00"  # Orange
        elif port.status == PortStatus.BUSY:
            return "Busy", "#ffa500"  # Orange
        elif port.status == PortStatus.ERROR:
            return "Error", "#dc3545"  # Red
        elif port.status == PortStatus.RESERVED:
            return "Reserved", "#6c757d"  # Gray
        else:
            return "Unknown", AppColors.TEXT_DISABLED
    
    def _format_capabilities(self, capabilities: List[str]) -> str:
        """Format capabilities list for compact display"""
        if not capabilities:
            return "Standard"
        
        # Use abbreviations for common capabilities
        abbrev_map = {
            "Hardware Flow Control": "HW Flow",
            "High Speed": "HS",
            "USB": "USB",
            "Multi-port": "Multi",
            "Network Serial": "Network",
            "TCP/IP": "TCP",
            "Null Modem": "Null",
            "Configurable": "Config",
            "Virtual": "Virtual"
        }
        
        # Convert to abbreviations and join
        abbreviated = []
        for cap in capabilities[:3]:  # Show max 3 capabilities
            abbreviated.append(abbrev_map.get(cap, cap))
        
        result = ", ".join(abbreviated)
        if len(capabilities) > 3:
            result += f" +{len(capabilities) - 3}"
        
        return result
    
    def _format_last_activity(self, last_activity) -> str:
        """Format last activity timestamp"""
        if last_activity is None:
            return "Never"
        
        from datetime import datetime
        now = datetime.now()
        diff = now - last_activity
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"
    
    def _get_port_parameters(self, port: SerialPortInfo) -> str:
        """Get formatted parameters string for port"""
        if port.port_type == "Physical":
            return "Auto 8N1"  # Hardware ports auto-configure
        elif "com0com" in port.port_type.lower():
            return "115200 8N1"  # com0com default settings
        else:
            return "Default 8N1"  # Other virtual ports