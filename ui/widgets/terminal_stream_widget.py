#!/usr/bin/env python3
"""
Terminal Stream Widget - Real-time serial data display
Provides a simple terminal window for logging incoming serial data
"""

from typing import Optional
import threading

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame, QSizePolicy, QMenu, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal, QByteArray
from PyQt6.QtGui import QTextCursor, QAction, QFont, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

from core.core import SerialPortInfo, SerialPortMonitor
from ui.theme.theme import (
    ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts
)
from ui.theme.icons.icons import AppIcons
from ui.windows.terminal_formatter import TerminalStreamFormatter


class TerminalStreamWidget(QWidget):
    """
    Simple terminal stream widget for real-time serial data display.
    Follows the same design patterns as monitor and test widgets.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_port: Optional[SerialPortInfo] = None
        self.port_monitor: Optional[SerialPortMonitor] = None
        self.formatter = TerminalStreamFormatter()
        self.line_buffer = ""  # Buffer for incomplete lines
        self.buffer_timer = QTimer()
        self.buffer_timer.setSingleShot(True)
        self.buffer_timer.timeout.connect(self._flush_buffer)
        self.encoding = 'utf-8'  # Default encoding
        self.hex_display_mode = False  # Toggle for hex display mode
        
        # Dynamic configuration
        self.current_baud_rate = 9600  # Default baud rate
        
        # User preference settings
        self.auto_scroll_enabled = True
        self.current_font_size = AppFonts.FONT_SIZE_LARGE
        self.word_wrap_enabled = False
        
        self.init_ui()
    
    def checkbox_icon(self, checked: bool) -> QIcon:
        """Generate Windows 10 style checkbox icon"""
        if checked:
            svg = f'''<svg width="16" height="16" xmlns="http://www.w3.org/2000/svg">
                <rect x="0.5" y="0.5" width="15" height="15" fill="{AppColors.CHECKBOX_BORDER_COLOR}" stroke="{AppColors.CHECKBOX_BORDER_COLOR}" stroke-width="1"/>
                <rect x="2" y="2" width="12" height="12" fill="{AppColors.CHECKBOX_CHECK_BACKGROUND}"/>
                <path d="M4 8l2 2 6-6" stroke="{AppColors.CHECKBOX_CHECK_COLOR}" stroke-width="1.5" fill="none" stroke-linecap="round"/>
            </svg>'''
        else:
            svg = f'''<svg width="16" height="16" xmlns="http://www.w3.org/2000/svg">
                <rect x="0.5" y="0.5" width="15" height="15" fill="{AppColors.CHECKBOX_BORDER_COLOR}" stroke="{AppColors.CHECKBOX_BORDER_COLOR}" stroke-width="1"/>
            </svg>'''
        
        renderer = QSvgRenderer(QByteArray(svg.encode()))
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
        
    def init_ui(self):
        """Initialize the user interface with theme integration"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section - matching monitor/test widget style
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(28)  # Match monitor widget height
        self.header_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
            }}
        """)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_SMALL,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_SMALL
        )
        header_layout.setSpacing(AppDimensions.SPACING_LARGE)
        
        # Port info section (left) - matching monitor widget
        port_section = QHBoxLayout()
        port_section.setSpacing(AppDimensions.SPACING_SMALL)
        port_section.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Port status indicator (small colored bar) - matching monitor widget
        self.status_indicator = QFrame()
        self.status_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.TEXT_DISABLED};
                border: none;
            }}
        """)
        port_section.addWidget(self.status_indicator, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Port name and type - matching monitor widget
        self.port_label = QLabel("No port selected")
        self.port_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                background: transparent;
                border: none;
            }}
        """)
        self.port_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        port_section.addWidget(self.port_label)
        
        # Set status indicator height to match port label font height
        label_font_metrics = self.port_label.fontMetrics()
        label_height = label_font_metrics.height()
        self.status_indicator.setFixedSize(3, label_height)
        
        header_layout.addLayout(port_section)
        header_layout.addStretch()
        
        # Control section (right) - matching monitor widget
        control_section = QHBoxLayout()
        control_section.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setFixedSize(24, 24)
        self.settings_btn.setToolTip("Terminal settings")
        self.settings_btn.clicked.connect(self.show_settings_menu)
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_HOVER};
                border: 1px solid {AppColors.BORDER_DEFAULT};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_PRESSED};
            }}
        """)
        self._update_settings_button_icon()
        control_section.addWidget(self.settings_btn)
        
        # Clear button
        self.clear_btn = QPushButton()
        self.clear_btn.setFixedSize(24, 24)
        self.clear_btn.setToolTip("Clear terminal")
        self.clear_btn.clicked.connect(self.clear_terminal)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_HOVER};
                border: 1px solid {AppColors.BORDER_DEFAULT};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_PRESSED};
            }}
        """)
        self._update_clear_button_icon()
        control_section.addWidget(self.clear_btn)
        
        # Monitor button - matching monitor widget
        self.monitor_btn = QPushButton()
        self.monitor_btn.setFixedSize(24, 24)
        self.monitor_btn.setToolTip("Start terminal monitoring")
        self.monitor_btn.clicked.connect(self.toggle_monitoring)
        self.monitor_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_HOVER};
                border: 1px solid {AppColors.BORDER_DEFAULT};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_PRESSED};
            }}
        """)
        self._update_monitor_button_icon(False)
        control_section.addWidget(self.monitor_btn)
        
        header_layout.addLayout(control_section)
        
        main_layout.addWidget(self.header_widget)
        
        # Separator line - matching monitor widget
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BORDER_DEFAULT};
                border: none;
                max-height: 1px;
            }}
        """)
        main_layout.addWidget(self.separator)
        
        # Terminal display area
        self.terminal_display = QTextEdit()
        self.terminal_display.setReadOnly(True)
        self._update_terminal_display_style()
        self.terminal_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.terminal_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Set up custom context menu
        self.terminal_display.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.terminal_display.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.terminal_display)
        
        # Initially hide everything
        self.hide_all()
    
    def _update_monitor_button_icon(self, is_monitoring: bool):
        """Update monitor button icon"""
        from ui.theme.theme import IconManager
        
        if is_monitoring:
            icon = IconManager.create_svg_icon(
                AppIcons.STOP,
                AppColors.TEXT_DEFAULT,
                IconManager.get_scaled_size(14)
            )
            self.monitor_btn.setToolTip("Stop terminal monitoring")
        else:
            icon = IconManager.create_svg_icon(
                AppIcons.PLAY,
                AppColors.TEXT_DEFAULT,
                IconManager.get_scaled_size(14)
            )
            self.monitor_btn.setToolTip("Start terminal monitoring")
        
        self.monitor_btn.setIcon(icon)
        self.monitor_btn.setIconSize(IconManager.get_scaled_size(14))
    
    def _update_settings_button_icon(self):
        """Update settings button icon"""
        from ui.theme.theme import IconManager
        
        # Try SETTINGS, GEAR, or COG icon constants, whichever is available
        # If none are available, this will need to be adjusted based on your icon constants
        icon = IconManager.create_svg_icon(
            AppIcons.TERMINAL_SETTINGS,  # Update this to match your available icon constant
            AppColors.TEXT_DEFAULT,
            IconManager.get_scaled_size(14)
        )
        self.settings_btn.setIcon(icon)
        self.settings_btn.setIconSize(IconManager.get_scaled_size(14))
    
    def _update_clear_button_icon(self):
        """Update clear button icon"""
        from ui.theme.theme import IconManager
        
        icon = IconManager.create_svg_icon(
            AppIcons.DELETE,
            AppColors.TEXT_DEFAULT,
            IconManager.get_scaled_size(14)
        )
        self.clear_btn.setIcon(icon)
        self.clear_btn.setIconSize(IconManager.get_scaled_size(14))
    
    def _apply_status_style(self, style_type: str):
        """Apply the status indicator color"""
        status_colors = {
            "available": AppColors.SUCCESS_PRIMARY,
            "in_use": AppColors.WARNING_PRIMARY,
            "unavailable": AppColors.ERROR_PRIMARY,
            "virtual": AppColors.ACCENT_BLUE,
            "moxa": AppColors.ACCENT_ORANGE,
            "monitoring": AppColors.ACCENT_GREEN,
            "info": AppColors.TEXT_DISABLED
        }
        
        color = status_colors.get(style_type, AppColors.TEXT_DISABLED)
        
        self.status_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
            }}
        """)
    
    def set_current_port(self, port_name: str, port_info: Optional[SerialPortInfo] = None, baud_rate: int = None):
        """Set the current port for terminal monitoring"""
        self.current_port = port_info
        
        # Update baud rate if provided
        if baud_rate is not None:
            self.current_baud_rate = baud_rate
        
        if port_name and port_name != "No ports available":
            # Update label to show current port
            if port_info:
                display_text = f"{port_name}"
                if port_info.description and port_info.description != "N/A":
                    desc = port_info.description[:30] + "..." if len(port_info.description) > 30 else port_info.description
                    display_text += f" - {desc}"
                
                # Update status indicator based on port type
                if port_info.is_moxa:
                    style_type = "moxa"
                elif port_info.port_type == "Physical":
                    style_type = "available"
                else:
                    style_type = "virtual"
                
                self._apply_status_style(style_type)
            else:
                display_text = f"{port_name}"
                self._apply_status_style("info")
            
            # Add baud rate to display text
            display_text += f" @ {self.current_baud_rate} baud"
            self.port_label.setText(display_text)
            self.header_widget.setVisible(True)
            self.separator.setVisible(True)
            
            # Show/hide monitor controls based on port type
            can_monitor = (port_info and (port_info.port_type == "Physical" or 
                          port_info.port_type.startswith("Virtual")))
            
            self.monitor_btn.setVisible(can_monitor)
            self.settings_btn.setVisible(True)  # Always show settings when port is selected
            
            if not can_monitor:
                self.stop_monitoring()
        else:
            self.hide_all()
    
    def update_baud_rate(self, new_baud_rate: int):
        """Update the baud rate and restart monitoring if active"""
        if new_baud_rate != self.current_baud_rate:
            self.current_baud_rate = new_baud_rate
            
            # Update the port label to show new baud rate
            if self.current_port:
                current_text = self.port_label.text()
                # Remove old baud rate info and add new one
                if ' @ ' in current_text:
                    base_text = current_text.split(' @ ')[0]
                    self.port_label.setText(f"{base_text} @ {self.current_baud_rate} baud")
            
            # If currently monitoring, restart with new baud rate
            if self.port_monitor and self.port_monitor.monitoring:
                self.stop_monitoring()
                self.start_monitoring()
    
    def toggle_monitoring(self):
        """Toggle terminal monitoring on/off"""
        if not self.current_port:
            return
            
        if self.port_monitor and self.port_monitor.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring the current port for terminal display"""
        if not self.current_port:
            return
            
        # Stop existing monitor
        self.stop_monitoring()
        
        # Create new monitor with current baud rate
        self.port_monitor = SerialPortMonitor(self.current_port.port_name, self.current_baud_rate)
        self.port_monitor.data_received.connect(self._handle_incoming_data)
        self.port_monitor.stats_updated.connect(self._handle_stats_update)
        self.port_monitor.error_occurred.connect(self._handle_monitoring_error)
        
        if self.port_monitor.start_monitoring():
            self._update_monitor_button_icon(True)
            self._apply_status_style("monitoring")
            
            # Add connection start message with current baud rate
            self.formatter.format_connection_start(
                self.terminal_display, 
                self.current_port.port_name, 
                self.current_baud_rate
            )
    
    def stop_monitoring(self):
        """Stop terminal monitoring"""
        if self.port_monitor:
            # Add connection end message if we were monitoring
            if self.port_monitor.monitoring and self.current_port:
                self.formatter.format_connection_end(
                    self.terminal_display,
                    self.current_port.port_name
                )
            
            self.port_monitor.stop_monitoring()
            self.port_monitor = None
            
        # Clear buffer and stop timer
        self.line_buffer = ""
        self.buffer_timer.stop()
        self._update_monitor_button_icon(False)
        
        # Reset status indicator
        if self.current_port:
            if self.current_port.is_moxa:
                self._apply_status_style("moxa")
            elif self.current_port.port_type == "Physical":
                self._apply_status_style("available")
            else:
                self._apply_status_style("virtual")
    
    def clear_terminal(self):
        """Clear the terminal display"""
        self.formatter.clear(self.terminal_display)
        
        # Clear the data buffer as well
        self.line_buffer = ""
        self.buffer_timer.stop()
        
        # If monitoring, add a clear separator
        if self.port_monitor and self.port_monitor.monitoring:
            self.formatter.append_separator(self.terminal_display, "Terminal cleared")
    
    def _handle_incoming_data(self, data: bytes):
        """Handle incoming serial data with proper line buffering"""
        try:
            if self.hex_display_mode:
                # Display raw hex data
                hex_data = ' '.join(f'{b:02X}' for b in data)
                ascii_data = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
                formatted_data = f"HEX: {hex_data} | ASCII: {ascii_data}"
                
                self.formatter.append_data(
                    self.terminal_display,
                    formatted_data,
                    "incoming",
                    show_timestamp=True
                )
                return
            
            # Decode bytes
            try:
                text_data = data.decode(self.encoding)
            except UnicodeDecodeError:
                # Try with replacement characters
                text_data = data.decode(self.encoding, errors='replace')
            
            # Normalize line endings
            text_data = text_data.replace('\r\n', '\n').replace('\r', '\n')
            
            # Add to line buffer
            self.line_buffer += text_data
            
            # Process complete lines
            lines = self.line_buffer.split('\n')
            
            # Display all complete lines
            for line in lines[:-1]:
                if line:  # Only display non-empty lines
                    self.formatter.append_data(
                        self.terminal_display,
                        line,
                        "incoming",
                        show_timestamp=True
                    )
            
            # Keep the last (potentially incomplete) line
            self.line_buffer = lines[-1]
            
            # Start timer for incomplete lines
            if self.line_buffer:
                self.buffer_timer.stop()
                self.buffer_timer.start(1000)  # 1 second timeout
                
        except Exception as e:
            self.formatter.append_status(
                self.terminal_display,
                f"Data processing error: {str(e)}",
                "error"
            )
    
    def _flush_buffer(self):
        """Flush remaining data in buffer"""
        if self.line_buffer:
            self.formatter.append_data(
                self.terminal_display,
                self.line_buffer,
                "incoming",
                show_timestamp=True
            )
            self.line_buffer = ""
    
    def _handle_stats_update(self, stats):
        """Handle monitoring statistics update"""
        # Terminal widget doesn't display stats
        pass
    
    def _handle_monitoring_error(self, error_msg):
        """Handle monitoring errors"""
        self.formatter.append_status(
            self.terminal_display,
            f"Port monitoring failed: {error_msg}",
            "error"
        )
        self.stop_monitoring()
    
    def hide_all(self):
        """Hide all terminal information"""
        self.header_widget.setVisible(False)
        self.separator.setVisible(False)
        self.stop_monitoring()
    
    def get_current_port(self) -> Optional[str]:
        """Get the currently set port name"""
        return self.current_port.port_name if self.current_port else None
    
    def show_settings_menu(self):
        """Show settings menu when gear button is clicked"""
        # Get the button's global position for menu placement
        button_pos = self.settings_btn.mapToGlobal(self.settings_btn.rect().bottomLeft())
        self._show_terminal_menu(button_pos)
    
    def show_context_menu(self, position):
        """Show custom context menu on right-click"""
        global_pos = self.terminal_display.mapToGlobal(position)
        self._show_terminal_menu(global_pos)
    

    def _show_terminal_menu(self, global_position):
        """Show terminal settings menu at specified position"""
        context_menu = QMenu(self)
        
        # Standard text operations
        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.terminal_display.selectAll)
        context_menu.addAction(select_all_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setEnabled(self.terminal_display.textCursor().hasSelection())
        copy_action.triggered.connect(self.terminal_display.copy)
        context_menu.addAction(copy_action)
        
        context_menu.addSeparator()
        
        # Font size controls
        font_menu = context_menu.addMenu("Font Size")
        
        increase_font_action = QAction("Increase Font Size", self)
        increase_font_action.setShortcut("Ctrl++")
        increase_font_action.triggered.connect(self.increase_font_size)
        font_menu.addAction(increase_font_action)
        
        decrease_font_action = QAction("Decrease Font Size", self)
        decrease_font_action.setShortcut("Ctrl+-")
        decrease_font_action.triggered.connect(self.decrease_font_size)
        font_menu.addAction(decrease_font_action)
        
        font_menu.addSeparator()
        
        reset_font_action = QAction("Reset Font Size", self)
        reset_font_action.triggered.connect(self.reset_font_size)
        font_menu.addAction(reset_font_action)
        
        context_menu.addSeparator()
        
        # Terminal-specific options
        auto_scroll_action = QAction("Auto-scroll", self)
        auto_scroll_action.setIcon(self.checkbox_icon(self.formatter.is_auto_scroll_enabled()))
        auto_scroll_action.triggered.connect(self.toggle_auto_scroll)
        context_menu.addAction(auto_scroll_action)
        
        word_wrap_action = QAction("Word Wrap", self)
        word_wrap_action.setIcon(self.checkbox_icon(self.word_wrap_enabled))
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        context_menu.addAction(word_wrap_action)
        
        context_menu.addSeparator()
        
        # Display mode toggle
        hex_mode_action = QAction("Hex Display Mode", self)
        hex_mode_action.setIcon(self.checkbox_icon(self.hex_display_mode))
        hex_mode_action.triggered.connect(self.toggle_hex_mode)
        context_menu.addAction(hex_mode_action)
        
        context_menu.addSeparator()
        
        # Scroll to bottom action
        scroll_to_bottom_action = QAction("Scroll to Bottom", self)
        scroll_to_bottom_action.triggered.connect(self.scroll_to_bottom)
        context_menu.addAction(scroll_to_bottom_action)
        
        # Clear terminal
        clear_action = QAction("Clear Terminal", self)
        clear_action.triggered.connect(self.clear_terminal)
        context_menu.addAction(clear_action)
        
        # Show the context menu at the specified position
        context_menu.exec(global_position)
    
    def _update_terminal_display_style(self):
        """Update terminal display style with current settings"""
        font = QFont(AppFonts.CONSOLE_FAMILY, self.current_font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.terminal_display.setFont(font)
        
        # Update stylesheet
        wrap_mode = "word-wrap" if self.word_wrap_enabled else "nowrap"
        self.terminal_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
                border: none;
                selection-background-color: {AppColors.SELECTION_BG};
                selection-color: {AppColors.SELECTION_TEXT};
                white-space: {wrap_mode};
            }}
        """)
        
        if self.word_wrap_enabled:
            self.terminal_display.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.terminal_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    
    def toggle_auto_scroll(self):
        """Toggle auto-scroll on/off"""
        self.auto_scroll_enabled = not self.auto_scroll_enabled
        self.formatter.set_auto_scroll_enabled(self.auto_scroll_enabled)
        
        if self.auto_scroll_enabled:
            self.formatter.force_scroll_to_bottom(self.terminal_display)
    
    def toggle_hex_mode(self):
        """Toggle hex display mode"""
        self.hex_display_mode = not self.hex_display_mode
        
        if self.hex_display_mode:
            self.formatter.append_status(
                self.terminal_display,
                "Hex display mode enabled",
                "status"
            )
        else:
            self.formatter.append_status(
                self.terminal_display,
                "Hex display mode disabled",
                "status"
            )
    
    def increase_font_size(self):
        """Increase terminal font size"""
        if self.current_font_size < 24:
            self.current_font_size += 1
            self._update_terminal_display_style()
    
    def decrease_font_size(self):
        """Decrease terminal font size"""
        if self.current_font_size > 8:
            self.current_font_size -= 1
            self._update_terminal_display_style()
    
    def reset_font_size(self):
        """Reset font size to default"""
        self.current_font_size = AppFonts.FONT_SIZE_LARGE
        self._update_terminal_display_style()
    
    def toggle_word_wrap(self):
        """Toggle word wrap on/off"""
        self.word_wrap_enabled = not self.word_wrap_enabled
        self._update_terminal_display_style()
    
    def scroll_to_bottom(self):
        """Manually scroll to bottom"""
        self.formatter.force_scroll_to_bottom(self.terminal_display)