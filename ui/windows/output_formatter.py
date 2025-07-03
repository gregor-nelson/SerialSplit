"""
Output Log Formatter Module

This module provides formatting capabilities for output log messages,
applying consistent styling and color-coding based on log levels.
"""

from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from PyQt6.QtWidgets import QTextEdit


class OutputLogFormatter:
    """
    Formats output log messages with color-coded log levels and consistent styling.
    
    Follows the same professional color scheme as CommandFormatter for UI consistency.
    """
    
    def __init__(self):
        """Initialize the formatter with color definitions for different log levels."""
        # Professional muted color scheme matching CommandFormatter style
        self.colors = {
            'info': '#2c2c2c',        # Dark gray for regular info
            'success': '#2a7f3e',     # Muted green for success
            'warning': '#cc6600',     # Muted orange for warnings
            'error': '#994444',       # Muted red for errors
            'debug': '#7a7a7a',       # Light gray for debug
            'highlight': '#0066cc',   # Subtle blue for emphasis
            'default': '#2c2c2c',     # Default text color
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
            fmt.setFontFamily("Consolas, 'Courier New', monospace")
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            self._format_cache[cache_key] = fmt
            
        return self._format_cache[cache_key]
    
    def append_log(self, text_edit: QTextEdit, message: str, level: str = "info"):
        """
        Format and append a log message to the text edit widget.
        
        Args:
            text_edit: The QTextEdit widget to append to
            message: The log message to format
            level: The log level (info, success, warning, error, debug)
        """
        # Set explicit monospace font on the widget (matching CommandFormatter)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        text_edit.setFont(font)
        
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)
        
        # Add newline if needed
        if text_edit.toPlainText() and not text_edit.toPlainText().endswith('\n'):
            cursor.insertText('\n')
        
        # Get color for the log level
        level_lower = level.lower()
        color = self.colors.get(level_lower, self.colors['default'])
        
        # Format log level prefix if not info
        if level_lower != "info":
            # Add log level prefix with appropriate formatting
            level_format = self._get_format(color, bold=True)
            prefix = f"[{level.upper()}] "
            cursor.insertText(prefix, level_format)
        
        # Format the message content
        message_format = self._get_format(color)
        cursor.insertText(message, message_format)
    
    def format_section_header(self, text_edit: QTextEdit, header: str):
        """
        Format a section header in the output log.
        
        Args:
            text_edit: The QTextEdit widget to insert into
            header: The header text
        """
        # Set explicit monospace font on the widget (matching CommandFormatter)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        text_edit.setFont(font)
        
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)
        
        # Add spacing before section (matching CommandFormatter spacing)
        if text_edit.toPlainText() and not text_edit.toPlainText().endswith('\n'):
            cursor.insertText('\n')
        cursor.insertText('\n', self._get_format(self.colors['default']))
        
        # Add separator line using dashed line (matching CommandFormatter)
        separator = "-" * 60
        separator_format = self._get_format(self.colors['debug'])
        cursor.insertText(separator + "\n", separator_format)
        
        # Add header text
        header_format = self._get_format(self.colors['highlight'], bold=True)
        cursor.insertText(header + "\n", header_format)
        
        # Add separator line with spacing after (matching CommandFormatter)
        cursor.insertText(separator + "\n\n", separator_format)
    
    def format_key_value(self, text_edit: QTextEdit, key: str, value: str):
        """
        Format a key-value pair in the output log.
        
        Args:
            text_edit: The QTextEdit widget to insert into
            key: The key text
            value: The value text
        """
        # Set explicit monospace font on the widget (matching CommandFormatter)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        text_edit.setFont(font)
        
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)
        
        # Add newline if needed
        if text_edit.toPlainText() and not text_edit.toPlainText().endswith('\n'):
            cursor.insertText('\n')
        
        # Format key
        key_format = self._get_format(self.colors['highlight'])
        cursor.insertText(f"{key}: ", key_format)
        
        # Format value
        value_format = self._get_format(self.colors['default'])
        cursor.insertText(value, value_format)
    
    def clear(self, text_edit: QTextEdit):
        """Clear all content from the text edit."""
        text_edit.clear()