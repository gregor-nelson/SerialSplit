#!/usr/bin/env python3
"""
Serial Port Manager Widget - Combines monitoring and testing functionality in tabs
Provides a clean interface for both monitoring and testing serial ports
"""

from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import pyqtSlot

from core.core import SerialPortInfo
from ui.widgets.port_monitor_widget import EnhancedPortInfoWidget
from ui.widgets.port_test_widget import SerialPortTestWidget
from ui.theme.theme import (
    ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts
)


class SerialPortManagerWidget(QWidget):
    """
    Tabbed widget that combines port monitoring and testing functionality.
    Provides a unified interface for comprehensive port management.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the tabbed user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create tab widget with theme-consistent styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {AppColors.BORDER_LIGHT};
                background-color: {AppColors.BACKGROUND_WHITE};
            }}
            QTabBar::tab {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                padding: {AppDimensions.PADDING_MEDIUM} {AppDimensions.PADDING_LARGE};
                margin-right: 2px;
                border: 1px solid {AppColors.BORDER_LIGHT};
                border-bottom: none;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background-color: {AppColors.BACKGROUND_WHITE};
                color: {AppColors.ACCENT_BLUE};
                font-weight: {AppFonts.BOLD_WEIGHT};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {AppColors.BUTTON_HOVER};
            }}
        """)
        
        # Monitor tab - existing functionality
        self.monitor_widget = EnhancedPortInfoWidget()
        self.tab_widget.addTab(self.monitor_widget, "Port Monitor")
        
        # Test tab - new functionality
        self.test_widget = SerialPortTestWidget()
        self.tab_widget.addTab(self.test_widget, "Port Test")
        
        main_layout.addWidget(self.tab_widget)
    
    def connect_signals(self):
        """Connect signals between widgets and forward to parent"""
        # Connect tab change events
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def set_current_port(self, port_name: str, port_info: Optional[SerialPortInfo] = None):
        """Set the current port in the test widget (called from main GUI)"""
        self.test_widget.set_current_port(port_name, port_info)
    
    def get_current_port(self) -> Optional[str]:
        """Get the currently set port from the test widget"""
        return self.test_widget.get_current_port()
    
    @pyqtSlot(int)
    def on_tab_changed(self, index: int):
        """Handle tab change events"""
        # Tab change handling - no sync needed since monitor widget doesn't handle selection
        pass
    
    # Forward monitor widget methods for compatibility
    def update_port_info(self, port_info: SerialPortInfo, enhanced_display: str):
        """Update port information display"""
        # Update monitor widget
        self.monitor_widget.update_port_info(port_info, enhanced_display)
        
        # Update test widget with current port
        self.test_widget.set_current_port(port_info.port_name, port_info)
    
    def set_port_type(self, port_type: str):
        """Set the port type display"""
        if hasattr(self.monitor_widget, 'set_port_type'):
            self.monitor_widget.set_port_type(port_type)
    
    def get_monitoring_controls(self):
        """Get monitoring controls for external access"""
        if hasattr(self.monitor_widget, 'get_monitoring_controls'):
            return self.monitor_widget.get_monitoring_controls()
        return None
    
    def hide_all(self):
        """Hide all port information"""
        self.monitor_widget.hide_all()
        self.test_widget.set_current_port("", None)
    
    def get_current_tab_name(self) -> str:
        """Get the name of the currently active tab"""
        current_index = self.tab_widget.currentIndex()
        return self.tab_widget.tabText(current_index)
    
    def switch_to_monitor_tab(self):
        """Switch to the monitor tab"""
        self.tab_widget.setCurrentIndex(0)
    
    def switch_to_test_tab(self):
        """Switch to the test tab"""
        self.tab_widget.setCurrentIndex(1)