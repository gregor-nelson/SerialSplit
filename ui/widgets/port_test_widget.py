#!/usr/bin/env python3
"""
Serial Port Test Widget - Provides comprehensive port testing functionality
Integrates with main GUI port selection (no internal dropdown)
"""

from typing import Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSlot, pyqtSignal

from core.core import SerialPortInfo, SerialPortTester
from ui.theme.theme import (
    ThemeManager, AppDimensions, AppColors, AppFonts
)


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
        
        # Current port display - matches help dialog text hierarchy
        self.port_label = QLabel("No port selected")
        self.port_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.INFO_PRIMARY};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.CAPTION_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                background: transparent;
            }}
        """)
        header_layout.addWidget(self.port_label)
        
        header_layout.addStretch()
        
        # Test button - styled to match help dialog buttons
        self.test_button = ThemeManager.create_button(
            "Test Port", 
            self.test_current_port,
            "primary"
        )
        
        self.test_button.setEnabled(False)
        header_layout.addWidget(self.test_button)
        
        main_layout.addLayout(header_layout)
        
        # Separator - matches help dialog separators
        separator = ThemeManager.create_separator("horizontal")
        main_layout.addWidget(separator)
        
        # Results text area - styled to match help dialog content display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
      
        main_layout.addWidget(self.results_text)
    
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
            else:
                display_text = f"{port_name}"
                
            self.port_label.setText(display_text)
            self.port_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.SUCCESS_PRIMARY};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                    font-size: {AppFonts.CAPTION_SIZE};
                    font-weight: {AppFonts.BOLD_WEIGHT};
                    background: transparent;
                }}
            """)
            
            # Enable test button if not currently testing
            self.test_button.setEnabled(not self._is_testing())
            
            # Clear previous results
            self.results_text.clear()
        else:
            self.test_button.setEnabled(False)
            self.results_text.clear()
    
    def test_current_port(self):
        """Test the currently set port (from main GUI selection)"""
        if self._is_testing():
            return
            
        if not self.current_port_name:
            return
        
        # Disable button and show testing state
        self.test_button.setEnabled(False)
        self.test_button.setText("Testing...")
        self.results_text.setPlainText(f"Testing port {self.current_port_name}...\nPlease wait...")
        
        # Start test in worker thread
        self.test_worker = PortTestWorker(self.current_port_name)
        self.test_worker.test_completed.connect(self.on_test_completed)
        self.test_worker.finished.connect(self.on_test_finished)
        self.test_worker.start()
    
    @pyqtSlot(dict)
    def on_test_completed(self, results: dict):
        """Handle completed port test"""
        # Format and display results
        formatted_results = self.tester.format_test_results(results)
        self.results_text.setPlainText(formatted_results)
    
    @pyqtSlot()
    def on_test_finished(self):
        """Handle test worker finishing (success or failure)"""
        # Reset UI state
        self.test_button.setEnabled(bool(self.current_port_name))
        self.test_button.setText("Test Port")
        
        # Clean up worker
        if self.test_worker:
            self.test_worker.deleteLater()
            self.test_worker = None
    
    def get_current_port(self) -> Optional[str]:
        """Get the currently set port name"""
        return self.current_port_name
    
    def _is_testing(self) -> bool:
        """Check if a test is currently running"""
        return self.test_worker is not None and self.test_worker.isRunning()