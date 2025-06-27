#!/usr/bin/env python3
"""
Pair Creation Dialog for Hub4com GUI
Handles creation of new COM0COM virtual port pairs
"""

from typing import Tuple, Optional

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

from ui.theme.theme import ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts


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
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Create a new pair of connected virtual serial ports.\n\n" +
            "💡 TIP: Leave the names empty to let COM0COM automatically assign port names like COM3, COM4, etc.\n" +
            "Or enter specific names like COM10, COM11 if you need particular port numbers."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(f"""
            padding: 10px; 
            background-color: {AppColors.BACKGROUND_LIGHT}; 
            border: 1px solid {AppColors.BORDER_DEFAULT}; 
            color: {AppColors.TEXT_DEFAULT};
            font-family: {AppFonts.DEFAULT_FAMILY};
            font-size: {AppFonts.DEFAULT_SIZE};
        """)
        layout.addWidget(instructions)
        
        # Port A input
        port_a_layout = QHBoxLayout()
        port_a_label = QLabel("Port A Name:")
        port_a_label.setStyleSheet(AppStyles.label())
        port_a_layout.addWidget(port_a_label)
        
        self.port_a_input = QLineEdit()
        self.port_a_input.setPlaceholderText("e.g., COM5 or leave empty")
        self.port_a_input.setStyleSheet(AppStyles.lineedit())
        port_a_layout.addWidget(self.port_a_input)
        
        layout.addLayout(port_a_layout)
        
        # Port B input
        port_b_layout = QHBoxLayout()
        port_b_label = QLabel("Port B Name:")
        port_b_label.setStyleSheet(AppStyles.label())
        port_b_layout.addWidget(port_b_label)
        
        self.port_b_input = QLineEdit()
        self.port_b_input.setPlaceholderText("e.g., COM6 or leave empty")
        self.port_b_input.setStyleSheet(AppStyles.lineedit())
        port_b_layout.addWidget(self.port_b_input)
        
        layout.addLayout(port_b_layout)
        
        # Buttons
        buttons = QHBoxLayout()
        
        self.create_btn = QPushButton("Create")
        self.create_btn.setStyleSheet(AppStyles.button("primary"))
        self.create_btn.clicked.connect(self.accept)
        buttons.addWidget(self.create_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(AppStyles.button())
        self.cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons)
    
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