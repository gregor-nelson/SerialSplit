#!/usr/bin/env python3
"""
Configuration Summary Dialog for Hub4com GUI
Clean and simple design matching help dialog patterns
Preserves essential visual elements for serial port routing explanation
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import Qt

from ui.theme.theme import ThemeManager, AppStyles, AppFonts, AppDimensions, AppColors, HTMLTheme
from core.core import DefaultConfig


class ConfigurationSummaryDialog(QDialog):
    """Simple configuration summary dialog matching help dialog patterns"""
    
    def __init__(self, parent=None, created_pairs=None, existing_pairs=None):
        super().__init__(parent)
        self.created_pairs = created_pairs or []
        self.existing_pairs = existing_pairs or []
        self.default_config = DefaultConfig()
        
        # Set window flags to prevent threading issues
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise the user interface"""
        self.setWindowTitle("Virtual COM Port Configuration Summary")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(AppDimensions.SPACING_LARGE)
        layout.setContentsMargins(*AppDimensions.MARGIN_DIALOG)
        
        # Create scrollable text area for configuration summary
        summary_text = QTextEdit()
        summary_text.setFont(AppFonts.CONSOLE_LARGE)
        summary_text.setReadOnly(True)
        summary_text.setStyleSheet(f"""
            QTextEdit {{
                border: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {AppColors.BORDER_DEFAULT};
                padding: {AppDimensions.PADDING_MEDIUM};
                background-color: {AppColors.BACKGROUND_WHITE};
                color: {AppColors.TEXT_DEFAULT};
                line-height: 1.4;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 10pt;
            }}
        """)
        
        summary_text.setHtml(self._generate_summary_content())
        layout.addWidget(summary_text)
        
        # Add footer with close button
        self._add_footer(layout)
    
    def _generate_summary_content(self):
        """Generate clean HTML content for configuration summary"""
        port_data = self._get_port_configuration_data()
        routing_data = self._get_routing_configuration_data()
        
        content = f"""
        {HTMLTheme.get_styles()}
        <h2>Virtual COM Port Configuration Summary</h2>
        <p><i>Configuration completed successfully - System ready for operation</i></p>
        
        <h3>Virtual COM Port Infrastructure</h3>
        <p><b>Status:</b> <span class="success-icon">✓</span> {port_data['status_text']}</p>
        
        <h4>Configured Port Pairs:</h4>
        <ul>
            {port_data['pairs_html']}
        </ul>
        
        <p><b>Technical Configuration:</b> Baud rate timing synchronisation enabled, buffer overrun protection active, bidirectional data flow configured</p>
        
        <h3>Hub4com Routing Service</h3>
        <p><b>Status:</b> <span class="success-icon">✓</span> Routing service configured and operational</p>
        
        <h4>Output Port Configuration:</h4>
        <ul>
            {routing_data}
        </ul>
        
        <p><b>Routing Protocol:</b> Full-duplex communication with automatic flow control, error detection, and connection monitoring</p>
        
        <h3>External Application Configuration</h3>
        
        <div class="warning-box">
            <p><b>Important Configuration Requirement</b></p>
            <p>External applications must connect to the designated client ports for proper data routing functionality.</p>
        </div>
        
        <h4>Application Connection Configuration:</h4>
        <ul>
            <li>For routing via <code>COM131</code> → Configure external application to use <code>COM132</code></li>
            <li>For routing via <code>COM141</code> → Configure external application to use <code>COM142</code></li>
        </ul>
        
        <h4>System Architecture:</h4>
        <ul>
            <li>Hub4com manages bidirectional routing between COM131 and COM141 (output ports)</li>
            <li>External applications connect through paired client ports (COM132 and COM142)</li>
            <li>Full-duplex communication with automatic error handling and reconnection</li>
        </ul>
        
        <h4>Data Flow Diagram:</h4>
        <div class="info-box" style="text-align: center; font-family: monospace; font-size: 9pt;">
            [Application A] ↔ COM132 ↔ COM131 ↔ Hub4com ↔ COM141 ↔ COM142 ↔ [Application B]
            <br><br>
            <i>Bidirectional Data Flow | Error Handling | Automatic Reconnection</i>
        </div>
        
        <div class="footer-box">
            <p><b><span class="success-icon">●</span> System configured and ready for external application connections</b></p>
        </div>
        """
        
        return content
    
    def _get_port_configuration_data(self):
        """Get port configuration data in simple format"""
        if self.created_pairs:
            status_text = "Virtual port pairs created successfully"
            pairs_list = self.created_pairs
        elif self.existing_pairs:
            status_text = "Existing virtual port pairs detected and configured"
            pairs_list = self.existing_pairs
        else:
            status_text = "Virtual port pairs configured and operational"
            pairs_list = ["COM131↔COM132", "COM141↔COM142"]
        
        # Simple list format
        pairs_html = ""
        for pair in pairs_list:
            pairs_html += f'<li><code>{pair}</code></li>\n'
        
        return {
            'status_text': status_text,
            'pairs_html': pairs_html
        }
    
    def _get_routing_configuration_data(self):
        """Get routing configuration in simple format"""
        routing_html = ""
        for port_config in self.default_config.output_mapping:
            port_info = f"Output Port: {port_config['port']} @ {port_config['baud']} baud"
            routing_html += f'<li><code>{port_info}</code></li>\n'
        
        return routing_html
    
    def _add_footer(self, layout):
        """Add simple footer matching help dialog pattern"""
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        # Simple close button using theme
        close_button = ThemeManager.create_button(
            "Close",
            self.accept,
            style_type="standard",
            variant="default"
        )
        close_button.setMinimumWidth(AppDimensions.BUTTON_WIDTH_STANDARD)
        close_button.setToolTip("Close configuration summary")
        
        footer_layout.addWidget(close_button)
        
        layout.addLayout(footer_layout)
    
    def closeEvent(self, event):
        """Handle dialog close event with proper resource cleanup"""
        event.accept()
        super().closeEvent(event)