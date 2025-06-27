#!/usr/bin/env python3
"""
Output Port Widget for Hub4com GUI
Handles individual port configuration with port selection and baud rate settings
Fully integrated with global theme system
"""

from typing import List, Optional

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

from core.components import PortConfig, SerialPortInfo
from ui.theme.theme import ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts


# Configuration constants
BAUD_RATES = ["1200", "2400", "4800", "9600", "14400", "19200", 
              "38400", "57600", "115200", "230400", "460800", "921600"]
DEFAULT_BAUD = "115200"


class OutputPortWidget(QWidget):
    """Widget for a single output port configuration with full theme integration"""
    
    port_changed = pyqtSignal()
    
    def __init__(self, port_number: int, available_ports: List[str], parent=None):
        super().__init__(parent)
        self.port_number = port_number
        self.scanned_ports: List[SerialPortInfo] = []
        
        # Apply widget styling
        self.setStyleSheet(f"""
            OutputPortWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
                padding: {AppDimensions.PADDING_MEDIUM};
                margin-bottom: {AppDimensions.SPACING_SMALL}px;
            }}
            OutputPortWidget:hover {{
                background-color: {AppColors.BUTTON_HOVER};
            }}
        """)
        
        self.init_ui(available_ports)
    
    def init_ui(self, available_ports: List[str]):
        """Initialize the user interface with full theme integration"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_MEDIUM
        )
        main_layout.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # Port label with fixed width
        self.label = ThemeManager.create_label(f"Port {self.port_number}:")
        self.label.setFixedWidth(55)  # Fixed width for alignment
        self.label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
            }}
        """)
        layout.addWidget(self.label)
        
        # Port selection combo
        self.port_combo = ThemeManager.create_combobox(editable=True)
        self.populate_ports(available_ports)
        self.port_combo.currentTextChanged.connect(self.port_changed.emit)
        self.port_combo.currentTextChanged.connect(self.update_port_type_indicator)
        self.port_combo.setMinimumWidth(120)
        layout.addWidget(self.port_combo, 2)  # Give it more stretch
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_LIGHT};
                margin: 0px {AppDimensions.SPACING_SMALL}px;
            }}
        """)
        layout.addWidget(separator)
        
        # Baud rate label
        baud_label = ThemeManager.create_label("Baud:")
        baud_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                margin-right: {AppDimensions.SPACING_SMALL}px;
            }}
        """)
        layout.addWidget(baud_label)
        
        # Baud rate selection
        self.baud_combo = ThemeManager.create_combobox()
        self.populate_baud_rates(DEFAULT_BAUD)
        self.baud_combo.currentTextChanged.connect(self.port_changed.emit)
        self.baud_combo.setFixedWidth(100)
        layout.addWidget(self.baud_combo)
        
        # Remove button with icon
        self.remove_btn = ThemeManager.create_icon_button(
            "REMOVE",  # Use REMOVE icon from AppIcons
            f"Remove port {self.port_number}",
            "small"
        )
        # Add hover effect
        self.remove_btn.setStyleSheet(self.remove_btn.styleSheet() + f"""
            QPushButton:hover {{
                background-color: {AppColors.ERROR_BACKGROUND};
                border: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {AppColors.ERROR_BORDER};
            }}
        """)
        layout.addWidget(self.remove_btn)
        
        main_layout.addLayout(layout)
        
        # Port type indicator with custom styling
        self.port_type_label = QLabel("")
        self.port_type_label.setWordWrap(True)
        self.port_type_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-style: italic;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.SMALL_SIZE};
                padding: {AppDimensions.PADDING_SMALL};
                background-color: {AppColors.INFO_BACKGROUND};
                border: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {AppColors.INFO_BACKGROUND};
                border-radius: {AppDimensions.BORDER_RADIUS_MODERN}px;
                margin-top: {AppDimensions.SPACING_SMALL}px;
            }}
        """)
        self.port_type_label.setVisible(False)  # Hidden by default
        
        # Create indented layout for the port type label
        indicator_layout = QHBoxLayout()
        indicator_layout.setContentsMargins(
            55 + AppDimensions.SPACING_MEDIUM,  # Align with port combo
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
            self.port_combo.addItem("No COM devices detected")
            self.port_combo.setEnabled(False)
    
    def populate_ports_enhanced(self, ports: List[SerialPortInfo]):
        """Populate port combo with enhanced port information"""
        self.scanned_ports = ports
        current_port = self.port_combo.currentData() or self.port_combo.currentText()
        
        self.port_combo.clear()
        self.port_combo.setEnabled(True)
        
        if not ports:
            self.port_combo.addItem("No COM devices detected")
            self.port_combo.setEnabled(False)
            self.port_type_label.setVisible(False)
            return
        
        # Add scanned ports with enhanced display formatting
        for port in ports:
            display_text = f"{port.port_name}"
            if port.is_moxa:
                display_text += " (Moxa)"
            elif port.port_type.startswith("Virtual"):
                display_text += f" ({port.port_type.split(' ')[1]})"
            
            # Add item with custom data
            self.port_combo.addItem(display_text, port.port_name)
            
            # Color code based on port type
            index = self.port_combo.count() - 1
            if port.is_moxa:
                self.port_combo.setItemData(index, ThemeManager.get_accent_color('orange'), Qt.ItemDataRole.ForegroundRole)
            elif port.port_type == "Physical":
                self.port_combo.setItemData(index, ThemeManager.get_accent_color('green'), Qt.ItemDataRole.ForegroundRole)
            else:  # Virtual
                self.port_combo.setItemData(index, ThemeManager.get_accent_color('blue'), Qt.ItemDataRole.ForegroundRole)
        
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
    
    def populate_baud_rates(self, default=DEFAULT_BAUD):
        """Populate combo box with common baud rate options"""
        self.baud_combo.clear()
        for rate in BAUD_RATES:
            self.baud_combo.addItem(rate, rate)
        
        # Set default
        index = self.baud_combo.findData(default)
        if index >= 0:
            self.baud_combo.setCurrentIndex(index)
    
    def update_port_type_indicator(self):
        """Update the port type indicator with theme-appropriate styling"""
        if not self.scanned_ports:
            self.port_type_label.setVisible(False)
            return
        
        current_port = self.port_combo.currentData() or self.port_combo.currentText().split(" ")[0]
        if not current_port or current_port == "No COM devices detected":
            self.port_type_label.setVisible(False)
            return
        
        # Find port info
        port_info = next((p for p in self.scanned_ports if p.port_name == current_port), None)
        if port_info:
            self.port_type_label.setVisible(True)
            
            if port_info.is_moxa:
                self.port_type_label.setText("🌐 MOXA Network Device - Make sure baud rate matches your source device")
                self._apply_indicator_style("warning")
            elif port_info.port_type == "Physical":
                self.port_type_label.setText("🔌 PHYSICAL PORT - Connected to real hardware, verify device baud rate")
                self._apply_indicator_style("success")
            else:
                self.port_type_label.setText("💻 VIRTUAL PORT - Software-created port for inter-application communication")
                self._apply_indicator_style("info")
        else:
            self.port_type_label.setVisible(False)
    
    def _apply_indicator_style(self, style_type: str):
        """Apply themed styling to the port type indicator"""
        bg_color = ThemeManager.get_semantic_color(style_type, "background")
        border_color = ThemeManager.get_semantic_color(style_type, "border")
        text_color = ThemeManager.get_semantic_color(style_type, "primary")
        
        self.port_type_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-style: italic;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.SMALL_SIZE};
                padding: {AppDimensions.PADDING_SMALL} {AppDimensions.PADDING_MEDIUM};
                background-color: {bg_color};
                border: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {border_color};
                border-radius: {AppDimensions.BORDER_RADIUS_MODERN}px;
                margin-top: {AppDimensions.SPACING_SMALL}px;
            }}
        """)
    
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
        
        # Apply disabled styling if needed
        if not enabled:
            self.setStyleSheet(self.styleSheet() + f"""
                OutputPortWidget:disabled {{
                    background-color: {AppColors.BACKGROUND_DISABLED};
                    border-color: {AppColors.BORDER_DISABLED};
                }}
            """)
        
        # Enable/disable child widgets
        self.port_combo.setEnabled(enabled)
        self.baud_combo.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)
    
    def mousePressEvent(self, event):
        """Handle mouse press for visual feedback"""
        self.setStyleSheet(self.styleSheet() + f"""
            OutputPortWidget {{
                background-color: {AppColors.BUTTON_PRESSED};
                border: {AppDimensions.BORDER_WIDTH_THICK}px solid {AppColors.BORDER_FOCUS};
            }}
        """)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to restore normal state"""
        # Restore normal styling
        self.setStyleSheet(f"""
            OutputPortWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
                padding: {AppDimensions.PADDING_MEDIUM};
                margin-bottom: {AppDimensions.SPACING_SMALL}px;
            }}
            OutputPortWidget:hover {{
                background-color: {AppColors.BUTTON_HOVER};
            }}
        """)
        super().mouseReleaseEvent(event)