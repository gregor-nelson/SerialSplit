#!/usr/bin/env python3
"""
Launch Dialog for Hub4com GUI
Clean and simple design matching help dialog patterns
Displays system initialisation summary
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QFrame, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.theme.theme import (ThemeManager, AppStyles, AppFonts, AppDimensions, 
                           AppColors, HTMLTheme)
from core.core import DefaultConfig, SettingsManager


class LaunchDialog(QDialog):
    """Simple launch dialog for displaying system initialisation summary"""
    
    def __init__(self, parent=None, created_pairs=None, existing_pairs=None):
        super().__init__(parent)
        self.created_pairs = created_pairs or []
        self.existing_pairs = existing_pairs or []
        self.default_config = DefaultConfig()
        self.settings_manager = SettingsManager()
        
        # Set window flags to prevent threading issues
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise the user interface"""
        self.setWindowTitle("System Initialisation")
        self.setMinimumSize(600, 450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(AppDimensions.SPACING_LARGE)
        layout.setContentsMargins(*AppDimensions.MARGIN_DIALOG)
        
        # Apply dark mode dialog styling
        ThemeManager.style_dialog(self)
        
        # Create scrollable text area for initialisation summary (matching help dialog)
        summary_text = QTextEdit()
        summary_text.setFont(AppFonts.CONSOLE_LARGE)
        summary_text.setReadOnly(True)
        # Apply dark mode styling using theme system
        summary_text.setStyleSheet(AppStyles.textedit_html())
        
        summary_text.setHtml(self._generate_summary_content())
        layout.addWidget(summary_text)
        
        # Add footer with options
        self._add_footer(layout)
    
    def _generate_summary_content(self):
        """Generate clean HTML content for initialisation summary"""
        port_status_data = self._get_port_status_data()
        connection_ports = self._get_connection_ports()
        
        content = f"""
        <h2>Serial Port Configuration Complete</h2>
        <p><i>The system has been initialised with default routing parameters.</i></p>
        
        <h3>Configured Components</h3>
        <ul>
            <li><b>Virtual Port Pairs:</b> <span style="color: {AppColors.SUCCESS_PRIMARY};">✓</span> {port_status_data['pairs_html']}</li>
            <li><b>Baud Rate:</b> <code style="background: {AppColors.GRAY_100}; padding: 2px 4px; color: {AppColors.TEXT_DEFAULT};">{self.default_config.default_baud}</code></li>
            <li><b>Buffer Management:</b> <span style="color: {AppColors.SUCCESS_PRIMARY};">Enabled</span></li>
            <li><b>Timing Control:</b> <span style="color: {AppColors.SUCCESS_PRIMARY};">Enabled</span></li>
        </ul>
        
        <div style="background-color: {AppColors.GRAY_100}; border-left: 3px solid {AppColors.ACCENT_BLUE}; padding: 10px; margin: 15px 0; color: {AppColors.TEXT_DEFAULT};">
            <h4>Application Connection</h4>
            <p>Applications should connect to {connection_ports} respectively.</p>
            <p>Data routing begins when the service is started.</p>
            <p>Bidirectional communication is supported between connected applications.</p>
        </div>
        
        <h3>System Status</h3>
        <p><b><span style="color: {AppColors.SUCCESS_PRIMARY};">●</span> System parameters are optimised for standard serial communication protocols.</b></p>
        
        <p><i>Click "View Technical Details" for comprehensive configuration information.</i></p>
        """
        
        return content
    
    def _get_port_status_data(self):
        """Get port status information in simple format"""
        if self.created_pairs:
            pairs_list = self.created_pairs
        elif self.existing_pairs:
            pairs_list = self.existing_pairs
        else:
            pairs_list = ["COM131↔COM132", "COM141↔COM142"]
        
        # Format pairs list simply
        formatted_pairs = []
        for pair in pairs_list:
            formatted_pairs.append(f'<code style="background: {AppColors.GRAY_50}; padding: 2px 4px; color: {AppColors.TEXT_DEFAULT};">{pair}</code>')
        
        pairs_html = ", ".join(formatted_pairs)
        
        return {
            'pairs_html': pairs_html,
            'pairs_list': pairs_list
        }
    
    def _get_connection_ports(self):
        """Get formatted connection ports"""
        ports = ["COM132", "COM142"]
        formatted_ports = []
        for port in ports:
            formatted_ports.append(f'<code style="background: {AppColors.GRAY_100}; padding: 2px 4px; color: {AppColors.TEXT_DEFAULT};">{port}</code>')
        
        return " and ".join(formatted_ports)
    
    def _add_footer(self, layout):
        """Add footer with options matching help dialog simplicity"""
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # Don't show again checkbox using theme
        self.dont_show_checkbox = ThemeManager.create_checkbox(
            "Don't show this dialog on startup"
        )
        footer_layout.addWidget(self.dont_show_checkbox)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Details button
        self.details_button = ThemeManager.create_button(
            "View Technical Details",
            self._show_technical_details,
            style_type="standard",
            variant="default"
        )
        
        button_layout.addWidget(self.details_button)
        button_layout.addStretch()
        
        # Continue button
        self.continue_button = ThemeManager.create_button(
            "Continue",
            self.accept,
            style_type="standard",
            variant="primary"
        )
        self.continue_button.setDefault(True)
        self.continue_button.setMinimumWidth(AppDimensions.BUTTON_WIDTH_STANDARD)
        
        button_layout.addWidget(self.continue_button)
        
        footer_layout.addLayout(button_layout)
        layout.addLayout(footer_layout)
    
    def _show_technical_details(self):
        """Show technical details dialog"""
        try:
            # Import here to avoid circular imports
            from ui.dialogs.configuration_summary_dialog import ConfigurationSummaryDialog
            
            # Create dialog with proper parent
            details_dialog = ConfigurationSummaryDialog(
                parent=self,
                created_pairs=self.created_pairs,
                existing_pairs=self.existing_pairs
            )
            
            # Show as modal dialog
            details_dialog.exec()
            
        except ImportError as e:
            # Handle import error gracefully
            print(f"Error importing ConfigurationSummaryDialog: {e}")
    
    def should_show_again(self):
        """Return whether this dialog should be shown again"""
        return not self.dont_show_checkbox.isChecked()
    
    def accept(self):
        """Override accept to save checkbox state before closing"""
        # Save the checkbox state to settings
        show_dialog = self.should_show_again()
        self.settings_manager.set_show_launch_dialog(show_dialog)
        
        # Call parent accept
        super().accept()
    
    def closeEvent(self, event):
        """Handle dialog close event with proper resource cleanup"""
        event.accept()
        super().closeEvent(event)