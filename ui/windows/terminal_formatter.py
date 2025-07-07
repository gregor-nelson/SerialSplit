#!/usr/bin/env python3
"""
Terminal Stream Formatter Module

This module provides formatting capabilities for terminal stream data,
applying consistent styling and color-coding for serial port communication.
Follows the same professional styling as CommandFormatter and OutputLogFormatter.
"""

from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from PyQt6.QtWidgets import QTextEdit
from datetime import datetime
from ui.theme.theme import AppColors, AppFonts


class TerminalStreamFormatter:
    """
    Formats terminal stream data with color-coded data flow and consistent styling.
    
    Follows the same professional color scheme as CommandFormatter for UI consistency.
    """
    
    def __init__(self):
        """Initialize the formatter with color definitions for different data types."""
        # Professional muted color scheme matching CommandFormatter style
        self.colors = {
            'incoming': AppColors.ACCENT_GREEN,      # Green for received data
            'outgoing': AppColors.ACCENT_BLUE,       # Blue for sent data
            'timestamp': AppColors.TEXT_DISABLED,    # Gray for timestamps
            'separator': AppColors.CMD_MUTED,        # Light gray for separators
            'error': AppColors.ERROR_PRIMARY,        # Red for connection errors
            'status': AppColors.CMD_HIGHLIGHT,       # Blue for status messages
            'default': AppColors.CMD_DEFAULT,        # Default text color
        }
        
        # Create format cache for performance
        self._format_cache = {}
        
    def _get_format(self, color: str, bold: bool = False) -> QTextCharFormat:
        """
        Get or create a text format with the specified color and style.
        
        Args:
            color: Hex color string
            bold: Whether to apply bold formatting
            
        Returns:
            QTextCharFormat with the specified styling
        """
        cache_key = f"{color}_{bold}"
        
        if cache_key not in self._format_cache:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            # Use the same font family as CommandFormatter for consistency
            fmt.setFontFamily(AppFonts.CONSOLE_FAMILY)
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            self._format_cache[cache_key] = fmt
            
        return self._format_cache[cache_key]
    
    def _ensure_monospace_font(self, text_edit: QTextEdit):
        """Ensure the text edit uses consistent monospace font."""
        font = QFont(AppFonts.CONSOLE.family(), AppFonts.FONT_SIZE_LARGE)
        font.setStyleHint(QFont.StyleHint.Monospace)
        text_edit.setFont(font)
    
    def append_data(self, text_edit: QTextEdit, data: str, data_type: str = "incoming", 
                   show_timestamp: bool = True):
        """
        Format and append serial data to the text edit widget.
        
        Args:
            text_edit: The QTextEdit widget to append to
            data: The data to format and display
            data_type: The data type (incoming, outgoing, status, error)
            show_timestamp: Whether to show timestamp prefix
        """
        # Set explicit monospace font on the widget (matching CommandFormatter)
        self._ensure_monospace_font(text_edit)
        
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)
        
        # Add newline if needed
        if text_edit.toPlainText() and not text_edit.toPlainText().endswith('\n'):
            cursor.insertText('\n')
        
        # Add timestamp if requested
        if show_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
            timestamp_format = self._get_format(self.colors['timestamp'])
            cursor.insertText(f"[{timestamp}] ", timestamp_format)
        
        # Add data type prefix for non-incoming data
        if data_type != "incoming":
            prefix_color = self.colors.get(data_type, self.colors['default'])
            prefix_format = self._get_format(prefix_color, bold=True)
            
            prefix_map = {
                'outgoing': 'TX',
                'status': 'STATUS',
                'error': 'ERROR'
            }
            prefix = prefix_map.get(data_type, data_type.upper())
            cursor.insertText(f"[{prefix}] ", prefix_format)
        
        # Format the data content
        data_color = self.colors.get(data_type, self.colors['default'])
        data_format = self._get_format(data_color)
        cursor.insertText(data, data_format)
        
        # Auto-scroll to bottom
        text_edit.ensureCursorVisible()
    
    def append_separator(self, text_edit: QTextEdit, label: str = ""):
        """
        Add a visual separator line to the terminal stream.
        
        Args:
            text_edit: The QTextEdit widget to insert into
            label: Optional label for the separator
        """
        # Set explicit monospace font on the widget (matching CommandFormatter)
        self._ensure_monospace_font(text_edit)
        
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)
        
        # Add spacing before separator (matching CommandFormatter spacing)
        if text_edit.toPlainText() and not text_edit.toPlainText().endswith('\n'):
            cursor.insertText('\n')
        cursor.insertText('\n', self._get_format(self.colors['default']))
        
        # Add separator line using dashed line (matching CommandFormatter)
        separator = "-" * 60
        separator_format = self._get_format(self.colors['separator'])
        cursor.insertText(separator + "\n", separator_format)
        
        # Add label if provided
        if label:
            label_format = self._get_format(self.colors['status'], bold=True)
            cursor.insertText(f" {label} \n", label_format)
            cursor.insertText(separator + "\n", separator_format)
        
        cursor.insertText('\n', self._get_format(self.colors['default']))
        
        # Auto-scroll to bottom
        text_edit.ensureCursorVisible()
    
    def append_status(self, text_edit: QTextEdit, message: str, status_type: str = "status"):
        """
        Add a status message to the terminal stream.
        
        Args:
            text_edit: The QTextEdit widget to append to
            message: The status message
            status_type: The status type (status, error)
        """
        self.append_data(text_edit, message, status_type, show_timestamp=True)
    
    def clear(self, text_edit: QTextEdit):
        """Clear all content from the text edit."""
        text_edit.clear()
    
    def format_connection_start(self, text_edit: QTextEdit, port_name: str, baud_rate: int):
        """
        Format the connection start message.
        
        Args:
            text_edit: The QTextEdit widget to insert into
            port_name: The name of the connected port
            baud_rate: The baud rate
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.append_separator(text_edit, f"CONNECTION STARTED - {timestamp}")
        self.append_status(text_edit, f"Connected to {port_name} at {baud_rate} baud", "status")
        self.append_separator(text_edit)
    
    def format_connection_end(self, text_edit: QTextEdit, port_name: str):
        """
        Format the connection end message.
        
        Args:
            text_edit: The QTextEdit widget to insert into
            port_name: The name of the disconnected port
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.append_separator(text_edit, f"CONNECTION ENDED - {timestamp}")
        self.append_status(text_edit, f"Disconnected from {port_name}", "status")
        self.append_separator(text_edit)