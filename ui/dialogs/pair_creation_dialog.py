#!/usr/bin/env python3
"""
Pair Creation Dialog for Hub4com GUI
Handles creation of new COM0COM virtual port pairs
"""

from typing import Tuple, Optional

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtCore import Qt

from ui.theme.theme import ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts, HTMLTheme


class PairCreationDialog(QDialog):
    """Dialog for creating new COM0COM virtual port pairs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.port_a_input = None
        self.port_b_input = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Create Virtual Port Pair")
        self.setMinimumSize(400, 300)
        
        ThemeManager.style_dialog(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*AppDimensions.MARGIN_DIALOG)
        layout.setSpacing(AppDimensions.SPACING_LARGE)
        
        # Instructions using QTextEdit for rich text
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setStyleSheet(AppStyles.textedit_html() + AppStyles.scrollbar())
        instructions.setHtml(self._get_instructions_html())
        layout.addWidget(instructions)
        
        # Port A input
        port_a_layout = QHBoxLayout()
        port_a_label = ThemeManager.create_label("Port A Name:")
        port_a_layout.addWidget(port_a_label)
        
        self.port_a_input = ThemeManager.create_lineedit()
        self.port_a_input.setPlaceholderText("e.g., COM5 or leave empty")
        port_a_layout.addWidget(self.port_a_input)
        
        layout.addLayout(port_a_layout)
        
        # Port B input
        port_b_layout = QHBoxLayout()
        port_b_label = ThemeManager.create_label("Port B Name:")
        port_b_layout.addWidget(port_b_label)
        
        self.port_b_input = ThemeManager.create_lineedit()
        self.port_b_input.setPlaceholderText("e.g., COM6 or leave empty")
        port_b_layout.addWidget(self.port_b_input)
        
        layout.addLayout(port_b_layout)
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        self.create_btn = ThemeManager.create_button("Create", self.accept, "primary")
        buttons.addWidget(self.create_btn)
        
        self.cancel_btn = ThemeManager.create_button("Cancel", self.reject)
        buttons.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons)
    
    def _get_instructions_html(self) -> str:
        """Get instructions in HTML format using the theme"""
        return f"""
        {HTMLTheme.get_styles()}
        <h3>Create Virtual Port Pair</h3>
        <p>Create a new pair of connected virtual serial ports.</p>
        <div class="info-box">
            <p><b>TIP:</b> Leave the names empty to let COM0COM automatically assign port names like <code>COM3</code>, <code>COM4</code>, etc.</p>
            <p>Or enter specific names like <code>COM10</code>, <code>COM11</code> if you need particular port numbers.</p>
        </div>
        """

    def get_port_names(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the entered port names, or None if empty"""
        port_a = self.port_a_input.text().strip() or None
        port_b = self.port_b_input.text().strip() or None
        return port_a, port_b
    
    def build_command_args(self) -> list:
        """Build command arguments for COM0COM"""
        port_a, port_b = self.get_port_names()
        
        cmd_args = ["install"]
        
        if port_a:
            cmd_args.append(f"PortName={port_a}")
        else:
            cmd_args.append("-")
            
        if port_b:
            cmd_args.append(f"PortName={port_b}")
        else:
            cmd_args.append("-")
        
        return cmd_args
    
    @staticmethod
    def create_port_pair(parent=None) -> Tuple[bool, Optional[list]]:
        """
        Static method to create a port pair with dialog
        Returns (user_accepted, command_args)
        """
        dialog = PairCreationDialog(parent)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, dialog.build_command_args()
        else:
            return False, None