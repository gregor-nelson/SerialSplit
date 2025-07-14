#!/usr/bin/env python3
"""
Output Port Widget for Hub4com GUI - Fully Refactored
All styles and dimensions extracted to global theme system
"""

from typing import List, Optional

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal

from core.core import PortConfig, SerialPortInfo
from ui.theme.theme import (
    ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts, 
    AppMessages, Config
)
from ui.theme.icons.icons import AppIcons
from ui.dialogs.help_dialog import HelpManager


class OutputPortWidget(QWidget):
    """Widget for a single output port configuration with full theme integration"""
    
    port_changed = pyqtSignal()
    
    def __init__(self, port_number: int, scanned_ports: List[SerialPortInfo], parent=None):
        super().__init__(parent)
        self.port_number = port_number
        self.scanned_ports: List[SerialPortInfo] = scanned_ports or []
        
        # Apply borderless styling for seamless integration
        self.setStyleSheet("QWidget { background-color: transparent; border: none; }")
        
        # Set consistent size policy without fixed height constraints
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.init_ui(scanned_ports)
    
    def init_ui(self, scanned_ports: List[SerialPortInfo]):
        """Initialize the user interface to match incoming port layout exactly"""
        main_layout = QVBoxLayout(self)
        ThemeManager.set_widget_margins(main_layout, "none")  # No extra margins like incoming port widgets
        main_layout.setSpacing(AppDimensions.SPACING_MEDIUM)  # Match incoming port spacing
        
        # Match incoming port design exactly - simple vertical layout
        layout = QVBoxLayout()
        ThemeManager.set_widget_margins(layout, "none")
        layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # Port label with remove button in far corner of same row
        label_layout = QHBoxLayout()
        self.label = ThemeManager.create_label(f"Port {self.port_number}:")
        label_layout.addWidget(self.label)
        label_layout.addStretch()  # Push button to far right
        
        # Remove button - match port test/monitor widget style exactly
        self.remove_btn = QPushButton()
        self.remove_btn.setFixedSize(24, 24)
        self.remove_btn.setToolTip(f"Remove port {self.port_number}")
        self.remove_btn.setStyleSheet(f"""
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
        self._update_delete_button_icon()
        label_layout.addWidget(self.remove_btn)
        
        layout.addLayout(label_layout)
        
        # Port selection combo (full width like incoming port)
        self.port_combo = ThemeManager.create_combobox(editable=True)
        self.populate_ports(scanned_ports)
        self.port_combo.currentTextChanged.connect(self.port_changed.emit)
        self.port_combo.setFixedHeight(AppDimensions.COMBOBOX_HEIGHT)
        layout.addWidget(self.port_combo)
        
        # Baud rate label on its own line (exactly like incoming port)
        layout.addWidget(ThemeManager.create_label("Baud Rate:"))
        
        # Baud rate selection (full width like incoming port)
        self.baud_combo = ThemeManager.create_combobox()
        self.populate_baud_rates(Config.DEFAULT_BAUD)
        self.baud_combo.currentTextChanged.connect(self.port_changed.emit)
        self.baud_combo.setFixedHeight(AppDimensions.COMBOBOX_HEIGHT)
        layout.addWidget(self.baud_combo)
        
        
        main_layout.addLayout(layout)
        
    
    def populate_ports(self, ports: List[SerialPortInfo]):
        """Populate port combo with enhanced port information using SerialPortInfo objects"""
        current_port = self.port_combo.currentData() or self.port_combo.currentText()
        
        self.port_combo.clear()
        self.port_combo.setEnabled(True)
        
        if not ports:
            self.port_combo.addItem(AppMessages.NO_DEVICES)
            self.port_combo.setEnabled(False)
            return
        
        # Add scanned ports using the same fast logic as incoming ports
        for port in ports:
            display_text = self._create_port_display_text(port)
            self.port_combo.addItem(display_text, port.port_name)
        
        # Restore previous selection if possible
        if current_port:
            index = self.port_combo.findData(current_port)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)
            elif self.port_combo.count() > 0:
                self.port_combo.setCurrentIndex(0)
        
    
    def _create_port_display_text(self, port):
        """Create enhanced display text for port - copied from incoming port logic"""
        display_text = port.port_name
        
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
        
        return display_text
    
    
    def populate_baud_rates(self, default=Config.DEFAULT_BAUD):
        """Populate combo box with common baud rate options"""
        self.baud_combo.clear()
        for rate in Config.BAUD_RATES:
            self.baud_combo.addItem(rate, rate)
        
        # Set default
        index = self.baud_combo.findData(default)
        if index >= 0:
            self.baud_combo.setCurrentIndex(index)
    
    
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
        self.label.setText(f"Port {new_number}:")
        self.remove_btn.setToolTip(f"Remove port {new_number}")
    
    def setEnabled(self, enabled: bool):
        """Override to handle enabling/disabling with proper visual feedback"""
        super().setEnabled(enabled)
        
        # Apply simple disabled styling for borderless design
        if not enabled:
            self.setStyleSheet("QWidget { background-color: transparent; border: none; }"
                             f"QWidget:disabled {{ color: {AppColors.TEXT_DISABLED}; }}")
        else:
            self.setStyleSheet("QWidget { background-color: transparent; border: none; }")
        
        # Enable/disable child widgets
        self.port_combo.setEnabled(enabled)
        self.baud_combo.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)
    
    def mousePressEvent(self, event):
        """Handle mouse press for visual feedback"""
        # No visual feedback needed for borderless design
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to restore normal state"""
        # No styling changes needed for borderless design
        super().mouseReleaseEvent(event)
    
    def _update_delete_button_icon(self):
        """Update delete button icon to match port test/monitor widget style"""
        from ui.theme.theme import IconManager
        
        icon = IconManager.create_svg_icon(
            AppIcons.DELETE,
            AppColors.TEXT_DEFAULT,
            IconManager.get_scaled_size(14)
        )
        self.remove_btn.setIcon(icon)
        self.remove_btn.setIconSize(IconManager.get_scaled_size(14))