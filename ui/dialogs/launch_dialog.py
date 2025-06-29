#!/usr/bin/env python3
"""
Launch Dialog for Hub4com GUI
Displays system initialisation summary with HTML styling
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QFrame, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.theme.theme import ThemeManager, AppStyles, AppFonts, AppDimensions, AppColors
from core.components import DefaultConfig


class LaunchDialog(QDialog):
    """Dialog for displaying system initialisation summary"""
    
    def __init__(self, parent=None, created_pairs=None, existing_pairs=None):
        super().__init__(parent)
        self.created_pairs = created_pairs or []
        self.existing_pairs = existing_pairs or []
        self.default_config = DefaultConfig()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("System Initialisation")
        self.setMinimumSize(600, 450)
        self.setMaximumSize(700, 550)
        
        # Apply window styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(AppDimensions.SPACING_LARGE)
        
        # Main content with HTML styling
        self._add_content(layout)
        
        # Footer with options
        self._add_footer(layout)
    
    def _add_content(self, layout):
        """Add main dialog content with HTML formatting"""
        content_text = self._generate_html_content()
        
        content_widget = QTextEdit()
        content_widget.setHtml(content_text)
        content_widget.setReadOnly(True)
        content_widget.setMaximumHeight(350)
        content_widget.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppColors.BACKGROUND_WHITE};
                border: 1px solid {AppColors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        layout.addWidget(content_widget)
    
    def _generate_html_content(self):
        """Generate HTML-styled content for the dialog"""
        
        # Determine port status
        if self.created_pairs:
            port_status = "<span style='color: #28a745; font-weight: bold;'>✅ Created virtual port pairs</span>"
            pairs_list = self.created_pairs
        elif self.existing_pairs:
            port_status = "<span style='color: #28a745; font-weight: bold;'>✅ Virtual port pairs active</span>"
            pairs_list = self.existing_pairs
        else:
            port_status = "<span style='color: #28a745; font-weight: bold;'>✅ Virtual port pairs active</span>"
            pairs_list = ["COM131↔COM132", "COM141↔COM142"]
        
        html_content = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: {AppColors.ACCENT_BLUE}; text-align: center; margin-bottom: 20px; font-size: 18px;">
                ✅ Serial Port Configuration Complete
            </h2>
            
            <p style="text-align: center; color: {AppColors.TEXT_WHITE}; margin-bottom: 25px; font-size: 14px;">
                The system has been initialised with default routing parameters.
            </p>
            
            <div style="background-color: #f8f9fa; border-left: 4px solid {AppColors.ACCENT_BLUE}; padding: 15px; margin: 15px 0; border-radius: 4px;">
                <h3 style="color: {AppColors.ACCENT_BLUE}; margin-top: 0; font-size: 14px; font-weight: bold;">
                    CONFIGURED COMPONENTS:
                </h3>
                <ul style="margin: 10px 0; padding-left: 20px; color: {AppColors.TEXT_DEFAULT};">
                    <li style="margin: 5px 0;">{port_status}: <code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: monospace;">{', '.join(pairs_list)}</code></li>
                    <li style="margin: 5px 0;"><strong>Baud rate:</strong> <code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: monospace;">115,200</code></li>
                    <li style="margin: 5px 0;"><strong>Buffer management:</strong> <span style="color: #28a745;">Enabled</span></li>
                    <li style="margin: 5px 0;"><strong>Timing control:</strong> <span style="color: #28a745;">Enabled</span></li>
                </ul>
            </div>
            
            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; border-radius: 4px;">
                <h3 style="color: #856404; margin-top: 0; font-size: 14px; font-weight: bold;">
                    APPLICATION CONNECTION:
                </h3>
                <p style="margin: 8px 0; color: {AppColors.TEXT_DEFAULT}; font-size: 13px;">
                    Applications should connect to <code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: monospace;">COM132</code> and <code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: monospace;">COM142</code> respectively.<br>
                    Data routing begins when the service is started.<br>
                    Bidirectional communication is supported between connected applications.
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 20px; padding: 10px; background-color: #e7f3ff; border-radius: 4px;">
                <p style="margin: 0; color: {AppColors.TEXT_DEFAULT}; font-size: 12px; font-style: italic;">
                    System parameters are optimised for standard serial communication protocols.
                </p>
            </div>
        </div>
        """
        
        return html_content
    
    def _add_footer(self, layout):
        """Add footer with options"""
        footer_layout = QVBoxLayout()
        
        # Don't show again checkbox
        self.dont_show_checkbox = QCheckBox("Don't show this dialog on startup")
        self.dont_show_checkbox.setStyleSheet(f"color: {AppColors.TEXT_DEFAULT};")
        footer_layout.addWidget(self.dont_show_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        details_button = QPushButton("View Technical Details")
        details_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.BACKGROUND_WHITE};
                color: {AppColors.ACCENT_BLUE};
                border: 1px solid {AppColors.ACCENT_BLUE};
                padding: 8px 16px;
                border-radius: 4px;
                margin-right: 10px;
            }}
            QPushButton:hover {{
                background-color: {AppColors.ACCENT_BLUE};
                color: white;
            }}
        """)
        details_button.clicked.connect(self._show_technical_details)
        
        continue_button = QPushButton("Continue")
        continue_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.ACCENT_BLUE};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {AppColors.ACCENT_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.ACCENT_BLUE};
            }}
        """)
        continue_button.clicked.connect(self.accept)
        continue_button.setDefault(True)
        
        button_layout.addWidget(details_button)
        button_layout.addWidget(continue_button)
        button_layout.addStretch()
        
        footer_layout.addLayout(button_layout)
        layout.addLayout(footer_layout)
    
    def _show_technical_details(self):
        """Show technical details dialog"""
        # Import at module level to avoid circular imports
        from ui.dialogs.configuration_summary_dialog import ConfigurationSummaryDialog
        
        details_dialog = ConfigurationSummaryDialog(
            parent=self,
            created_pairs=self.created_pairs,
            existing_pairs=self.existing_pairs
        )
        details_dialog.exec()
    
    def should_show_again(self):
        """Return whether this dialog should be shown again"""
        return not self.dont_show_checkbox.isChecked()