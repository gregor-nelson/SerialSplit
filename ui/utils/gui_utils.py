#!/usr/bin/env python3
"""
GUI utility classes extracted from gui.py
Contains helper classes for GUI operations
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Callable, Any, Tuple
from PyQt6.QtWidgets import (QStyledItemDelegate, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QStyle)
from PyQt6.QtCore import Qt, QRect, QRectF, QByteArray
from PyQt6.QtGui import QFont, QColor, QFontMetrics
from PyQt6.QtSvg import QSvgRenderer

from ui.theme.theme import AppFonts, AppColors, AppDimensions
from ui.theme.icons.icons import AppIcons
from core.core import PortConfig


class FeatureIconDelegate(QStyledItemDelegate):
    """Custom delegate to render SVG icons inline with feature text"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        """Custom paint method to render SVG icons inline"""
        # Get the text
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text or "Features:" not in text:
            # Use default painting for items without features
            super().paint(painter, option, index)
            return
        
        # Split text to find features section
        parts = text.split("[Features: ")
        if len(parts) < 2:
            super().paint(painter, option, index)
            return
        
        main_text = parts[0]
        features_text = parts[1].rstrip("]")
        
        # Set up font and metrics
        font = QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL)
        painter.setFont(font)
        fm = QFontMetrics(font)
        
        # Draw background if selected
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(QColor(AppColors.TEXT_DEFAULT))
        
        # Draw main text
        main_rect = QRect(option.rect.x() + 4, option.rect.y(), 
                         option.rect.width() - 8, option.rect.height())
        main_width = fm.horizontalAdvance(main_text + "[Features: ")
        painter.drawText(main_rect, Qt.AlignmentFlag.AlignVCenter, main_text + "[Features: ")
        
        # Draw features with custom SVG icons
        features_x = option.rect.x() + main_width + 4
        features_y = option.rect.y()
        icon_size = 16
        icon_gap = 6
        
        # Replace bullet points with actual SVG icons
        current_x = features_x
        for feature in features_text.split(", "):
            if "●" in feature:
                # Extract feature name and determine icon
                feature_name = feature.replace("● ", "").strip()
                icon_key, color = self._get_icon_for_feature(feature_name)
                
                if icon_key:
                    # Draw SVG icon
                    svg_template = getattr(AppIcons, icon_key)
                    colored_svg = svg_template.replace(AppIcons._COLORS['PRIMARY_BLUE'], color)
                    
                    # Render SVG
                    svg_bytes = QByteArray(colored_svg.encode('utf-8'))
                    renderer = QSvgRenderer(svg_bytes)
                    
                    icon_rect = QRectF(current_x, features_y + (option.rect.height() - icon_size) // 2, 
                                      icon_size, icon_size)
                    renderer.render(painter, icon_rect)
                    
                    current_x += icon_size + icon_gap
                
                # Draw feature name
                if option.state & QStyle.StateFlag.State_Selected:
                    painter.setPen(option.palette.highlightedText().color())
                else:
                    painter.setPen(QColor(color))
                painter.drawText(current_x, features_y + option.rect.height() // 2 + fm.height() // 4, 
                               feature_name)
                current_x += fm.horizontalAdvance(feature_name) + 12
        
        # Draw closing bracket
        painter.setPen(QColor(AppColors.TEXT_DEFAULT))
        painter.drawText(current_x, features_y + option.rect.height() // 2 + fm.height() // 4, "]")
    
    def _get_icon_for_feature(self, feature_name):
        """Get icon and color for feature name"""
        feature_map = {
            "Baud Rate Timing": ("TIMING_CLOCK", AppColors.TEXT_PRIMARY),
            "Buffer Overrun": ("BUFFER_STACK", AppColors.TEXT_PRIMARY),
            "Exclusive Mode": ("EXCLUSIVE_LOCK", AppColors.TEXT_PRIMARY),
            "Plug-In Mode": ("PLUGIN_CONNECTOR", AppColors.TEXT_PRIMARY)
        }
        return feature_map.get(feature_name, (None, AppColors.TEXT_DEFAULT))


class Config:
    """Application configuration constants"""
    BAUD_RATES = ["1200", "2400", "4800", "9600", "14400", "19200", 
                  "38400", "57600", "115200", "230400", "460800", "921600"]
    QUICK_BAUD_RATES = ["9600", "19200", "38400", "57600", "115200"]
    DEFAULT_BAUD = "115200"
    MIN_OUTPUT_PORTS = 1


class OperationType(Enum):
    """Operation types for generic handlers"""
    CREATE_PAIR = "create"
    REMOVE_PAIR = "remove"
    MODIFY_PAIR = "modify"
    LIST_PAIRS = "list"
    

@dataclass
class ButtonConfig:
    """Configuration for button creation"""
    icon_name: str
    callback: Callable
    tooltip: str
    enabled: bool = True
    reference_name: Optional[str] = None


class ThreadRegistry:
    """Manages all application threads"""
    def __init__(self):
        self.threads = {}
        
    def register(self, name: str, thread):
        """Register a thread with a unique name"""
        self.threads[name] = thread
        
    def unregister(self, name: str):
        """Unregister a thread"""
        if name in self.threads:
            del self.threads[name]
            
    def stop_all(self, timeout: int = 1000) -> List[str]:
        """Stop all threads safely and return list of threads that didn't stop"""
        failed = []
        for name, thread in self.threads.items():
            if thread and thread.isRunning():
                thread.quit()  # Request graceful shutdown first
                if not thread.wait(timeout):
                    failed.append(name)
                    thread.terminate()  # Only as last resort
        self.threads.clear()
        return failed


class PortManager:
    """Manages port-related operations"""
    @staticmethod
    def format_port_name(port: str) -> Optional[str]:
        """Format port name for hub4com"""
        port = port.upper().strip()
        
        if "No COM" in port:
            return None
        
        if port.startswith(('COM', 'CNC')):
            return f"\\\\.\\{port}"
        elif port.startswith('\\\\.\\'):
            return port
        elif port.isdigit():
            return f"\\\\.\\COM{port}"
        else:
            return f"\\\\.\\{port}"
    
    @staticmethod
    def extract_port_info(text: str) -> Tuple[str, str]:
        """Extract port names from list item text"""
        if "[CNCA" in text and "CNCB" in text:
            bracket_content = text.split("[")[1].split("]")[0]
            parts = bracket_content.split(" ↔ ")
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return "", ""


@dataclass
class ControlPanelColumn:
    """Configuration for a control panel column"""
    title: str
    buttons: List[ButtonConfig]
    width_hint: int = 100  # Minimum width hint
    

@dataclass
class StatusIndicator:
    """Configuration for status indicators"""
    key: str
    initial_text: str
    

class ControlPanelBuilder:
    """Builds clean, robust column-based control panels"""
    
    def __init__(self, parent):
        self.parent = parent
        
    def create_control_panel(self, columns: List[ControlPanelColumn], 
                           status_indicators: List[StatusIndicator] = None) -> QWidget:
        """Create a professional column-based control panel"""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.CONTROL_PANEL_BACKGROUND};
                border-bottom: 1px solid {AppColors.CONTROL_PANEL_BORDER};
            }}
        """)
        
        layout = QHBoxLayout(panel)
        layout.setSpacing(16)  # Increased spacing between columns
        layout.setContentsMargins(*AppDimensions.MARGIN_SMALL)  # Use theme margins
        
        # Add columns
        for i, column in enumerate(columns):
            column_widget = self._create_column(column)
            layout.addWidget(column_widget)
            
            # Add separator between columns (except after last column)
            if i < len(columns) - 1:
                separator = self._create_column_separator()
                layout.addWidget(separator)
        
        # Add stretch before status indicators
        layout.addStretch()
        
        # Add status indicators
        if status_indicators:
            status_widget = self._create_status_section(status_indicators)
            layout.addWidget(status_widget)
        
        panel.setFixedHeight(AppDimensions.HEIGHT_CONTROL_BAR)  # Use theme height
        return panel
    
    def _create_column(self, column: ControlPanelColumn) -> QWidget:
        """Create a single column with title and buttons"""
        widget = QWidget()
        widget.setFixedWidth(column.width_hint)  # Use fixed width for consistency
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)  # Compact spacing between title and buttons
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Column title
        title_label = QLabel(column.title)
        title_label.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL, QFont.Weight.Bold))  # Use theme font size
        title_label.setStyleSheet(f"QLabel {{ color: {AppColors.CONTROL_PANEL_TEXT}; padding: {AppDimensions.PADDING_COMPACT}; }}")  # Use theme padding
        layout.addWidget(title_label)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)  # Compact spacing between buttons
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Apply alignment based on button count for visual consistency
        if len(column.buttons) == 2:
            # Left-align 2-button sections to match visual flow
            pass  # No leading stretch
        else:
            # Center-align 3+ button sections
            button_layout.addStretch()
        
        # Create buttons using parent's button creation method
        button_refs = self.parent._create_icon_button_group(column.buttons, button_layout)
        
        # Update parent's UI references
        self.parent.ui_refs.update(button_refs)
        
        # Add trailing stretch for both cases
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_column_separator(self) -> QFrame:
        """Create a vertical separator between columns"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet(f"QFrame {{ color: {AppColors.CONTROL_PANEL_SEPARATOR}; margin: 2px 0px; }}")
        separator.setMaximumHeight(55)  # Increased to match new panel height
        return separator
    
    def _create_status_section(self, indicators: List[StatusIndicator]) -> QWidget:
        """Create status indicators section with fixed width to prevent jitter"""
        if len(indicators) == 1:
            # Single status indicator with fixed width to prevent layout jitter
            status_label = QLabel(indicators[0].initial_text)
            status_label.setFont(QFont(AppFonts.DEFAULT_FAMILY, 8))  # Use SMALL_SIZE
            status_label.setStyleSheet(f"QLabel {{ color: {AppColors.CONTROL_PANEL_STATUS_TEXT}; padding: 4px 8px; font-style: italic; }}")
            status_label.setMinimumWidth(200)  # Reserve space for longer status messages
            self.parent.ui_refs[indicators[0].key] = status_label
            return status_label
        else:
            # Multiple status indicators in vertical layout
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setSpacing(1)
            layout.setContentsMargins(0, 0, 0, 0)
            
            for indicator in indicators:
                label = QLabel(indicator.initial_text)
                label.setFont(QFont(AppFonts.DEFAULT_FAMILY, 8))  # Use SMALL_SIZE
                label.setStyleSheet(f"QLabel {{ color: {AppColors.CONTROL_PANEL_STATUS_TEXT}; padding: 2px 8px; font-style: italic; }}")
                label.setMinimumWidth(200)  # Reserve space for longer status messages
                layout.addWidget(label)
                self.parent.ui_refs[indicator.key] = label
            
            return widget


class CommandBuilder:
    """Builds hub4com commands"""
    def __init__(self):
        self.port_manager = PortManager()
        
    def build(self, incoming_port: str, incoming_baud: str, 
              output_configs: List[PortConfig], route_settings: Dict,
              disable_cts: bool) -> Optional[List[str]]:
        """Build the complete hub4com command"""
        cmd = ["hub4com.exe"]
        
        if not incoming_port or "No COM" in incoming_port:
            return None
            
        if not output_configs:
            return None
            
        # Add route options
        self._add_route_options(cmd, len(output_configs), route_settings)
        
        # Add CTS option
        if disable_cts:
            cmd.append('--octs=off')
            
        # Add incoming port
        cmd.append(f'--baud={incoming_baud}')
        formatted_incoming = self.port_manager.format_port_name(incoming_port)
        if not formatted_incoming:
            return None
        cmd.append(formatted_incoming)
        
        # Add output ports
        for config in output_configs:
            cmd.append(f'--baud={config.baud_rate}')
            formatted_port = self.port_manager.format_port_name(config.port_name)
            if not formatted_port:
                return None
            cmd.append(formatted_port)
            
        return cmd
        
    def _add_route_options(self, cmd: List[str], num_ports: int, settings: Dict):
        """Add route options to command"""
        output_indices = ','.join(str(i + 1) for i in range(num_ports))
        
        mode = settings.get('mode', 'two_way')
        if mode == 'one_way':
            cmd.append(f'--route=0:{output_indices}')
        elif mode == 'two_way':
            cmd.append(f'--bi-route=0:{output_indices}')
        elif mode == 'full_network':
            cmd.append('--route=All:All')
            
        if settings.get('echo_enabled'):
            cmd.append('--echo-route=0')
        if settings.get('flow_control_enabled'):
            cmd.append(f'--fc-route=0:{output_indices}')
        if settings.get('disable_default_fc'):
            cmd.append(f'--no-default-fc-route=0:{output_indices}')