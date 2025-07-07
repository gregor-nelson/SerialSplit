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
import re
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
        
        # NMEA message color mapping - bright colors optimized for dark backgrounds
        # Using high-contrast hex colors that are clearly visible on dark terminals
        self.nmea_colors = {
            # Navigation/Position messages - Bright Cyan Blue
            'GGA': '#00D7FF',     # Global Positioning System Fix Data - Bright cyan
            'GLL': '#00D7FF',     # Geographic Position - Bright cyan
            'RMC': '#00D7FF',     # Recommended Minimum Navigation Information - Bright cyan
            'ZDA': '#00D7FF',     # Date & Time - Bright cyan
            
            # Depth/Sonar messages - Bright Teal
            'DBS': '#00FFAA',     # Depth Below Surface - Bright teal/aqua
            'DBT': '#00FFAA',     # Depth Below Transducer - Bright teal/aqua
            'DPT': '#00FFAA',     # Depth - Bright teal/aqua
            'SONDEP': '#00FFAA',  # Sonar Depth - Bright teal/aqua
            
            # Heading/Attitude messages - Bright Purple/Magenta
            'HDT': '#FF88FF',     # Heading True - Bright magenta
            'HPR': '#FF88FF',     # Heading, Pitch, Roll - Bright magenta
            'PASHR': '#FF88FF',   # Proprietary Attitude Sensor - Bright magenta
            'THS': '#FF88FF',     # True Heading and Status - Bright magenta
            
            # Velocity/Motion messages - Bright Green
            'VBW': '#00FF88',     # Dual Ground/Water Speed - Bright green
            'VDR': '#00FF88',     # Set and Drift - Bright green
            'VHW': '#00FF88',     # Water Speed and Heading - Bright green
            'VTG': '#00FF88',     # Track Made Good and Ground Speed - Bright green
            
            # Weather/Environmental messages - Bright Orange
            'WIMDA': '#FFAA00',   # Meteorological Composite - Bright orange
            'WIMWD': '#FFAA00',   # Wind Direction and Speed - Bright orange
            'WIMWV': '#FFAA00',   # Wind Speed and Angle - Bright orange
            
            # Satellite/GPS messages - Bright Yellow
            'GSA': '#FFFF00',     # GNSS DOP and Active Satellites - Bright yellow
            'GST': '#FFFF00',     # GNSS Pseudorange Error Statistics - Bright yellow
            'GSV': '#FFFF00',     # GNSS Satellites in View - Bright yellow
            'GRS': '#FFFF00',     # GNSS Range Residuals - Bright yellow
            
            # Proprietary messages - Bright Violet
            'PSAT': '#AA88FF',    # Proprietary Satellite - Bright violet
            'PSONNAV': '#AA88FF', # Proprietary Navigation - Bright violet
            'PSXN': '#AA88FF',    # Proprietary System - Bright violet
            'PTNL': '#AA88FF',    # Proprietary Trimble - Bright violet
            'PDWA': '#AA88FF',    # Proprietary Dynamic Wayfinding - Bright violet
            
            # AIS messages - Bright Red
            'AIVDM': '#FF4444',   # AIS VDM message - Bright red
            
            # Other/miscellaneous messages - Light Gray
            'DRU': '#CCCCCC',     # Dual Rudder - Light gray
            'HEV': '#CCCCCC',     # Heave - Light gray
            'ROV': '#CCCCCC',     # Remotely Operated Vehicle - Light gray
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
    
    def _detect_nmea_message_type(self, data: str) -> str:
        """
        Detect and classify NMEA message type from data string.
        
        Args:
            data: The incoming data string to analyze
            
        Returns:
            The NMEA message type or None if not detected
        """
        # Strip whitespace and check for NMEA patterns
        data = data.strip()
        
        # Check for AIS messages (starts with !)
        if data.startswith('!AIVDM'):
            return 'AIVDM'
        
        # Check for standard NMEA messages (starts with $)
        if data.startswith('$'):
            # Extract message type from standard NMEA format
            # Format: $AABBB,... where AA is talker ID and BBB is message type
            # Also handle proprietary formats like $PSAT,HPR or $PSONNAV
            
            # Remove leading $
            nmea_data = data[1:]
            
            # Split by comma to get the first field
            fields = nmea_data.split(',')
            if not fields:
                return None
            
            header = fields[0]
            
            # Handle proprietary messages with specific patterns
            if header.startswith('PSAT') and len(fields) > 1 and fields[1] == 'HPR':
                return 'PSAT'
            elif header.startswith('PSONNAV'):
                return 'PSONNAV'
            elif header.startswith('PSXN'):
                return 'PSXN'
            elif header.startswith('PTNL') and len(fields) > 1 and fields[1] == 'AVR':
                return 'PTNL'
            elif header.startswith('PDWA'):
                return 'PDWA'
            
            # Handle standard NMEA messages
            if len(header) >= 5:
                # Standard format: AABBB (AA=talker, BBB=message type)
                message_type = header[2:5]  # Extract BBB part
                
                # Check if it's in our color mapping
                if message_type in self.nmea_colors:
                    return message_type
                
                # Handle full header matches (for proprietary messages)
                if header in self.nmea_colors:
                    return header
            
            # Handle special cases where message type is longer or different
            for nmea_type in self.nmea_colors:
                if header.startswith(nmea_type) or header.endswith(nmea_type):
                    return nmea_type
        
        return None
    
    def append_data(self, text_edit: QTextEdit, data: str, data_type: str = "incoming", 
                   show_timestamp: bool = True):
        """
        Format and append serial data to the text edit widget.
        
        Args:
            text_edit: The QTextEdit widget to append to
            data: The data to format and display (should be a single line)
            data_type: The data type (incoming, outgoing, status, error)
            show_timestamp: Whether to show timestamp prefix
        """
        # Set explicit monospace font on the widget (matching CommandFormatter)
        self._ensure_monospace_font(text_edit)
        
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        text_edit.setTextCursor(cursor)
        
        # Add newline if needed (unless this is the first line)
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
        
        # Detect NMEA message type and use appropriate color
        nmea_type = None
        if data_type == "incoming":  # Only colorize incoming data
            nmea_type = self._detect_nmea_message_type(data)
        
        # Choose color based on NMEA type or default data type
        if nmea_type and nmea_type in self.nmea_colors:
            data_color = self.nmea_colors[nmea_type]
        else:
            data_color = self.colors.get(data_type, self.colors['default'])
        
        # Format the data content
        data_format = self._get_format(data_color)
        cursor.insertText(data, data_format)
        
        # Add newline at the end
        cursor.insertText('\n')
        
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