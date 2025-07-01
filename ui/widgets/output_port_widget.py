#!/usr/bin/env python3
"""
Output Port Widget for Hub4com GUI - Fully Refactored
All styles and dimensions extracted to global theme system
"""

from typing import List, Optional

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

from core.components import PortConfig, SerialPortInfo
from ui.theme.theme import (
    ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts, 
    AppMessages, Config
)
from ui.dialogs.help_dialog import HelpManager


class OutputPortWidget(QWidget):
    """Widget for a single output port configuration with full theme integration"""
    
    port_changed = pyqtSignal()
    
    def __init__(self, port_number: int, available_ports: List[str], parent=None):
        super().__init__(parent)
        self.port_number = port_number
        self.scanned_ports: List[SerialPortInfo] = []
        
        # Apply widget styling from theme
        self.setStyleSheet(AppStyles.output_port_widget())
        
        self.init_ui(available_ports)
    
    def init_ui(self, available_ports: List[str]):
        """Initialize the user interface with full theme integration"""
        main_layout = QVBoxLayout(self)
        ThemeManager.set_widget_margins(main_layout, "control")
        main_layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Main horizontal layout
        layout = QHBoxLayout()
        ThemeManager.set_widget_margins(layout, "none")
        layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # Port label using theme manager
        self.label = ThemeManager.create_port_label(self.port_number)
        layout.addWidget(self.label)
        
        # Port selection combo
        self.port_combo = ThemeManager.create_combobox(editable=True)
        self.populate_ports(available_ports)
        self.port_combo.currentTextChanged.connect(self.port_changed.emit)
        self.port_combo.currentTextChanged.connect(self.update_port_type_indicator)
        self.port_combo.setMinimumWidth(AppDimensions.COMBOBOX_MIN_WIDTH)
        layout.addWidget(self.port_combo, 2)  # Give it more stretch
        
        # Separator using theme
        layout.addWidget(ThemeManager.create_separator("vertical"))
        
        # Baud rate label using theme
        layout.addWidget(ThemeManager.create_baud_label())
        
        # Baud rate selection
        self.baud_combo = ThemeManager.create_combobox()
        self.populate_baud_rates(Config.DEFAULT_BAUD)
        self.baud_combo.currentTextChanged.connect(self.port_changed.emit)
        self.baud_combo.setFixedWidth(AppDimensions.WIDTH_BAUD_COMBO)
        layout.addWidget(self.baud_combo)
        
        # Remove button with theme-based styling
        self.remove_btn = ThemeManager.create_icon_button(
            "REMOVE",
            f"Remove port {self.port_number}",
            "small"
        )
        # Apply danger hover style
        current_style = self.remove_btn.styleSheet()
        self.remove_btn.setStyleSheet(AppStyles.icon_button_hover_danger())
        layout.addWidget(self.remove_btn)
        
        main_layout.addLayout(layout)
        
        # Port type indicator using theme
        self.port_type_label = ThemeManager.create_port_type_indicator()
        
        # Create indented layout for the port type label
        indicator_layout = QHBoxLayout()
        indicator_layout.setContentsMargins(
            AppDimensions.WIDTH_LABEL_PORT + AppDimensions.SPACING_MEDIUM,
            0, 0, 0
        )
        indicator_layout.addWidget(self.port_type_label)
        main_layout.addLayout(indicator_layout)
    
    def populate_ports(self, available_ports: List[str]):
        """Populate port combo with available ports (simple version)"""
        self.port_combo.clear()
        if available_ports:
            self.port_combo.addItems(available_ports)
        else:
            self.port_combo.addItem(AppMessages.NO_DEVICES)
            self.port_combo.setEnabled(False)
    
    def populate_ports_enhanced(self, ports: List[SerialPortInfo]):
        """Populate port combo with enhanced port information"""
        self.scanned_ports = ports
        current_port = self.port_combo.currentData() or self.port_combo.currentText()
        
        self.port_combo.clear()
        self.port_combo.setEnabled(True)
        
        if not ports:
            self.port_combo.addItem(AppMessages.NO_DEVICES)
            self.port_combo.setEnabled(False)
            self.port_type_label.setVisible(False)
            return
        
        # Add scanned ports with enhanced display formatting
        for port in ports:
            # Create enhanced display text with status indicator
            display_text = port.port_name
            
            # Add device type and status information
            if port.is_moxa:
                display_text += "  •  Moxa Device"
                if port.device_name and port.device_name != "Unknown":
                    display_text += f"  •  {port.device_name}"
            elif port.port_type.startswith("Virtual"):
                virtual_type = port.port_type.split(' ')[1] if ' ' in port.port_type else "Virtual"
                display_text += f"  •  {virtual_type} Port"
            else:
                display_text += "  •  Hardware Port"
                if port.device_name and port.device_name != "Unknown":
                    display_text += f"  •  {port.device_name}"
            
            # Add item with custom data
            self.port_combo.addItem(display_text, port.port_name)
            
            # Color code based on port type using enhanced theme colors
            index = self.port_combo.count() - 1
            if port.is_moxa:
                self.port_combo.setItemData(
                    index, 
                    ThemeManager.get_accent_color('purple'), 
                    Qt.ItemDataRole.ForegroundRole
                )
            elif port.port_type == "Physical":
                self.port_combo.setItemData(
                    index, 
                    ThemeManager.get_accent_color('green'), 
                    Qt.ItemDataRole.ForegroundRole
                )
            else:  # Virtual
                self.port_combo.setItemData(
                    index, 
                    ThemeManager.get_accent_color('blue'), 
                    Qt.ItemDataRole.ForegroundRole
                )
        
        # Restore previous selection if possible
        if current_port:
            index = self.port_combo.findData(current_port)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)
            else:
                # Try to find by text if data lookup failed
                index = self.port_combo.findText(current_port, Qt.MatchFlag.MatchStartsWith)
                if index >= 0:
                    self.port_combo.setCurrentIndex(index)
        
        self.update_port_type_indicator()
    
    def populate_baud_rates(self, default=Config.DEFAULT_BAUD):
        """Populate combo box with common baud rate options"""
        self.baud_combo.clear()
        for rate in Config.BAUD_RATES:
            self.baud_combo.addItem(rate, rate)
        
        # Set default
        index = self.baud_combo.findData(default)
        if index >= 0:
            self.baud_combo.setCurrentIndex(index)
    
    def update_port_type_indicator(self):
        """Update the port type indicator with theme messages and styling"""
        if not self.scanned_ports:
            self.port_type_label.setVisible(False)
            return
        
        current_port = self.port_combo.currentData() or self.port_combo.currentText().split(" ")[0]
        if not current_port or current_port == AppMessages.NO_DEVICES:
            self.port_type_label.setVisible(False)
            return
        
        # Find port info
        port_info = next((p for p in self.scanned_ports if p.port_name == current_port), None)
        if port_info:
            self.port_type_label.setVisible(True)
            
            # Use centralized tooltip system with enhanced status indicators
            if port_info.is_moxa:
                self.port_type_label.setText(HelpManager.get_tooltip("port_type_moxa"))
                self.port_type_label.setStyleSheet(AppStyles.port_type_indicator("moxa"))
            elif port_info.port_type == "Physical":
                self.port_type_label.setText(HelpManager.get_tooltip("port_type_physical"))
                self.port_type_label.setStyleSheet(AppStyles.port_type_indicator("available"))
            else:
                self.port_type_label.setText(HelpManager.get_tooltip("port_type_virtual"))
                self.port_type_label.setStyleSheet(AppStyles.port_type_indicator("virtual"))
        else:
            self.port_type_label.setVisible(False)
    
    def get_current_port_info(self) -> Optional[SerialPortInfo]:
        """Get the SerialPortInfo for the currently selected port"""
        current_port = self.port_combo.currentData() or self.port_combo.currentText().split(" ")[0]
        if current_port and self.scanned_ports:
            return next((p for p in self.scanned_ports if p.port_name == current_port), None)
        return None
    
    def get_config(self) -> PortConfig:
        """Get the port configuration"""
        port_text = self.port_combo.currentData() or self.port_combo.currentText()
        # Extract just the port name if it has additional formatting
        if port_text and " (" in port_text:
            port_text = port_text.split(" (")[0]
        
        return PortConfig(
            port_text,
            self.baud_combo.currentText()
        )
    
    def renumber(self, new_number: int):
        """Update the port number after reordering"""
        self.port_number = new_number
        self.label.setText(AppMessages.BUTTON_PORT_LABEL.format(number=new_number))
        self.remove_btn.setToolTip(f"Remove port {new_number}")
    
    def setEnabled(self, enabled: bool):
        """Override to handle enabling/disabling with proper visual feedback"""
        super().setEnabled(enabled)
        
        # Apply disabled styling from theme
        if not enabled:
            current_style = self.styleSheet()
            self.setStyleSheet(current_style + AppStyles.output_port_widget_disabled())
        else:
            self.setStyleSheet(AppStyles.output_port_widget())
        
        # Enable/disable child widgets
        self.port_combo.setEnabled(enabled)
        self.baud_combo.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)
    
    def mousePressEvent(self, event):
        """Handle mouse press for visual feedback"""
        self.setStyleSheet(AppStyles.output_port_widget_pressed())
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to restore normal state"""
        # Restore normal styling from theme
        self.setStyleSheet(AppStyles.output_port_widget())
        super().mouseReleaseEvent(event)