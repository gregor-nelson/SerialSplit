#!/usr/bin/env python3
"""
Enhanced Port Scan Dialog for Hub4com GUI
Handles port scanning, display, and export functionality with modern Windows-style UI
"""

import json
from typing import Optional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QGroupBox, QTextEdit,
                             QMessageBox, QFileDialog, QHeaderView, QWidget, QFrame,
                             QSplitter, QScrollArea)
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QColor

from core.core import (ResponsiveWindowManager, SerialPortInfo, PortScanner, 
                           WINREG_AVAILABLE)
from ui.theme.theme import AppFonts, AppColors, ThemeManager, AppStyles, AppDimensions


class PortScanDialog(QDialog):
    """Dialog for displaying scanned ports with custom SVG icons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ports = []
        self.scanner = None
        
        # Get window configuration from ResponsiveWindowManager
        self.window_config = ResponsiveWindowManager.calculate_dialog_config(800, 500)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the enhanced user interface with modern styling"""
        self.setWindowTitle("Serial Port Scanner")
        
        # Apply enhanced window configuration matching help dialog
        self.setMaximumSize(1280, 768)
        self.resize(1000, 600)
        self.setMinimumSize(QSize(800, 500))
        
        # Apply dialog styling consistent with help dialog
        ThemeManager.style_dialog(self)
        
        # Main layout with no margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section (similar to help dialog)
        header_widget = self.create_header_section()
        main_layout.addWidget(header_widget)
        
        # Add separator like help dialog
        main_layout.addWidget(ThemeManager.create_separator("horizontal"))
        
        # Content section with splitter layout
        content_widget = self.create_content_section()
        main_layout.addWidget(content_widget)
        
        # Auto-scan on startup
        QTimer.singleShot(100, self.scan_ports)
        
    def create_header_section(self) -> QWidget:
        """Create header section with title and action buttons"""
        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
                border-bottom: 1px solid {AppColors.BORDER_LIGHT};
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title_label = QLabel("Port Scanner")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 18pt;
                font-weight: 600;
                color: {AppColors.TEXT_DEFAULT};
                margin: 0;
                padding: 0;
                letter-spacing: -0.5px;
            }}
        """)
        title_layout.addWidget(title_label)
        
        self.status_label = QLabel("Ready to scan for available serial ports")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 10pt;
                color: {AppColors.TEXT_DISABLED};
                margin: 0;
                padding: 0;
                font-weight: 400;
            }}
        """)
        title_layout.addWidget(self.status_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Action buttons section with consistent spacing
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        # Scan button with primary styling
        self.scan_btn = ThemeManager.create_button(
            "Scan Ports", 
            self.scan_ports,
            "primary"
        )
        self.scan_btn.setToolTip("Scan for available serial ports")
        actions_layout.addWidget(self.scan_btn)
        
        # Export button with secondary styling
        self.export_btn = ThemeManager.create_button(
            "Export Results", 
            self.export_ports,
            "secondary"
        )
        self.export_btn.setToolTip("Export port information to JSON file")
        self.export_btn.setEnabled(False)  # Disabled until scan completes
        actions_layout.addWidget(self.export_btn)
        
        layout.addLayout(actions_layout)
        return header
        
    def create_content_section(self) -> QWidget:
        """Create main content area with splitter layout like help dialog"""
        content_widget = QWidget()
        layout = QHBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter for responsive layout
        splitter = ThemeManager.create_splitter(Qt.Orientation.Horizontal)
        
        # Left panel - Port list/table
        ports_widget = self.create_ports_panel()
        splitter.addWidget(ports_widget)
        
        # Right panel - Details display
        details_widget = self.create_details_panel()
        splitter.addWidget(details_widget)
        
        # Configure splitter proportions to match help dialog
        splitter.setStretchFactor(0, 1)  # Ports table takes more space
        splitter.setStretchFactor(1, 0)  # Details panel fixed width
        splitter.setSizes([680, 320])
        
        layout.addWidget(splitter)
        return content_widget
        
    def create_ports_panel(self) -> QWidget:
        """Create the ports table panel"""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 16, 20)
        layout.setSpacing(16)
        
        # Panel header with enhanced styling
        header_label = QLabel("Available Serial Ports")
        header_label.setStyleSheet(f"""
            QLabel {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 14pt;
                font-weight: 600;
                color: {AppColors.TEXT_DEFAULT};
                margin-bottom: 12px;
                letter-spacing: -0.3px;
            }}
        """)
        layout.addWidget(header_label)
        
        # Enhanced table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Port", "Type", "Device Name", "Description"])
        
        # Professional table styling matching help dialog
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
                border: 1px solid {AppColors.BORDER_LIGHT};
                selection-background-color: {AppColors.SELECTION_BG};
                gridline-color: transparent;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                outline: none;
            }}
            QTableWidget::item {{
                padding: 12px 16px;
                border: none;
                border-bottom: 1px solid {AppColors.BORDER_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
            }}
            QTableWidget::item:selected {{
                background-color: {AppColors.SELECTION_BG};
                color: {AppColors.SELECTION_TEXT};
            }}
            QTableWidget::item:hover:!selected {{
                background-color: {AppColors.BUTTON_HOVER};
            }}
            QTableWidget::item:first {{
            }}
            QHeaderView::section {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
                font-weight: 600;
                font-size: 11pt;
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid {AppColors.BORDER_DEFAULT};
                border-right: 1px solid {AppColors.BORDER_LIGHT};
            }}
            QHeaderView::section:first {{
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            QHeaderView::section:hover {{
                background-color: {AppColors.BUTTON_HOVER};
            }}
        """)
        
        # Enhanced column configuration
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 85)
        self.table.setColumnWidth(1, 140)
        
        # Hide vertical header for cleaner look
        self.table.verticalHeader().setVisible(False)
        
        # Professional table configuration
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)  # Using hover effects instead
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        layout.addWidget(self.table)
        
        # Connect table selection
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        return panel
        
    def create_details_panel(self) -> QWidget:
        """Create the details panel similar to help dialog's content area"""
        panel = QWidget()
        panel.setMinimumWidth(240)
        panel.setMaximumWidth(320)
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border-left: 1px solid {AppColors.BORDER_LIGHT};
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Panel header with enhanced styling
        header_label = QLabel("Port Details")
        header_label.setStyleSheet(f"""
            QLabel {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 14pt;
                font-weight: 600;
                color: {AppColors.TEXT_DEFAULT};
                margin-bottom: 12px;
                letter-spacing: -0.3px;
            }}
        """)
        layout.addWidget(header_label)
        
        # Professional details text area with rich formatting
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppColors.BACKGROUND_WHITE};
                border: 1px solid {AppColors.BORDER_LIGHT};
                padding: 16px;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 10pt;
                line-height: 1.4;
                color: {AppColors.TEXT_DEFAULT};
            }}
            QTextEdit:focus {{
                border-color: {AppColors.ACCENT_BLUE};
                outline: none;
            }}
        """)
        self.details_text.setPlaceholderText("Select a port to view detailed information...")
        layout.addWidget(self.details_text)
        
        layout.addStretch()
        return panel
    
    def scan_ports(self):
        """Start port scanning with enhanced feedback"""
        self.scan_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.status_label.setText("Scanning for serial ports...")
        # Scanning state styling
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 10pt;
                color: {AppColors.ACCENT_BLUE};
                margin: 0;
                padding: 0;
                font-weight: 500;
            }}
        """)
        
        # Clear previous results
        self.table.setRowCount(0)
        self.details_text.clear()
        
        # Check if winreg is available
        if not WINREG_AVAILABLE:
            QMessageBox.warning(
                self,
                "Limited Functionality", 
                "Windows registry access is not available.\nPort scanning will be limited to basic detection."
            )
            self.on_scan_completed([])  # Empty list
            return
        
        try:
            self.scanner = PortScanner()
            self.scanner.scan_completed.connect(self.on_scan_completed)
            self.scanner.scan_progress.connect(self.on_scan_progress)
            self.scanner.finished.connect(lambda: setattr(self, 'scanner', None))
            self.scanner.start()
        except Exception as e:
            self.status_label.setText(f"Scan failed: {str(e)}")
            # Error state styling
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: 10pt;
                    color: {AppColors.ERROR_PRIMARY};
                    margin: 0;
                    padding: 0;
                    font-weight: 500;
                }}
            """)
            self.scan_btn.setEnabled(True)
    
    def on_scan_progress(self, message):
        """Update scan progress with enhanced messaging"""
        self.status_label.setText(f"Scanning... {message}")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 10pt;
                color: {AppColors.ACCENT_BLUE};
                margin: 0;
                padding: 0;
                font-weight: 500;
            }}
        """)
    
    def on_scan_completed(self, ports):
        """Handle completed port scan with enhanced feedback"""
        self.ports = ports
        self.populate_table()
        self.scan_btn.setEnabled(True)
        self.export_btn.setEnabled(len(ports) > 0)
        
        if ports:
            port_types = {}
            for port in ports:
                port_types[port.port_type] = port_types.get(port.port_type, 0) + 1
            
            type_summary = ", ".join([f"{count} {type_name}" for type_name, count in port_types.items()])
            self.status_label.setText(f"Scan complete: {len(ports)} ports found ({type_summary})")
            # Success state styling
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: 10pt;
                    color: {AppColors.TEXT_DEFAULT};
                    margin: 0;
                    padding: 0;
                    font-weight: 500;
                }}
            """)
        else:
            self.status_label.setText("Scan complete: No COM devices detected")
            # Warning state styling
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: 10pt;
                    color: {AppColors.TEXT_DISABLED};
                    margin: 0;
                    padding: 0;
                    font-weight: 400;
                }}
            """)
    
    def populate_table(self):
        """Populate the ports table with enhanced styling"""
        self.table.setRowCount(len(self.ports))
        
        if not self.ports:
            # Show professionally styled message when no ports detected
            self.table.setRowCount(1)
            item = QTableWidgetItem("No COM devices detected")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFont(AppFonts.get_font("default", 11, italic=True))
            item.setForeground(QColor(AppColors.TEXT_DISABLED))
            # Enhanced styling for empty state
            item.setData(Qt.ItemDataRole.BackgroundRole, QColor(AppColors.BACKGROUND_LIGHT))
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 4)
            self.table.setRowHeight(0, 60)  # Taller row for better visual impact
            return
        
        for row, port in enumerate(self.ports):
            # Set consistent row height for professional appearance
            self.table.setRowHeight(row, 48)
            
            # Port name with enhanced styling
            port_item = QTableWidgetItem(port.port_name)
            self.table.setItem(row, 0, port_item)
            
            # Port type with enhanced visual indicators
            type_item = QTableWidgetItem(port.port_type)
            
            # Professional color coding with refined contrast
            if port.port_type == "Physical":
                type_item.setBackground(QColor("#E8F4FD"))  # Softer blue
                type_item.setForeground(QColor("#1565C0"))  # Professional blue
            elif port.port_type == "Virtual (Moxa)":
                type_item.setBackground(QColor("#F8E8FF"))  # Softer purple
                type_item.setForeground(QColor("#8E24AA"))  # Professional purple
            elif "Virtual" in port.port_type:
                type_item.setBackground(QColor("#EDF7ED"))  # Softer green
                type_item.setForeground(QColor("#2E7D32"))  # Professional green
            else:
                type_item.setBackground(QColor("#FFF8E1"))  # Softer orange
                type_item.setForeground(QColor("#EF6C00"))  # Professional orange
                
            self.table.setItem(row, 1, type_item)
            
            # Device name with truncation handling
            device_name = port.device_name
            if len(device_name) > 40:
                device_name = device_name[:37] + "..."
            device_item = QTableWidgetItem(device_name)
            device_item.setToolTip(port.device_name)  # Full name in tooltip
            self.table.setItem(row, 2, device_item)
            
            # Description with truncation handling
            description = port.description
            if len(description) > 50:
                description = description[:47] + "..."
            desc_item = QTableWidgetItem(description)
            desc_item.setToolTip(port.description)  # Full description in tooltip
            self.table.setItem(row, 3, desc_item)
        
        # Auto-select first port if available
        if self.ports:
            self.table.selectRow(0)
    
    def on_selection_changed(self):
        """Handle table selection change"""
        current_row = self.table.currentRow()
        if 0 <= current_row < len(self.ports):
            port = self.ports[current_row]
            self.show_port_details(port)
    
    def show_port_details(self, port: SerialPortInfo):
        """Show detailed information about selected port with rich formatting"""
        # Create professional HTML-formatted details using HTMLTheme
        port_type_class = "port-type-physical" if port.port_type == "Physical" else "port-type-virtual"
        
        html_content = f"""
        {HTMLTheme.get_styles()}
        
        <div class="section-header">Port Information</div>
        
        <div class="field">
            <span class="field-label">Port Name:</span>
            <span class="field-value"><strong>{port.port_name}</strong></span>
        </div>
        
        <div class="field">
            <span class="field-label">Type:</span>
            <span class="{port_type_class}">{port.port_type}</span>
        </div>
        
        <div class="field">
            <span class="field-label">Registry Key:</span>
            <span class="field-value">{port.registry_key}</span>
        </div>
        
        <div class="field">
            <span class="field-label">Description:</span>
            <span class="field-value">{port.description}</span>
        </div>
        """
        
        if port.is_moxa and port.moxa_details:
            html_content += f"""
            <div class="moxa-section">
                <div class="section-header">Moxa Device Information</div>
                
                <div class="field">
                    <span class="field-label">Driver:</span>
                    <span class="field-value">{port.moxa_details['driver_name']}</span>
                </div>
                
                <div class="field">
                    <span class="field-label">Port Number:</span>
                    <span class="field-value">{port.moxa_details['port_number']}</span>
                </div>
                
                <div class="field">
                    <span class="field-label">Connection:</span>
                    <span class="field-value">{port.moxa_details['connection_type']}</span>
                </div>
                
                <div class="section-header">Recommendations</div>
            """
            
            for rec in port.moxa_details['recommendations']:
                html_content += f'<div class="recommendation">• {rec}</div>'
                
            html_content += "</div>"
        
        self.details_text.setHtml(html_content)
    
    def export_ports(self):
        """Export port information to JSON"""
        if not self.ports:
            QMessageBox.information(self, "No Data", "No ports to export. Please scan first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Port Information",
            "serial_ports.json",
            "JSON files (*.json);;All files (*.*)"
        )
        
        if file_path:
            try:
                # Convert to JSON-serializable format
                export_data = []
                for port in self.ports:
                    port_data = {
                        "port_name": port.port_name,
                        "device_name": port.device_name,
                        "port_type": port.port_type,
                        "registry_key": port.registry_key,
                        "description": port.description,
                        "is_moxa": port.is_moxa,
                        "moxa_details": port.moxa_details
                    }
                    export_data.append(port_data)
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                QMessageBox.information(self, "Export Complete", f"Port information exported to:\n{file_path}")
            
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def get_selected_port(self) -> Optional[str]:
        """Get the currently selected port name"""
        current_row = self.table.currentRow()
        if 0 <= current_row < len(self.ports):
            return self.ports[current_row].port_name
        return None