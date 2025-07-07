#!/usr/bin/env python3
"""
Terminal Stream Formatter Module

This module provides formatting capabilities for terminal stream data,
applying consistent styling and color-coding for serial port communication.
Follows the same professional styling as CommandFormatter and OutputLogFormatter.
"""

import time
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
        
        # Windows 10 Dark Mode NMEA Message Colors - Muted Terminal Palette with Subtle Variations
        # Optimized for reduced eye strain and professional appearance in streaming data
        self.nmea_colors = {
            # Navigation/Position messages - Muted Blue Family (subtle variations)
            'GGA': '#8bb5d9',     # Global Positioning System Fix Data - Base soft blue
            'GLL': '#7ba8cc',     # Geographic Position - Slightly darker blue
            'RMC': '#9bc2e6',     # Recommended Minimum Navigation Information - Slightly lighter blue
            'ZDA': '#85b0d6',     # Date & Time - Slightly grayer blue
            
            # Depth/Sonar messages - Muted Green Family (subtle variations)
            'DBS': '#90c695',     # Depth Below Surface - Base soft green
            'DBT': '#84b989',     # Depth Below Transducer - Slightly darker green
            'DPT': '#9cd3a1',     # Depth - Slightly lighter green
            'DEP': '#8ac093',     # Depth (alternate format) - Slightly grayer green
            'SONDEP': '#96cc99',  # Sonar Depth - Slightly more saturated green
            
            # Heading/Attitude messages - Muted Purple Family (subtle variations)
            'HDT': '#b4a7d6',     # Heading True - Base soft purple
            'HPR': '#a89ac9',     # Heading, Pitch, Roll - Slightly darker purple
            'PASHR': '#c0b4e3',   # Proprietary Attitude Sensor - Slightly lighter purple
            'THS': '#b1a3d3',     # True Heading and Status - Slightly grayer purple
            'HEV': '#aea0d0',     # Heave - Slightly more muted purple
            
            # Velocity/Motion messages - Muted Teal Family (subtle variations)
            'VBW': '#7fb8c4',     # Dual Ground/Water Speed - Base soft teal
            'VDR': '#73abb7',     # Set and Drift - Slightly darker teal
            'VHW': '#8bc5d1',     # Water Speed and Heading - Slightly lighter teal
            'VTG': '#79b5c1',     # Track Made Good and Ground Speed - Slightly grayer teal
            
            # Weather/Environmental messages - Muted Orange Family (subtle variations)
            'WIMDA': '#d4a574',   # Meteorological Composite - Base soft orange
            'WIMWD': '#c89866',   # Wind Direction and Speed - Slightly darker orange
            'WIMWV': '#e0b282',   # Wind Speed and Angle - Slightly lighter orange
            'MDA': '#d1a271',     # Meteorological Composite (short form) - Slightly grayer orange
            'MWD': '#cb9b69',     # Wind Direction and Speed (short form) - Slightly more muted orange
            'MWV': '#ddaf7f',     # Wind Speed and Angle (short form) - Slightly warmer orange
            
            # Satellite/GPS messages - Muted Yellow Family (subtle variations)
            'GSA': '#d4c875',     # GNSS DOP and Active Satellites - Base soft yellow
            'GST': '#c8bb69',     # GNSS Pseudorange Error Statistics - Slightly darker yellow
            'GSV': '#e0d581',     # GNSS Satellites in View - Slightly lighter yellow
            'GRS': '#d1c572',     # GNSS Range Residuals - Slightly grayer yellow
            
            # Proprietary messages - Muted Pink/Rose Family (subtle variations)
            'PSAT': '#c99bb3',    # Proprietary Satellite - Base soft rose
            'PSONNAV': '#bd8fa7', # Proprietary Navigation - Slightly darker rose
            'PSXN': '#d5a7bf',    # Proprietary System - Slightly lighter rose
            'PTNL': '#c698b0',    # Proprietary Trimble - Slightly grayer rose
            'PDWA': '#c295ad',    # Proprietary Dynamic Wayfinding - Slightly more muted rose
            
            # AIS messages - Muted Red Family
            'AIVDM': '#cc8888',   # AIS VDM message - Soft red
            
            # Other/miscellaneous messages - Neutral Gray Family (subtle variations)
            'DRU': '#a0a0a0',     # Dual Rudder - Light gray
            'ROV': '#959595',     # Remotely Operated Vehicle - Slightly darker gray
            'NMEA_UNKNOWN': '#888888',  # Unknown NMEA message - Medium gray
        }
        
        # Create format cache for performance with size limit
        self._format_cache = {}
        self._max_cache_size = 100
        
        # Initialize robust parsing state
        self._init_robust_parsing_state()
        
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
            # Clear cache if it gets too large
            if len(self._format_cache) >= self._max_cache_size:
                self._format_cache.clear()
            
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            # Use the same font family as CommandFormatter for consistency
            fmt.setFontFamily(AppFonts.CONSOLE_FAMILY)
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            self._format_cache[cache_key] = fmt
            
        return self._format_cache[cache_key]
    
    def _init_robust_parsing_state(self):
        """Initialize robust parsing state management."""
        self.line_buffer = ""
        self.consecutive_failures = 0
        self.last_successful_parse = time.time()
        self.total_messages_processed = 0
        self.successful_nmea_detections = 0
        self.parser_state = "normal"  # normal, degraded, recovery
        self.last_known_good_message_type = None
        
        # Comprehensive fallback patterns with dynamic talker ID support
        self.fallback_patterns = [
            # Standard GPS/GNSS messages (any talker ID)
            (r'\$[A-Z]{2}GGA', 'GGA'),  # Global Positioning System Fix Data
            (r'\$[A-Z]{2}RMC', 'RMC'),  # Recommended Minimum Navigation Information
            (r'\$[A-Z]{2}GLL', 'GLL'),  # Geographic Position - Latitude/Longitude
            (r'\$[A-Z]{2}GSA', 'GSA'),  # GNSS DOP and Active Satellites
            (r'\$[A-Z]{2}GSV', 'GSV'),  # GNSS Satellites in View
            (r'\$[A-Z]{2}VTG', 'VTG'),  # Track Made Good and Ground Speed
            (r'\$[A-Z]{2}ZDA', 'ZDA'),  # UTC Time and Date
            (r'\$[A-Z]{2}GST', 'GST'),  # GNSS Pseudorange Error Statistics
            (r'\$[A-Z]{2}GRS', 'GRS'),  # GNSS Range Residuals
            
            # Depth/Sonar messages (any talker ID)
            (r'\$[A-Z]{2}DBS', 'DBS'),  # Depth Below Surface
            (r'\$[A-Z]{2}DBT', 'DBT'),  # Depth Below Transducer
            (r'\$[A-Z]{2}DPT', 'DPT'),  # Depth of Water
            (r'\$[A-Z]{2}DEP', 'DEP'),  # Depth (alternate format)
            
            # Heading/Attitude messages (any talker ID)
            (r'\$[A-Z]{2}HDT', 'HDT'),  # Heading True
            (r'\$[A-Z]{2}THS', 'THS'),  # True Heading and Status
            (r'\$[A-Z]{2}HPR', 'HPR'),  # Heading, Pitch, Roll
            (r'\$[A-Z]{2}HEV', 'HEV'),  # Heave
            
            # Velocity/Motion messages (any talker ID)
            (r'\$[A-Z]{2}VBW', 'VBW'),  # Dual Ground/Water Speed
            (r'\$[A-Z]{2}VDR', 'VDR'),  # Set and Drift
            (r'\$[A-Z]{2}VHW', 'VHW'),  # Water Speed and Heading
            
            # Weather/Environmental messages (any talker ID - both forms)
            (r'\$[A-Z]{2}MWV', 'MWV'),  # Wind Speed and Angle
            (r'\$[A-Z]{2}MWD', 'MWD'),  # Wind Direction and Speed
            (r'\$[A-Z]{2}MDA', 'MDA'),  # Meteorological Composite
            (r'\$..MWV', 'WIMWV'),      # Legacy mapping
            (r'\$..MWD', 'WIMWD'),      # Legacy mapping
            (r'\$..MDA', 'WIMDA'),      # Legacy mapping
            
            # Other messages (any talker ID)
            (r'\$[A-Z]{2}DRU', 'DRU'),  # Dual Rudder
            (r'\$[A-Z]{2}ROV', 'ROV'),  # Remotely Operated Vehicle
            
            # Proprietary messages
            (r'\$PASHR', 'PASHR'),      # Proprietary Attitude and Heading Reference
            (r'\$PSAT,HPR', 'PSAT'),    # Proprietary Satellite - Attitude Data
            (r'\$PSONNAV', 'PSONNAV'),  # Proprietary Navigation
            (r'\$PSXN', 'PSXN'),        # Proprietary Extended Navigation
            (r'\$PTNL,AVR', 'PTNL'),    # Proprietary Trimble - Attitude and Velocity
            (r'\$PDWA', 'PDWA'),        # Proprietary Dynamic Water Analysis
            
            # AIS messages
            (r'\!AIVDM', 'AIVDM'),      # AIS VHF Data-Link Message
        ]
        
        # Known NMEA talker IDs for validation
        self.known_talkers = {
            'GP': 'Global Positioning System',
            'GN': 'Global Navigation Satellite System',
            'GL': 'GLONASS',
            'GA': 'Galileo',
            'BD': 'BeiDou',
            'GB': 'BeiDou',
            'GQ': 'QZSS',
            'II': 'Integrated Instrumentation',
            'IN': 'Integrated Navigation',
            'LC': 'Loran-C',
            'EC': 'Electronic Chart Display',
            'CD': 'Digital Selective Calling',
            'HC': 'Heading/Compass',
            'HE': 'Gyro North Seeking',
            'RA': 'Radar',
            'SD': 'Sounder/Depth',
            'TI': 'Turn Indicator',
            'VD': 'Velocity Sensor',
            'VW': 'Mechanical Speed Log',
            'WI': 'Weather Instruments',
            'YX': 'Transducer',
            'ZA': 'Atomic Clock',
            'ZV': 'Radio beacon'
        }
        
        # Compile regex patterns for performance with error handling
        self.compiled_patterns = []
        for pattern, msg_type in self.fallback_patterns:
            try:
                self.compiled_patterns.append((re.compile(pattern), msg_type))
            except re.error:
                # Skip invalid patterns silently to maintain stability
                continue
    
    def _is_valid_nmea_structure(self, line: str) -> bool:
        """Validate basic NMEA message structure."""
        if not line or len(line) < 7:  # Minimum viable NMEA length
            return False
        
        line = line.strip()
        
        # Check NMEA sentence structure
        if line.startswith('$') and '*' in line:
            parts = line.split('*')
            if len(parts) == 2:
                sentence_part = parts[0]
                checksum_part = parts[1]
                
                # Validate checksum format (2 hex characters)
                if len(checksum_part) >= 2 and all(c in '0123456789ABCDEFabcdef' for c in checksum_part[:2]):
                    # Validate sentence has at least talker ID and message type
                    if len(sentence_part) >= 6 and sentence_part[1:].replace(',', '').replace('.', '').replace('-', '').isalnum():
                        return True
        
        # Check AIS message structure
        if line.startswith('!') and '*' in line:
            parts = line.split('*')
            if len(parts) == 2 and len(parts[1]) >= 2:
                return True
        
        return False
    
    def _calculate_checksum(self, sentence: str) -> str:
        """Calculate NMEA checksum for validation."""
        checksum = 0
        for char in sentence:
            checksum ^= ord(char)
        return f"{checksum:02X}"
    
    def _validate_nmea_checksum(self, line: str) -> bool:
        """Validate NMEA checksum if present."""
        if '*' not in line:
            return False
        
        try:
            sentence_part, checksum_part = line.split('*', 1)
            if len(checksum_part) < 2:
                return False
            
            # Remove leading $ or !
            if sentence_part.startswith(('$', '!')):
                sentence_part = sentence_part[1:]
            
            expected_checksum = self._calculate_checksum(sentence_part)
            actual_checksum = checksum_part[:2].upper()
            
            return expected_checksum == actual_checksum
        except Exception:
            return False
    
    def _preprocess_data_line(self, raw_line: str) -> str:
        """Safely preprocess a data line for parsing."""
        if not raw_line:
            return ""
        
        # Remove common line endings and extra whitespace
        line = raw_line.strip('\r\n\t ')
        
        # Remove non-printable characters except for standard NMEA chars
        line = ''.join(c for c in line if c.isprintable() or c in '\r\n')
        
        # Remove checksum portion for field parsing (keep for validation)
        if '*' in line:
            line_for_parsing = line.split('*')[0]
        else:
            line_for_parsing = line
        
        return line_for_parsing.strip()
    
    def _detect_nmea_with_fallback(self, line: str) -> str:
        """Detect NMEA message type using primary method with fallback."""
        # Try primary detection first
        msg_type = self._detect_nmea_message_type(line)
        if msg_type and msg_type in self.nmea_colors:
            return msg_type
        
        # Try fallback regex patterns with error handling
        for pattern, fallback_type in self.compiled_patterns:
            try:
                if pattern.search(line):
                    if fallback_type in self.nmea_colors:
                        return fallback_type
            except (re.error, TypeError):
                # Skip problematic patterns to maintain stability
                continue
        
        # If it looks like NMEA but we can't classify it, return generic type
        if self._is_valid_nmea_structure(line):
            return 'NMEA_UNKNOWN'
        
        return None
    
    def _update_parser_statistics(self, success: bool, msg_type: str = None):
        """Update parser statistics and state."""
        self.total_messages_processed += 1
        
        if success:
            self.successful_nmea_detections += 1
            self.consecutive_failures = 0
            self.last_successful_parse = time.time()
            if msg_type:
                self.last_known_good_message_type = msg_type
        else:
            self.consecutive_failures += 1
        
        # Update parser state based on success rate
        if self.consecutive_failures > 10:
            self.parser_state = "degraded"
        elif self.consecutive_failures > 20:
            self.parser_state = "recovery"
        else:
            self.parser_state = "normal"
    
    def _should_reset_parser_state(self) -> bool:
        """Determine if parser state should be reset."""
        # Reset if too many consecutive failures
        if self.consecutive_failures > 30:
            return True
        
        # Reset if no successful parse in too long
        if time.time() - self.last_successful_parse > 300:  # 5 minutes
            return True
        
        return False
    
    def _reset_parser_state(self):
        """Reset parser state to recover from errors."""
        self.line_buffer = ""
        self.consecutive_failures = 0
        self.parser_state = "normal"
        self.last_successful_parse = time.time()
    
    def _process_complete_line(self, line: str) -> tuple:
        """Process a complete line and return (message_type, processed_line)."""
        if not line:
            return None, line
        
        # Preprocess the line
        processed_line = self._preprocess_data_line(line)
        if not processed_line:
            return None, line
        
        # Validate NMEA structure if it looks like NMEA
        if processed_line.startswith(('$', '!')):
            if not self._is_valid_nmea_structure(line):
                self._update_parser_statistics(False)
                return None, line
            
            # Validate checksum if in strict mode
            if self.parser_state == "normal":
                if not self._validate_nmea_checksum(line):
                    self._update_parser_statistics(False)
                    return None, line
        
        # Detect message type with fallback
        msg_type = self._detect_nmea_with_fallback(processed_line)
        
        if msg_type:
            self._update_parser_statistics(True, msg_type)
            return msg_type, line
        else:
            self._update_parser_statistics(False)
            return None, line
    
    def process_serial_data(self, raw_data: str) -> list:
        """Process raw serial data and return list of (message_type, line) tuples."""
        if not raw_data:
            return []
        
        # Basic input size validation
        if len(raw_data) > 50000:  # Limit single data chunk size
            raw_data = raw_data[:50000]
        
        # Reset parser state if necessary
        if self._should_reset_parser_state():
            self._reset_parser_state()
        
        # Add to line buffer with size limit
        self.line_buffer += raw_data
        
        # Prevent buffer from growing too large
        if len(self.line_buffer) > 10000:
            # Keep only the last 5000 characters
            self.line_buffer = self.line_buffer[-5000:]
        
        # Split into lines
        lines = self.line_buffer.split('\n')
        
        # Keep the last incomplete line in buffer
        self.line_buffer = lines[-1]
        
        # Process complete lines
        processed_lines = []
        for line in lines[:-1]:
            msg_type, processed_line = self._process_complete_line(line)
            processed_lines.append((msg_type, processed_line))
        
        return processed_lines
    
    def append_serial_data(self, text_edit: QTextEdit, raw_data: str, data_type: str = "incoming", 
                          show_timestamp: bool = True):
        """Process and append serial data using robust parsing."""
        if not raw_data:
            return
        
        # Process the raw data through robust parsing
        processed_lines = self.process_serial_data(raw_data)
        
        # Append each processed line
        for msg_type, line in processed_lines:
            if msg_type:
                # Use detected NMEA type for coloring
                self.append_data(text_edit, line, data_type, show_timestamp)
            else:
                # Fall back to default coloring
                self.append_data(text_edit, line, data_type, show_timestamp)
    
    def get_parser_statistics(self) -> dict:
        """Get current parser statistics for debugging."""
        success_rate = 0
        if self.total_messages_processed > 0:
            success_rate = (self.successful_nmea_detections / self.total_messages_processed) * 100
        
        return {
            'total_processed': self.total_messages_processed,
            'successful_detections': self.successful_nmea_detections,
            'consecutive_failures': self.consecutive_failures,
            'success_rate': success_rate,
            'parser_state': self.parser_state,
            'last_known_good_type': self.last_known_good_message_type,
            'buffer_size': len(self.line_buffer)
        }
    
    def _ensure_monospace_font(self, text_edit: QTextEdit):
        """Ensure the text edit uses consistent monospace font."""
        font = QFont(AppFonts.CONSOLE.family(), AppFonts.FONT_SIZE_LARGE)
        font.setStyleHint(QFont.StyleHint.Monospace)
        text_edit.setFont(font)
    
    def _detect_nmea_message_type(self, data: str) -> str:
        """
        Enhanced NMEA message type detection with dynamic talker ID support.
        
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
            elif header.startswith('PASHR'):
                return 'PASHR'
            
            # Handle standard NMEA messages with dynamic talker ID detection
            if len(header) >= 3:
                # Extract potential talker ID and message type
                if len(header) >= 5:
                    # Standard format: AABBB (AA=talker, BBB=message type)
                    potential_talker = header[:2]
                    message_type = header[2:]
                    
                    # Validate talker ID (known talkers or alphabetic)
                    if potential_talker in self.known_talkers or potential_talker.isalpha():
                        # Check if message type is in our color mapping
                        if message_type in self.nmea_colors:
                            return message_type
                        
                        # Handle weather messages (check for MWV, MWD, MDA)
                        if message_type in ['MWV', 'MWD', 'MDA']:
                            return message_type
                        
                        # Handle depth messages (DEP)
                        if message_type == 'DEP':
                            return 'DEP'
                        
                        # Handle longer message types (like WIMWV, WIMWD, WIMDA)
                        if len(message_type) > 3:
                            short_type = message_type[-3:]  # Get last 3 characters
                            if short_type in self.nmea_colors:
                                return short_type
                
                # Handle cases where the entire header might be the message type
                if header in self.nmea_colors:
                    return header
                
                # Handle partial matches for complex proprietary messages
                for nmea_type in self.nmea_colors:
                    if len(nmea_type) > 3 and header.endswith(nmea_type):
                        return nmea_type
                    elif header.startswith(nmea_type):
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
        # Basic null check
        if not text_edit or not data:
            return
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
            nmea_type = self._detect_nmea_with_fallback(data)
        
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
        # Basic null check
        if not text_edit:
            return
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
        # Basic null check
        if not text_edit or not message:
            return
        self.append_data(text_edit, message, status_type, show_timestamp=True)
    
    def clear(self, text_edit: QTextEdit):
        """Clear all content from the text edit."""
        if text_edit:
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