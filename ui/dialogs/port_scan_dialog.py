#!/usr/bin/env python3
"""
Port Scan Dialog for Hub4com GUI
Handles port scanning, display, and export functionality
Updated to use custom SVG icons instead of emojis
"""

import json
from typing import Optional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QGroupBox, QTextEdit,
                             QMessageBox, QFileDialog, QHeaderView)
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QColor

from core.components import (ResponsiveWindowManager, SerialPortInfo, PortScanner, 
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
        """Initialize the user interface"""
        self.setWindowTitle("Serial Port Scanner")
        
        # Apply window configuration from ResponsiveWindowManager
        self.setGeometry(
            self.window_config.x,
            self.window_config.y,
            self.window_config.width,
            self.window_config.height
        )
        self.setMinimumSize(QSize(self.window_config.min_width, self.window_config.min_height))
        
        layout = QVBoxLayout(self)
        
        # Scan button row
        scan_layout = QHBoxLayout()
        
        # Create refresh button with custom SVG icon
        self.scan_btn = ThemeManager.create_icon_button(
            "refresh", 
            "Scan for available serial ports",
            "medium"
        )
        self.scan_btn.clicked.connect(self.scan_ports)
        scan_layout.addWidget(self.scan_btn)
        
        # Create export button with custom SVG icon
        self.export_btn = ThemeManager.create_icon_button(
            "export",
            "Export port information to JSON file",
            "medium"
        )
        self.export_btn.clicked.connect(self.export_ports)
        scan_layout.addWidget(self.export_btn)
        
        scan_layout.addStretch()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(AppStyles.label())
        scan_layout.addWidget(self.status_label)
        
        layout.addLayout(scan_layout)
        
        # Ports table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Port", "Type", "Device Name", "Description"])
        self.table.setStyleSheet(AppStyles.tablewidget())
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 120)
        
        layout.addWidget(self.table)
        
        # Details section
        details_group = QGroupBox("Port Details")
        details_group.setStyleSheet(AppStyles.groupbox())
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(AppDimensions.HEIGHT_TEXT_SMALL)
        self.details_text.setFont(AppFonts.CONSOLE)
        self.details_text.setStyleSheet(AppStyles.textedit())
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        # Connect table selection
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Auto-scan on startup
        QTimer.singleShot(100, self.scan_ports)
    
    def scan_ports(self):
        """Start port scanning"""
        self.scan_btn.setEnabled(False)
        self.status_label.setText("Scanning...")
        
        # Check if winreg is available
        if not WINREG_AVAILABLE:
            QMessageBox.warning(
                self,
                "Limited Functionality", 
                "Windows registry access is not available.\nPort scanning will be limited."
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
            self.status_label.setText(f"Error: {str(e)}")
            self.scan_btn.setEnabled(True)
    
    def on_scan_progress(self, message):
        """Update scan progress"""
        self.status_label.setText(message)
    
    def on_scan_completed(self, ports):
        """Handle completed port scan"""
        self.ports = ports
        self.populate_table()
        self.scan_btn.setEnabled(True)
        
        if ports:
            self.status_label.setText(f"Found {len(ports)} ports")
        else:
            self.status_label.setText("No COM devices detected")
    
    def populate_table(self):
        """Populate the ports table"""
        self.table.setRowCount(len(self.ports))
        
        if not self.ports:
            # Show message when no ports detected
            self.table.setRowCount(1)
            item = QTableWidgetItem("No COM devices detected")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 4)
            return
        
        for row, port in enumerate(self.ports):
            # Port name
            item = QTableWidgetItem(port.port_name)
            self.table.setItem(row, 0, item)
            
            # Port type with color coding
            type_item = QTableWidgetItem(port.port_type)
            if port.port_type == "Physical":
                type_item.setBackground(QColor(AppColors.ACCENT_BLUE))
            elif port.port_type == "Virtual (Moxa)":
                type_item.setBackground(QColor(AppColors.ACCENT_PURPLE))
            else:
                type_item.setBackground(QColor(AppColors.PAIR_HIGHLIGHT))
            self.table.setItem(row, 1, type_item)
            
            # Device name
            device_item = QTableWidgetItem(port.device_name)
            self.table.setItem(row, 2, device_item)
            
            # Description
            desc_item = QTableWidgetItem(port.description)
            self.table.setItem(row, 3, desc_item)
    
    def on_selection_changed(self):
        """Handle table selection change"""
        current_row = self.table.currentRow()
        if 0 <= current_row < len(self.ports):
            port = self.ports[current_row]
            self.show_port_details(port)
    
    def show_port_details(self, port: SerialPortInfo):
        """Show detailed information about selected port"""
        details = f"Port: {port.port_name}\n"
        details += f"Type: {port.port_type}\n"
        details += f"Registry Key: {port.registry_key}\n"
        details += f"Description: {port.description}\n"
        
        if port.is_moxa and port.moxa_details:
            details += "\nMoxa-Specific Information:\n"
            details += f"• Driver Name: {port.moxa_details['driver_name']}\n"
            details += f"• Port Number: {port.moxa_details['port_number']}\n"
            details += f"• Connection Type: {port.moxa_details['connection_type']}\n"
            details += "\nRecommendations:\n"
            for rec in port.moxa_details['recommendations']:
                details += f"• {rec}\n"
        
        self.details_text.setPlainText(details)
    
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