#!/usr/bin/env python3
"""
Terminal Stream Widget - Real-time serial data display
Provides a simple terminal window for logging incoming serial data
"""

from typing import Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QTextCursor

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
        self.data_buffer = []  # Buffer for incoming data
        self.buffer_timer = QTimer()
        self.buffer_timer.setSingleShot(True)
        self.buffer_timer.timeout.connect(self._flush_buffer)
        
        self.init_ui()
        
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
        self.terminal_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppColors.BACKGROUND_WHITE};
                color: {AppColors.TEXT_DEFAULT};
                border: none;
                font-family: {AppFonts.CONSOLE_FAMILY};
                font-size: {AppFonts.FONT_SIZE_LARGE};
                selection-background-color: {AppColors.SELECTION_BG};
                selection-color: {AppColors.SELECTION_TEXT};
            }}
        """)
        self.terminal_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.terminal_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
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
    
    def set_current_port(self, port_name: str, port_info: Optional[SerialPortInfo] = None):
        """Set the current port for terminal monitoring"""
        self.current_port = port_info
        
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
            
            self.port_label.setText(display_text)
            self.header_widget.setVisible(True)
            self.separator.setVisible(True)
            
            # Show/hide monitor controls based on port type
            can_monitor = (port_info and (port_info.port_type == "Physical" or 
                          port_info.port_type.startswith("Virtual")))
            
            self.monitor_btn.setVisible(can_monitor)
            
            if not can_monitor:
                self.stop_monitoring()
        else:
            self.hide_all()
    
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
        
        # Create new monitor
        self.port_monitor = SerialPortMonitor(self.current_port.port_name, 9600)
        self.port_monitor.data_received.connect(self._handle_incoming_data)
        self.port_monitor.stats_updated.connect(self._handle_stats_update)
        self.port_monitor.error_occurred.connect(self._handle_monitoring_error)
        
        if self.port_monitor.start_monitoring():
            self._update_monitor_button_icon(True)
            self._apply_status_style("monitoring")
            
            # Add connection start message
            self.formatter.format_connection_start(
                self.terminal_display, 
                self.current_port.port_name, 
                9600
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
        
        # If monitoring, add a clear separator
        if self.port_monitor and self.port_monitor.monitoring:
            self.formatter.append_separator(self.terminal_display, "TERMINAL CLEARED")
    
    def _handle_incoming_data(self, data: bytes):
        """Handle incoming serial data"""
        try:
            # Convert bytes to string, handling common encodings
            text_data = data.decode('utf-8', errors='replace')
            
            # Add to buffer for batched processing
            self.data_buffer.append(text_data)
            
            # Start/restart buffer timer for smooth display
            if not self.buffer_timer.isActive():
                self.buffer_timer.start(50)  # 50ms delay for batching
                
        except Exception as e:
            # Handle decoding errors
            self.formatter.append_status(
                self.terminal_display,
                f"Data decode error: {str(e)}",
                "error"
            )
    
    def _flush_buffer(self):
        """Flush the data buffer to terminal display"""
        if self.data_buffer:
            # Combine all buffered data
            combined_data = ''.join(self.data_buffer)
            self.data_buffer.clear()
            
            # Add to terminal display
            self.formatter.append_data(
                self.terminal_display,
                combined_data,
                "incoming",
                show_timestamp=True
            )
    
    def _handle_stats_update(self, stats):
        """Handle monitoring statistics update (optional for terminal)"""
        # Terminal widget doesn't need to display stats,
        # but we keep this for compatibility with SerialPortMonitor
        pass
    
    def _handle_monitoring_error(self, error_msg):
        """Handle monitoring errors"""
        self.formatter.append_status(
            self.terminal_display,
            f"Monitoring error: {error_msg}",
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