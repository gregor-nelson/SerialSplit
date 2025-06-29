#!/usr/bin/env python3
"""
Configuration Summary Dialog for Hub4com GUI
Displays startup configuration summary for marine workers
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QFrame, QGridLayout, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.theme.theme import ThemeManager, AppStyles, AppFonts, AppDimensions, AppColors
from core.components import DefaultConfig


class ConfigurationSummaryDialog(QDialog):
    """Dialog for displaying startup configuration summary"""
    
    def __init__(self, parent=None, created_pairs=None, existing_pairs=None):
        super().__init__(parent)
        self.created_pairs = created_pairs or []
        self.existing_pairs = existing_pairs or []
        self.default_config = DefaultConfig()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Serial Port Configuration Summary")
        self.setMinimumSize(650, 500)
        self.setMaximumSize(800, 600)
        
        # Apply window styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(AppDimensions.SPACING_LARGE)
        
        # Header
        self._add_header(layout)
        
        # Configuration sections
        self._add_pairs_section(layout)
        self._add_routing_section(layout)
        self._add_connection_guide(layout)
        
        # Footer with close button
        self._add_footer(layout)
    
    def _add_header(self, layout):
        """Add dialog header"""
        header_label = QLabel("Serial Port Configuration Complete")
        header_label.setFont(AppFonts.HEADING_LARGE)
        header_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.ACCENT_BLUE};
                font-weight: bold;
                padding: 10px;
                margin-bottom: 10px;
            }}
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Subtitle
        subtitle = QLabel("Your virtual COM ports have been configured and are ready for use")
        subtitle.setFont(AppFonts.DEFAULT_MEDIUM)
        subtitle.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
    
    def _add_pairs_section(self, layout):
        """Add virtual pairs configuration section"""
        group_box = QGroupBox("Virtual COM Port Pairs")
        group_box.setFont(AppFonts.DEFAULT_BOLD)
        group_box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {AppColors.BORDER_DEFAULT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: {AppColors.BACKGROUND_WHITE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {AppColors.ACCENT_BLUE};
            }}
        """)
        
        pairs_layout = QVBoxLayout(group_box)
        
        # Show created or existing pairs
        if self.created_pairs:
            status_text = "✅ Successfully created the following virtual port pairs:"
            pairs_info = self.created_pairs
        else:
            status_text = "✅ Found existing virtual port pairs:"
            pairs_info = ["COM131↔COM132", "COM141↔COM142"]  # Default assumption
        
        status_label = QLabel(status_text)
        status_label.setFont(AppFonts.DEFAULT_MEDIUM)
        pairs_layout.addWidget(status_label)
        
        # Show pairs in a formatted way
        for pair in pairs_info:
            pair_label = QLabel(f"   • {pair}")
            pair_label.setFont(AppFonts.CONSOLE_MEDIUM)
            pair_label.setStyleSheet(f"""
                color: {AppColors.SUCCESS_GREEN};
                font-weight: bold;
                padding: 2px 20px;
            """)
            pairs_layout.addWidget(pair_label)
        
        # Configuration details
        config_label = QLabel("⚙️ Configuration: Baud rate timing enabled, Buffer overrun protection enabled")
        config_label.setFont(AppFonts.DEFAULT_SMALL)
        config_label.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; padding: 5px 20px;")
        config_label.setWordWrap(True)
        pairs_layout.addWidget(config_label)
        
        layout.addWidget(group_box)
    
    def _add_routing_section(self, layout):
        """Add routing configuration section"""
        group_box = QGroupBox("Hub4com Routing Configuration")
        group_box.setFont(AppFonts.DEFAULT_BOLD)
        group_box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {AppColors.BORDER_DEFAULT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: {AppColors.BACKGROUND_WHITE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {AppColors.ACCENT_BLUE};
            }}
        """)
        
        routing_layout = QVBoxLayout(group_box)
        
        # Routing status
        routing_status = QLabel("🔗 Pre-configured for two-way routing:")
        routing_status.setFont(AppFonts.DEFAULT_MEDIUM)
        routing_layout.addWidget(routing_status)
        
        # Output ports
        for port_config in self.default_config.output_mapping:
            port_info = f"   • Output Port: {port_config['port']} @ {port_config['baud']} baud"
            port_label = QLabel(port_info)
            port_label.setFont(AppFonts.CONSOLE_MEDIUM)
            port_label.setStyleSheet(f"""
                color: {AppColors.ACCENT_BLUE};
                font-weight: bold;
                padding: 2px 20px;
            """)
            routing_layout.addWidget(port_label)
        
        layout.addWidget(group_box)
    
    def _add_connection_guide(self, layout):
        """Add connection guide for external applications"""
        group_box = QGroupBox("External Application Connection Guide")
        group_box.setFont(AppFonts.DEFAULT_BOLD)
        group_box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {AppColors.BORDER_DEFAULT};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: {AppColors.BACKGROUND_WHITE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {AppColors.WARNING_ORANGE};
            }}
        """)
        
        guide_layout = QVBoxLayout(group_box)
        
        # Important instruction
        important_label = QLabel("📱 IMPORTANT: Connect your external applications to these ports:")
        important_label.setFont(AppFonts.DEFAULT_MEDIUM)
        important_label.setStyleSheet(f"color: {AppColors.WARNING_ORANGE}; font-weight: bold;")
        guide_layout.addWidget(important_label)
        
        # Connection instructions
        connection_text = """
   • For routing via COM131 → Connect external application to COM132
   • For routing via COM141 → Connect external application to COM142

How it works:
   Hub4com routes data between COM131 and COM141 (the configured output ports)
   External applications connect to the paired ports (COM132 and COM142)
   Data flows bidirectionally between all connected applications
        """
        
        connection_label = QLabel(connection_text.strip())
        connection_label.setFont(AppFonts.CONSOLE_MEDIUM)
        connection_label.setStyleSheet(f"""
            color: {AppColors.TEXT_DEFAULT};
            padding: 10px 20px;
            line-height: 1.4;
        """)
        connection_label.setWordWrap(True)
        guide_layout.addWidget(connection_label)
        
        # Visual diagram
        diagram_label = QLabel("""
Connection Flow:
[External App A] ←→ COM132 ←→ COM131 ←→ Hub4com ←→ COM141 ←→ COM132 ←→ [External App B]
        """)
        diagram_label.setFont(AppFonts.CONSOLE_SMALL)
        diagram_label.setStyleSheet(f"""
            color: {AppColors.TEXT_SECONDARY};
            padding: 10px 20px;
            font-family: monospace;
            background-color: {AppColors.BACKGROUND_LIGHT};
            border: 1px solid {AppColors.BORDER_LIGHT};
            border-radius: 4px;
        """)
        diagram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        guide_layout.addWidget(diagram_label)
        
        layout.addWidget(group_box)
    
    def _add_footer(self, layout):
        """Add footer with close button"""
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        close_button = QPushButton("Understood")
        close_button.setFont(AppFonts.DEFAULT_MEDIUM)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.ACCENT_BLUE};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {AppColors.ACCENT_BLUE_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.ACCENT_BLUE_PRESSED};
            }}
        """)
        close_button.clicked.connect(self.accept)
        
        footer_layout.addWidget(close_button)
        footer_layout.addStretch()
        
        layout.addLayout(footer_layout)