#!/usr/bin/env python3
"""
Main GUI window for Hub4com GUI Launcher
Contains the primary application interface - Optimized version
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Callable, Any, Tuple
from functools import partial
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QComboBox, QPushButton, QCheckBox, 
                             QTextEdit, QFileDialog, QGroupBox, QGridLayout,
                             QMessageBox, QProgressBar, QFrame, QSplitter,
                             QTabWidget, QScrollArea, QListWidget, QListWidgetItem, 
                             QAbstractItemView, QMenu, QDialog, QSizePolicy)
from PyQt6.QtCore import QTimer, Qt, QSize, QByteArray
from PyQt6.QtGui import QFont, QIcon, QColor, QAction, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

from core.core import (
    ResponsiveWindowManager, SerialPortInfo, PortScanner, Hub4comProcess,
    WINREG_AVAILABLE, PortConfig, Com0comProcess, DefaultConfig
)
from ui.theme.theme import (
    ThemeManager, AppStyles, AppFonts, AppDimensions, AppColors, 
    AppMessages, IconManager
)
from ui.dialogs import PortScanDialog, PairCreationDialog, ConfigurationSummaryDialog, LaunchDialog
from ui.dialogs.help_dialog import HelpManager, HelpTopic
from ui.widgets import OutputPortWidget
from ui.widgets.tab_manager_widget import SerialPortManagerWidget
from ui.windows.command_formatter import CommandFormatter
from ui.windows.output_formatter import OutputLogFormatter



class Config:
    """Application configuration constants"""
    BAUD_RATES = ["1200", "2400", "4800", "9600", "14400", "19200", 
                  "38400", "57600", "115200", "230400", "460800", "921600"]
    QUICK_BAUD_RATES = ["9600", "19200", "38400", "57600", "115200"]
    DEFAULT_BAUD = "115200"
    MIN_OUTPUT_PORTS = 1

# ============================================================================
# INTERNAL HELPER CLASSES
# ============================================================================

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
        """Stop all threads and return list of threads that didn't stop"""
        failed = []
        for name, thread in self.threads.items():
            if thread and thread.isRunning():
                thread.terminate()
                if not thread.wait(timeout):
                    failed.append(name)
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
        panel.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                border-bottom: 1px solid #d0d0d0;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setSpacing(16)  # Increased spacing between columns
        layout.setContentsMargins(2, 2, 2, 2)  # Reduced margins for control panels
        
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
        
        panel.setFixedHeight(65)  # Significantly increased height for full visibility
        return panel
    
    def _create_column(self, column: ControlPanelColumn) -> QWidget:
        """Create a single column with title and buttons"""
        widget = QWidget()
        widget.setMinimumWidth(column.width_hint)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)  # Compact spacing between title and buttons
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Column title
        title_label = QLabel(column.title)
        title_label.setFont(QFont(AppFonts.DEFAULT_FAMILY, 8, QFont.Weight.Bold))  # Use SMALL_SIZE from theme
        title_label.setStyleSheet("QLabel { color: #333333; padding: 2px 0px; }")  # Minimal padding for compact headers
        layout.addWidget(title_label)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)  # Compact spacing between buttons
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create buttons using parent's button creation method
        button_refs = self.parent._create_icon_button_group(column.buttons, button_layout)
        
        # Update parent's UI references
        self.parent.ui_refs.update(button_refs)
        
        # Add stretch to left-align buttons
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_column_separator(self) -> QFrame:
        """Create a vertical separator between columns"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("QFrame { color: #d0d0d0; margin: 2px 0px; }")
        separator.setMaximumHeight(55)  # Increased to match new panel height
        return separator
    
    def _create_status_section(self, indicators: List[StatusIndicator]) -> QWidget:
        """Create status indicators section"""
        if len(indicators) == 1:
            # Single status indicator
            status_label = QLabel(indicators[0].initial_text)
            status_label.setFont(QFont(AppFonts.DEFAULT_FAMILY, 8))  # Use SMALL_SIZE
            status_label.setStyleSheet("QLabel { color: #666666; padding: 4px 8px; font-style: italic; }")  # Compact padding
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
                label.setStyleSheet("QLabel { color: #666666; padding: 2px 8px; font-style: italic; }")  # Compact padding
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
        
        mode = settings.get('mode', 'one_way')
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


# ============================================================================
# MAIN GUI CLASS
# ============================================================================

class Hub4comGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Core components
        self.thread_registry = ThreadRegistry()
        self.port_manager = PortManager()
        self.command_builder = CommandBuilder()
        self.command_formatter = CommandFormatter()
        self.output_log_formatter = OutputLogFormatter()
        self.control_panel_builder = ControlPanelBuilder(self)
        
        # State management
        self.app_state = {
            'hub4com_process': None,
            'scanned_ports': [],
            'output_port_widgets': [],
            'route_settings': {
                'mode': 'two_way',
                'echo_enabled': False,
                'flow_control_enabled': False,
                'disable_default_fc': False
            },
            'pending_modifications': 0,
            'modification_success': True
        }
        
        # UI references dictionary for easy access
        self.ui_refs = {}
        
        # Initialize window
        self.window_config = ResponsiveWindowManager.calculate_main_window_config()
        self._init_ui()
        self._setup_timers()
    
    # ========================================================================
    # UI INITIALIZATION
    # ========================================================================
    
    def _init_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle("Serial Port Splitter - COM0COM/HUB4COM")
        self._setup_window()
        
        # Create main layout
        central_widget = self._create_central_widget()
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        margins = ThemeManager.get_standard_margins()
        layout.setContentsMargins(*margins)
        
        # Main vertical splitter for all sections
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(self._create_virtual_ports_section())
        main_splitter.addWidget(self._create_configuration_section())
        main_splitter.addWidget(self._create_output_section())
        main_splitter.setSizes([200, 400, 400])  # Virtual:21.7%, Config:43.3%, Output:35%
        main_splitter.setStretchFactor(0, 1)   # Virtual ports (smallest)
        main_splitter.setStretchFactor(1, 2)  # Configuration (largest) 
        main_splitter.setStretchFactor(2, 2)   # Output (middle)
        layout.addWidget(main_splitter)
        
    def _setup_window(self):
        """Configure window geometry"""
        self.setGeometry(
            self.window_config.x, 
            self.window_config.y, 
            self.window_config.width, 
            self.window_config.height
        )
        self.setMinimumSize(QSize(self.window_config.min_width, self.window_config.min_height))
    
    def _create_central_widget(self):
        """Create scrollable central widget"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(AppStyles.scroll_area())
        
        central_widget = QWidget()
        central_widget.setStyleSheet(f"QWidget {{ background-color: {AppColors.BACKGROUND_LIGHT}; }}")
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)
        
        return central_widget
    
    def _setup_timers(self):
        """Setup initial timers"""
        timers = [
            (100, self.update_preview),
            (500, self.initialize_default_configuration),
            (1000, self._safe_refresh_ports),
            (1500, self.add_output_port),
            (2000, self.list_com0com_pairs)
        ]
        
        for delay, callback in timers:
            QTimer.singleShot(delay, callback)
    
    # ========================================================================
    # UI HELPER METHODS
    # ========================================================================
    
    def _create_groupbox_with_layout(self, title: str, layout_class=QVBoxLayout) -> tuple:
        """Create a styled groupbox with layout optimized for control panels"""
        group = ThemeManager.create_groupbox(title)
        
        # Override GroupBox styling to prevent control panel clipping
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: normal;
                color: {AppColors.TEXT_DEFAULT};
                border: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {AppColors.BORDER_DEFAULT};
                margin-top: 12px;  /* Reduced from 8px */
                padding-top: 2px;  /* Minimal padding - reduced from 6px */
                background-color: {AppColors.BACKGROUND_LIGHT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {AppDimensions.SPACING_LARGE}px;
                padding: 0 {AppDimensions.SPACING_SMALL}px;
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
            }}
        """)
        
        layout = layout_class(group) if layout_class else None
        if layout:
            layout.setSpacing(AppDimensions.SPACING_MEDIUM)
            layout.setContentsMargins(8, 4, 8, 8)  # Minimal top margin
        return group, layout
    
    def _create_icon_button_group(self, buttons: List[ButtonConfig], 
                                  layout: QHBoxLayout) -> Dict[str, QPushButton]:
        """Create a group of Windows Explorer style compact buttons with SVG icons"""
        created_buttons = {}
        
        # Icon mapping to SVG names
        icon_svg_map = {
            "refresh": "REFRESH",
            "create": "CREATE", 
            "delete": "DELETE",
            "settings": "SETTINGS",
            "help": "HELP",
            "list": "SEARCH",  # Use search icon for port scanning
            "play": "PLAY",
            "stop": "STOP",
            "port": "PORT",
            "configure": "CONFIGURE"
        }
        
        # Button text mapping
        button_text_map = {
            "refresh": "Refresh",
            "create": "New",
            "delete": "Delete",
            "settings": "Settings",
            "help": "Help",
            "list": "Scan",
            "play": "Start",
            "stop": "Stop",
            "port": "Ports",
            "configure": "Configure"
        }
        
        for config in buttons:
            # Create base button with Windows Explorer styling
            btn = QPushButton()
            btn.setMinimumWidth(90)  # Further increased
            btn.setMaximumWidth(120)  # Further increased 
            btn.setMinimumHeight(32)  # Much taller buttons
            btn.setMaximumHeight(32)  # Much taller buttons
            btn.setFont(QFont(AppFonts.DEFAULT_FAMILY, 8))  # Use SMALL_SIZE for compact appearance
            
            # Set button text
            button_text = button_text_map.get(config.icon_name, config.icon_name.title())
            btn.setText(button_text)
            btn.setToolTip(config.tooltip)
            
            # Add SVG icon if available using the ThemeManager system
            svg_name = icon_svg_map.get(config.icon_name)
            if svg_name:
                try:
                    # Use the IconManager directly to create the icon
                    from ui.theme.icons.icons import AppIcons
                    icon_template = getattr(AppIcons, svg_name, None)
                    if icon_template:
                        icon_size = QSize(16, 16)
                        icon = IconManager.create_svg_icon(icon_template, AppColors.ICON_DEFAULT, icon_size)
                        btn.setIcon(icon)
                        btn.setIconSize(icon_size)
                except Exception as e:
                    print(f"Warning: Could not load icon {svg_name}: {e}")
            
            # Apply Windows Explorer button styling - subtle and compact
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid transparent;
                    padding: 4px 10px 4px 26px;  /* More generous padding */
                    text-align: left;
                    font-family: "Segoe UI";
                    font-size: 8pt;  /* Match button font */
                    color: #333333;
                    line-height: 1.2;
                }
                QPushButton:hover {
                    background-color: #e5f3ff;
                    border-color: #cce4f7;
                }
                QPushButton:pressed {
                    background-color: #cce4f7;
                    border-color: #9ac9e3;
                }
                QPushButton:disabled {
                    background-color: transparent;
                    color: #999999;
                    border-color: transparent;
                }
            """)
            
            # Special styling for primary actions
            if config.icon_name in ["play", "create"]:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e5f3ff;
                        border: 1px solid #cce4f7;
                        padding: 4px 10px 4px 26px;  /* More generous padding */
                        text-align: left;
                        font-family: "Segoe UI";
                        font-size: 8pt;  /* Match button font */
                        color: #0078d4;
                        font-weight: normal;
                        line-height: 1.2;
                    }
                    QPushButton:hover {
                        background-color: #d0e7ff;
                        border-color: #9ac9e3;
                    }
                    QPushButton:pressed {
                        background-color: #bde0ff;
                        border-color: #7bb8dd;
                    }
                    QPushButton:disabled {
                        background-color: #f5f5f5;
                        color: #999999;
                        border-color: #d0d0d0;
                    }
                """)
            
            btn.clicked.connect(config.callback)
            btn.setEnabled(config.enabled)
            layout.addWidget(btn)
            
            if config.reference_name:
                created_buttons[config.reference_name] = btn
                
        return created_buttons
    
    def checkbox_icon(self, checked: bool) -> QIcon:
        """Generate Windows 10 style checkbox icon"""
        if checked:
            svg = '''<svg width="16" height="16" xmlns="http://www.w3.org/2000/svg">
                <rect x="0.5" y="0.5" width="15" height="15" fill="white" stroke="#999" stroke-width="1"/>
                <rect x="2" y="2" width="12" height="12" fill="#0078D4"/>
                <path d="M4 8l2 2 6-6" stroke="white" stroke-width="1" fill="none" stroke-linecap="round"/>
            </svg>'''
        else:
            svg = '''<svg width="16" height="16" xmlns="http://www.w3.org/2000/svg">
                <rect x="0.5" y="0.5" width="15" height="15" fill="white" stroke="#999" stroke-width="1"/>
            </svg>'''
        
        renderer = QSvgRenderer(QByteArray(svg.encode()))
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)

    def _add_separator(self, layout: QVBoxLayout, orientation: str = "horizontal"):
        """Add a themed separator to layout"""
        separator = ThemeManager.create_separator(orientation)
        layout.addWidget(separator)
    
    def _show_message(self, title: str, message: str, msg_type: str = "info"):
        """Show message box with specified type"""
        msg_funcs = {
            "info": QMessageBox.information,
            "warning": QMessageBox.warning,
            "error": QMessageBox.critical,
            "question": QMessageBox.question
        }
        return msg_funcs.get(msg_type, QMessageBox.information)(self, title, message)
    
    def _update_status(self, message: str, widget: QLabel = None, component: str = None):
        """Update status label - unified status management"""
        if not widget:
            widget = self.ui_refs.get(f'{component}_status') if component else None
            if not widget:
                widget = self.ui_refs.get('status_label')
        
        if widget:
            widget.setText(message)
    
    # ========================================================================
    # UI SECTION BUILDERS
    # ========================================================================
    
    def _create_virtual_ports_section(self) -> QGroupBox:
        """Create virtual ports management section with clean column-based layout"""
        group, layout = self._create_groupbox_with_layout("Com0com Configuration")
        
        
        # Define control panel structure
        columns = [
            ControlPanelColumn(
                title="Port Management",
                buttons=[
                    ButtonConfig("refresh", self.list_com0com_pairs, "Refresh port pairs list", True),
                    ButtonConfig("create", self.create_com0com_pair, "Create new virtual port pair", True)
                ],
                width_hint=160  # Increased width
            ),
            ControlPanelColumn(
                title="Pair Configuration",
                buttons=[
                    ButtonConfig("delete", self.remove_com0com_pair, "Delete selected pair", False, "remove_pair_btn"),
                    ButtonConfig("settings", self.show_settings_menu, "Configure selected pair", False, "settings_btn"),
                    ButtonConfig("help", lambda: self._show_help(HelpTopic.COM0COM_SETTINGS), "Help and documentation", True)
                ],
                width_hint=180  # Increased width
            )
        ]
        
        # Define status indicators
        status_indicators = [
            StatusIndicator("com0com_status", AppMessages.READY)
        ]
        
        # Create control panel using the builder
        control_panel = self.control_panel_builder.create_control_panel(columns, status_indicators)
        layout.addWidget(control_panel)
        
        # Port pairs list
        self.ui_refs['port_pairs_list'] = ThemeManager.create_listwidget()
        self.ui_refs['port_pairs_list'].itemSelectionChanged.connect(self.on_pair_selected)
        self.ui_refs['port_pairs_list'].itemDoubleClicked.connect(self.on_pair_double_clicked)
        self.ui_refs['port_pairs_list'].setMaximumHeight(AppDimensions.HEIGHT_LIST_MEDIUM)
        
        # Add right-click context menu support
        self.ui_refs['port_pairs_list'].setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui_refs['port_pairs_list'].customContextMenuRequested.connect(self.show_port_pair_context_menu)
        
        layout.addWidget(self.ui_refs['port_pairs_list'])
        
        # Progress bar
        self.ui_refs['com0com_progress'] = ThemeManager.create_progress_bar()
        self.ui_refs['com0com_progress'].setRange(0, 100)
        self.ui_refs['com0com_progress'].setVisible(False)
        layout.addWidget(self.ui_refs['com0com_progress'])
        
        return group
    
    def _create_configuration_section(self) -> QGroupBox:
        """Create hub4com configuration section with clean column-based layout"""
        group, layout = self._create_groupbox_with_layout("Hub4com Configuration", QVBoxLayout)
        
        # Define control panel structure with 3 columns
        columns = [
            ControlPanelColumn(
                title="Port Discovery",
                buttons=[
                    ButtonConfig("list", self.show_port_scanner, "Scan ports for detailed analysis", True),
                    ButtonConfig("refresh", self.refresh_port_lists, "Refresh port lists", True)
                ],
                width_hint=140  # Increased width
            ),
            ControlPanelColumn(
                title="Port Management",
                buttons=[
                    ButtonConfig("create", self.add_output_port, "Add new output port", True),
                    ButtonConfig("delete", self.remove_all_output_ports, "Remove all output ports", True, "remove_all_ports_btn"),
                    ButtonConfig("configure", self.update_preview, "Update command preview", True)
                ],
                width_hint=160  # Increased width
            ),
            ControlPanelColumn(
                title="Hub4com Control",
                buttons=[
                    ButtonConfig("settings", self.show_hub4com_settings_menu, "Hub4com configuration settings", True, "hub4com_settings_btn"),
                    ButtonConfig("play", self.start_hub4com, "Start hub4com routing", True, "start_btn"),
                    ButtonConfig("stop", self.stop_hub4com, "Stop hub4com routing", False, "stop_btn")
                ],
                width_hint=150  # Increased width
            )
        ]
        
        # Define dual status indicators
        status_indicators = [
            StatusIndicator("port_status", AppMessages.SCANNING),
            StatusIndicator("status_label", AppMessages.READY)
        ]
        
        # Create control panel using the builder
        control_panel = self.control_panel_builder.create_control_panel(columns, status_indicators)
        layout.addWidget(control_panel)
        
        # Initialize hidden settings
        self._init_hidden_settings()
        
        # Port configuration with splitter
        ports_splitter = QSplitter(Qt.Orientation.Horizontal)
        ports_splitter.addWidget(self._create_incoming_port_section())
        ports_splitter.addWidget(self._create_outgoing_ports_section())
        ports_splitter.setSizes([400, 400])  # 50/50 split on launch
        ports_splitter.setChildrenCollapsible(False)  # Prevent collapse
        ports_splitter.setStretchFactor(0, 1)  # Incoming: equal scaling
        ports_splitter.setStretchFactor(1, 1)  # Outgoing: equal scaling
        layout.addWidget(ports_splitter)
        
        return group
    
    def _init_hidden_settings(self):
        """Initialize hidden checkbox settings"""
        self.ui_refs['disable_cts'] = ThemeManager.create_checkbox("Disable CTS Handshaking")
        self.ui_refs['disable_cts'].setChecked(True)
        self.ui_refs['disable_cts'].stateChanged.connect(self.update_preview)
        self.ui_refs['disable_cts'].setVisible(False)
        
        self.ui_refs['sync_baud_rates'] = ThemeManager.create_checkbox("Sync Baud Rates")
        self.ui_refs['sync_baud_rates'].setChecked(True)
        self.ui_refs['sync_baud_rates'].stateChanged.connect(self.on_sync_baud_rates_changed)
        self.ui_refs['sync_baud_rates'].setVisible(False)
    
    def _create_incoming_port_section(self) -> QGroupBox:
        """Create incoming port configuration"""
        group, layout = self._create_groupbox_with_layout("Incoming Port")
        
        self.ui_refs['incoming_port'] = ThemeManager.create_combobox(editable=True)
        self.ui_refs['incoming_port'].currentTextChanged.connect(self.update_preview)
        self.ui_refs['incoming_port'].currentTextChanged.connect(self.update_port_type_indicator)
        self.ui_refs['incoming_port'].setFixedHeight(AppDimensions.COMBOBOX_HEIGHT)
        layout.addWidget(self.ui_refs['incoming_port'])
        
        layout.addWidget(ThemeManager.create_label("Baud Rate:"))
        
        self.ui_refs['incoming_baud'] = ThemeManager.create_combobox()
        self._populate_baud_rates(self.ui_refs['incoming_baud'])
        self.ui_refs['incoming_baud'].currentTextChanged.connect(self.update_preview)
        self.ui_refs['incoming_baud'].currentTextChanged.connect(self.on_incoming_baud_changed)
        self.ui_refs['incoming_baud'].setFixedHeight(AppDimensions.COMBOBOX_HEIGHT)
        layout.addWidget(self.ui_refs['incoming_baud'])
        
        # Port manager widget with monitor and test tabs - allow it to expand
        self.port_manager_widget = SerialPortManagerWidget()
        self.port_manager_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.port_manager_widget, 1)  # Give it stretch factor
        
        return group
    
    def _create_outgoing_ports_section(self) -> QGroupBox:
        """Create outgoing ports configuration - direct layout like incoming port"""
        group, layout = self._create_groupbox_with_layout("Outgoing Ports")
        
        # Store reference to the main layout for direct widget placement
        self.output_ports_layout = layout
        
        return group
    
    def _create_output_section(self) -> QSplitter:
        """Create horizontal two-pane design with command preview and output log"""
        splitter = ThemeManager.create_splitter(Qt.Orientation.Horizontal)
        
        # Command preview
        preview_group, preview_layout = self._create_groupbox_with_layout("Command Preview")
        self.ui_refs['command_preview'] = ThemeManager.create_textedit("console")
        self.ui_refs['command_preview'].setMinimumHeight(AppDimensions.HEIGHT_TEXT_MEDIUM)
        preview_layout.addWidget(self.ui_refs['command_preview'])
        
        # Output log
        output_group, output_layout = self._create_groupbox_with_layout("Output Log")
        self.ui_refs['output_text'] = ThemeManager.create_textedit("console")
        self.ui_refs['output_text'].setMinimumHeight(AppDimensions.HEIGHT_TEXT_MEDIUM)
        output_layout.addWidget(self.ui_refs['output_text'])
        
        splitter.addWidget(preview_group)
        splitter.addWidget(output_group)
        splitter.setSizes([400, 400])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        return splitter
    
    # ========================================================================
    # PORT MANAGEMENT
    # ========================================================================
    
    def _populate_baud_rates(self, combo: QComboBox):
        """Populate combo box with baud rates"""
        for rate in Config.BAUD_RATES:
            combo.addItem(rate, rate)
        combo.setCurrentText(Config.DEFAULT_BAUD)
    
    def add_output_port(self):
        """Add a new output port configuration with consistent spacing"""
        port_number = len(self.app_state['output_port_widgets']) + 1
        available_ports = self.get_available_ports()
        
        widget = OutputPortWidget(port_number, available_ports, self)
        widget.remove_btn.clicked.connect(lambda: self.remove_output_port(widget))
        widget.port_combo.currentTextChanged.connect(self.update_preview)
        widget.baud_combo.currentTextChanged.connect(self.update_preview)
        widget.port_changed.connect(self.update_preview)
        
        self.app_state['output_port_widgets'].append(widget)
        
        # Remove any existing stretch to recalculate layout
        if hasattr(self, '_output_stretch_item'):
            self.output_ports_layout.removeItem(self._output_stretch_item)
        
        # Add widget without stretch factor for consistent spacing
        insert_position = len(self.app_state['output_port_widgets']) - 1
        self.output_ports_layout.insertWidget(insert_position, widget)
        
        # Add stretch at the end to push all widgets to the top
        self._output_stretch_item = self.output_ports_layout.addStretch()
        
        self.renumber_output_ports()
        self.update_preview()
    
    def remove_output_port(self, widget: OutputPortWidget):
        """Remove an output port configuration"""
        if len(self.app_state['output_port_widgets']) > Config.MIN_OUTPUT_PORTS:
            self.app_state['output_port_widgets'].remove(widget)
            self.output_ports_layout.removeWidget(widget)
            widget.deleteLater()
            
            # Remove existing stretch and re-add to maintain consistent layout
            if hasattr(self, '_output_stretch_item'):
                self.output_ports_layout.removeItem(self._output_stretch_item)
            self._output_stretch_item = self.output_ports_layout.addStretch()
            
            self.renumber_output_ports()
            self.update_preview()
        else:
            self._show_message("Cannot Remove", "At least one output port is required.")
    
    def remove_all_output_ports(self):
        """Remove all output ports except the minimum required"""
        if len(self.app_state['output_port_widgets']) <= Config.MIN_OUTPUT_PORTS:
            self._show_message("Cannot Remove All", "At least one output port is required.")
            return
        
        widgets_to_remove = self.app_state['output_port_widgets'][Config.MIN_OUTPUT_PORTS:]
        for widget in widgets_to_remove:
            self.app_state['output_port_widgets'].remove(widget)
            self.output_ports_layout.removeWidget(widget)
            widget.deleteLater()
        
        # Remove existing stretch and re-add to maintain consistent layout
        if hasattr(self, '_output_stretch_item'):
            self.output_ports_layout.removeItem(self._output_stretch_item)
        self._output_stretch_item = self.output_ports_layout.addStretch()
        
        self.renumber_output_ports()
        self.update_preview()
    
    def renumber_output_ports(self):
        """Update port numbers after add/remove"""
        for i, widget in enumerate(self.app_state['output_port_widgets']):
            widget.port_number = i + 1
            widget.findChild(QLabel).setText(f"Port {i + 1}:")
    
    def get_available_ports(self) -> List[str]:
        """Get list of available ports"""
        return [p.port_name for p in self.app_state['scanned_ports']] if self.app_state['scanned_ports'] else []
    
    def set_all_baud_rates(self, rate: str):
        """Set all ports to the same baud rate"""
        self.ui_refs['incoming_baud'].setCurrentText(rate)
        for widget in self.app_state['output_port_widgets']:
            widget.baud_combo.setCurrentText(rate)
        self.update_preview()
    
    def on_sync_baud_rates_changed(self):
        """Handle sync baud rates checkbox change"""
        if self.ui_refs['sync_baud_rates'].isChecked():
            self.set_all_baud_rates(self.ui_refs['incoming_baud'].currentText())
    
    def on_incoming_baud_changed(self):
        """Handle incoming baud rate change"""
        if self.ui_refs['sync_baud_rates'].isChecked():
            self.set_all_baud_rates(self.ui_refs['incoming_baud'].currentText())
    
    # ========================================================================
    # PORT SCANNING
    # ========================================================================
    
    def _safe_refresh_ports(self):
        """Safely refresh port lists with error handling"""
        try:
            self.refresh_port_lists()
        except Exception as e:
            print(f"Error during auto-scan: {e}")
            self._update_status(AppMessages.NO_DEVICES, component='port')
            self._update_port_combos_no_devices()
    
    def show_port_scanner(self):
        """Show the port scanner dialog"""
        dialog = PortScanDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.app_state['scanned_ports'] = dialog.ports
            self.refresh_port_lists()
    
    def refresh_port_lists(self):
        """Refresh all port combo boxes with scanned ports"""
        if self.thread_registry.threads.get('port_scanner'):
            return
        
        try:
            thread = PortScanner()
            thread.scan_completed.connect(self.on_ports_scanned)
            thread.finished.connect(lambda: self.thread_registry.unregister('port_scanner'))
            self.thread_registry.register('port_scanner', thread)
            thread.start()
        except Exception as e:
            print(f"Error starting port scan: {e}")
            self._update_status(AppMessages.NO_DEVICES, component='port')
            self._update_port_combos_no_devices()
    
    def _update_port_combos_no_devices(self):
        """Update port combos when no devices are found"""
        incoming = self.ui_refs['incoming_port']
        incoming.clear()
        incoming.addItem(AppMessages.NO_DEVICES)
        incoming.setEnabled(False)
        
        for widget in self.app_state['output_port_widgets']:
            widget.populate_ports([])
    
    def on_ports_scanned(self, ports):
        """Handle completed port scan for combo boxes"""
        self.app_state['scanned_ports'] = ports
        
        if not ports:
            self._update_status(AppMessages.NO_DEVICES, component='port')
            self._update_port_combos_no_devices()
            return
        
        self._update_status(f"Found {len(ports)} ports", component='port')
        
        # Update incoming port combo
        incoming = self.ui_refs['incoming_port']
        current_incoming = incoming.currentText()
        incoming.clear()
        incoming.setEnabled(True)
        
        for port in ports:
            # Create enhanced display text with status indicator
            display_text = port.port_name
            
            # Add device type and status information
            if port.is_moxa:
                display_text += "  •  Moxa Device"
                if port.device_name and port.device_name != "Unknown":
                    display_text += f"  •  {port.device_name}"
            elif port.port_type.startswith("Virtual"):
                virtual_type = port.port_type.split(' ')[1] if ' ' in port.port_type else "Virtual"
                display_text += f"  •  {virtual_type} Port"
            else:
                display_text += "  •  Hardware Port"
                if port.device_name and port.device_name != "Unknown":
                    display_text += f"  •  {port.device_name}"
            
            incoming.addItem(display_text, port.port_name)
        
        # Restore selection
        index = incoming.findData(current_incoming)
        if index >= 0:
            incoming.setCurrentIndex(index)
        elif incoming.count() > 0:
            incoming.setCurrentIndex(0)
        
        # Update output port widgets
        for widget in self.app_state['output_port_widgets']:
            widget.populate_ports_enhanced(ports)
        
        self.update_port_type_indicator()
    
    def update_port_type_indicator(self):
        """Update the port type indicator using theme messages - now integrated with tab manager"""
        current_port = self.ui_refs['incoming_port'].currentData()
        
        if not current_port:
            # No port selected - hide tab manager
            self.port_manager_widget.hide_all()
            return
        
        port_info = next((p for p in self.app_state['scanned_ports'] if p.port_name == current_port), None)
        if not port_info:
            # Port not found in scanned ports - hide tab manager
            self.port_manager_widget.hide_all()
            return
        
        # Create enhanced display text (same logic as before)
        if port_info.is_moxa:
            enhanced_text = HelpManager.get_tooltip("port_type_moxa")
            style_type = "moxa"
        elif port_info.port_type == "Physical":
            enhanced_text = HelpManager.get_tooltip("port_type_physical")
            style_type = "available"
        else:
            enhanced_text = HelpManager.get_tooltip("port_type_virtual")
            style_type = "virtual"
        
        # Update the tab manager with comprehensive port info
        self.port_manager_widget.update_port_info(port_info, enhanced_text)
        self.port_manager_widget.set_port_type(style_type)
    
    # ========================================================================
    # HUB4COM MANAGEMENT
    # ========================================================================
    
    def build_command(self) -> Optional[List[str]]:
        """Build the hub4com command with baud rate support"""
        incoming = self.ui_refs['incoming_port'].currentData() or self.ui_refs['incoming_port'].currentText()
        incoming_baud = self.ui_refs['incoming_baud'].currentText()
        
        # Get output configs
        output_configs = []
        for widget in self.app_state['output_port_widgets']:
            config = widget.get_config()
            if config.port_name and "No COM" not in config.port_name:
                output_configs.append(config)
        
        return self.command_builder.build(
            incoming, incoming_baud, output_configs,
            self.app_state['route_settings'],
            self.ui_refs['disable_cts'].isChecked()
        )
    
    def update_preview(self):
        """Update the command preview with enhanced formatting"""
        cmd = self.build_command()
        preview = self.ui_refs['command_preview']
        
        if not cmd:
            if not self.app_state['scanned_ports']:
                preview.setPlainText(AppMessages.NO_DEVICES_FULL)
            else:
                preview.setPlainText("Please select valid ports for routing")
            return
        
        # Gather route information
        route_info = self._gather_route_info()
        
        # Use the enhanced formatter
        self.command_formatter.format_command_preview(preview, cmd, route_info)
    
    def _gather_route_info(self) -> Dict:
        """Gather route information for command preview"""
        incoming_display = self.ui_refs['incoming_port'].currentData() or self.ui_refs['incoming_port'].currentText()
        incoming_baud = self.ui_refs['incoming_baud'].currentText()
        
        # Collect output port information
        output_configs = []
        for widget in self.app_state['output_port_widgets']:
            config = widget.get_config()
            if config.port_name and "No COM" not in config.port_name:
                output_configs.append({
                    'port': config.port_name,
                    'baud': config.baud_rate
                })
        
        return {
            'incoming_port': incoming_display,
            'incoming_baud': incoming_baud,
            'outgoing_ports': output_configs,
            'mode': self.app_state['route_settings'].get('mode', 'one_way'),
            'cts_disabled': self.ui_refs['disable_cts'].isChecked(),
            'echo_enabled': self.app_state['route_settings'].get('echo_enabled', False),
            'flow_control_enabled': self.app_state['route_settings'].get('flow_control_enabled', False),
            'disable_default_fc': self.app_state['route_settings'].get('disable_default_fc', False)
        }
    
    def start_hub4com(self):
        """Start the hub4com process"""
        cmd = self.build_command()
        if not cmd:
            if not self.app_state['scanned_ports']:
                self._show_message("No Devices", AppMessages.NO_DEVICES_FULL, "warning")
            else:
                self._show_message("Error", "Please select valid ports for routing", "warning")
            return
        
        # Perform pre-start checks
        if not self._perform_pre_start_checks(cmd):
            return
        
        # Start process
        self.ui_refs['start_btn'].setEnabled(False)
        self.ui_refs['stop_btn'].setEnabled(True)
        
        output_text = self.ui_refs['output_text']
        self.output_log_formatter.clear(output_text)
        self.output_log_formatter.format_section_header(output_text, "Starting Hub4com Process")
        self._update_status(AppMessages.STARTING_HUBCOM)
        
        self.app_state['hub4com_process'] = Hub4comProcess(cmd)
        process = self.app_state['hub4com_process']
        process.output_received.connect(self.on_hub4com_output)
        process.process_started.connect(lambda: self._handle_process_event('started'))
        process.process_stopped.connect(lambda: self._handle_process_event('stopped'))
        process.error_occurred.connect(lambda msg: self._handle_process_event('error', msg))
        process.start()
    
    def _perform_pre_start_checks(self, cmd: List[str]) -> bool:
        """Perform all pre-start checks"""
        # Check hub4com.exe exists
        if not self._verify_hub4com_exe(cmd):
            return False
        
        # Check for Moxa port
        if not self._check_moxa_port():
            return False
        
        # Check for baud rate mismatches
        if not self._check_baud_rates():
            return False
        
        return True
    
    def _verify_hub4com_exe(self, cmd: List[str]) -> bool:
        """Verify hub4com.exe exists"""
        exe_path = cmd[0]
        if not Path(exe_path).exists():
            possible_paths = [
                Path.cwd() / "hub4com.exe",
                Path("C:/Program Files (x86)/com0com/hub4com.exe"),
                Path("C:/Program Files/com0com/hub4com.exe"),
            ]
            
            for path in possible_paths:
                if path.exists():
                    cmd[0] = str(path)
                    return True
            
            self._show_message("Error", 
                             "hub4com.exe not found. Please ensure it's in the current directory or installed with COM0COM.", 
                             "warning")
            return False
        return True
    
    def _check_moxa_port(self) -> bool:
        """Check for Moxa port and give advice"""
        incoming_port = self.ui_refs['incoming_port'].currentData() or self.ui_refs['incoming_port'].currentText()
        port_info = next((p for p in self.app_state['scanned_ports'] if p.port_name == incoming_port), None)
        
        if port_info and port_info.is_moxa and not self.ui_refs['disable_cts'].isChecked():
            reply = QMessageBox.question(
                self,
                "Moxa Port Detected",
                "You're using a Moxa virtual port. It's recommended to disable CTS handshaking.\n\nDisable CTS handshaking now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.ui_refs['disable_cts'].setChecked(True)
        return True
    
    def _check_baud_rates(self) -> bool:
        """Check for baud rate mismatches"""
        all_baud_rates = [self.ui_refs['incoming_baud'].currentText()]
        for widget in self.app_state['output_port_widgets']:
            all_baud_rates.append(widget.baud_combo.currentText())
        
        if len(set(all_baud_rates)) > 1:
            baud_info = f"Incoming: {self.ui_refs['incoming_baud'].currentText()}\n"
            for i, widget in enumerate(self.app_state['output_port_widgets']):
                baud_info += f"Output {i+1}: {widget.baud_combo.currentText()}\n"
            
            reply = QMessageBox.question(
                self,
                "Baud Rate Mismatch",
                f"Baud rates don't match:\n{baud_info}\n"
                f"This may cause communication issues. Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            return reply == QMessageBox.StandardButton.Yes
        return True
    
    def stop_hub4com(self):
        """Stop the hub4com process"""
        if self.app_state['hub4com_process']:
            self.app_state['hub4com_process'].stop_process()
            self._update_status(AppMessages.STOPPING_HUBCOM)
    
    def on_hub4com_output(self, text: str):
        """Handle output from hub4com process"""
        # Determine log level based on content
        level = "info"
        if "error" in text.lower() or "failed" in text.lower():
            level = "error"
        elif "warning" in text.lower() or "warn" in text.lower():
            level = "warning"
        elif "success" in text.lower() or "started" in text.lower():
            level = "success"
        
        self.output_log_formatter.append_log(self.ui_refs['output_text'], text, level)
    
    def _handle_process_event(self, event_type: str, data: str = None):
        """Handle hub4com process events"""
        output_text = self.ui_refs['output_text']
        
        if event_type == 'started':
            self._update_status(AppMessages.HUBCOM_RUNNING)
            self.output_log_formatter.append_log(output_text, "hub4com started successfully!", "success")
            self.output_log_formatter.append_log(output_text, "Data routing is now active between your ports.", "success")
            
            # Log configuration
            self.output_log_formatter.append_log(output_text, "Configuration:", "info")
            incoming_baud = self.ui_refs['incoming_baud'].currentText()
            self.output_log_formatter.format_key_value(output_text, "Incoming", 
                                                      f"{self.ui_refs['incoming_port'].currentText()} @ {incoming_baud} baud")
            
            for i, widget in enumerate(self.app_state['output_port_widgets']):
                config = widget.get_config()
                self.output_log_formatter.format_key_value(output_text, f"Output {i+1}", 
                                                          f"{config.port_name} @ {config.baud_rate} baud")
        
        elif event_type == 'stopped':
            self._update_status(AppMessages.HUBCOM_STOPPED)
            self.output_log_formatter.format_section_header(output_text, "hub4com stopped")
            self.ui_refs['start_btn'].setEnabled(True)
            self.ui_refs['stop_btn'].setEnabled(False)
        
        elif event_type == 'error':
            self._update_status(AppMessages.ERROR_OCCURRED)
            self.output_log_formatter.append_log(output_text, f"ERROR: {data}", "error")
            self._show_message("Hub4com Error", data, "error")
            self.ui_refs['start_btn'].setEnabled(True)
            self.ui_refs['stop_btn'].setEnabled(False)
    
    # ========================================================================
    # COM0COM MANAGEMENT
    # ========================================================================
    
    def initialize_default_configuration(self):
        """Initialize application with default COM pair configuration"""
        if not WINREG_AVAILABLE:
            return
        
        self._update_status("Initialising virtual COM port configuration...", component='com0com')
        
        thread = Com0comProcess([], "check_and_create_default")
        thread.command_completed.connect(self._on_default_config_completed)
        self.thread_registry.register('default_config', thread)
        thread.start()
    
    def _on_default_config_completed(self, success: bool, output: str):
        """Handle default configuration completion"""
        if success:
            # Parse created/existing pairs
            import re
            created_pairs = []
            existing_pairs = []
            
            if "Successfully created new virtual COM port pairs:" in output:
                pair_matches = re.findall(r'COM\d+<->COM\d+', output)
                created_pairs = [pair.replace('<->', '↔') for pair in pair_matches]
                self._update_status(f"Virtual COM pairs created successfully: {', '.join(created_pairs)}", component='com0com')
            
            if "Found existing virtual COM port pairs:" in output:
                pair_matches = re.findall(r'COM\d+<->COM\d+', output)
                existing_pairs = [pair.replace('<->', '↔') for pair in pair_matches]
                if not created_pairs:
                    self._update_status(f"Virtual COM pairs verified: {', '.join(existing_pairs)} ready", component='com0com')
            
            # Store info for dialog
            self.created_pairs_info = created_pairs
            self.existing_pairs_info = existing_pairs
            
            # Schedule follow-up actions
            QTimer.singleShot(500, self.list_com0com_pairs)
            QTimer.singleShot(1000, self._populate_default_output_ports)
            QTimer.singleShot(1500, self._show_configuration_summary)
        else:
            self._update_status("Virtual COM pair configuration encountered issues - checking existing pairs", component='com0com')
            self.created_pairs_info = []
            self.existing_pairs_info = []
            QTimer.singleShot(1000, self._populate_default_output_ports)
            QTimer.singleShot(1500, self._show_configuration_summary)
    
    def _populate_default_output_ports(self):
        """Pre-populate output port widgets with default COM131 and COM141"""
        default_config = DefaultConfig()
        
        # Ensure we have enough output port widgets
        while len(self.app_state['output_port_widgets']) < len(default_config.output_mapping):
            self.add_output_port()
        
        # Set the default ports and baud rates
        for i, port_config in enumerate(default_config.output_mapping):
            if i < len(self.app_state['output_port_widgets']):
                widget = self.app_state['output_port_widgets'][i]
                
                # Set port name
                if hasattr(widget, 'port_combo') and widget.port_combo:
                    port_name = port_config["port"]
                    combo = widget.port_combo
                    
                    # Add if not present and select
                    port_index = combo.findText(port_name)
                    if port_index == -1:
                        combo.addItem(port_name)
                        port_index = combo.findText(port_name)
                    
                    if port_index != -1:
                        combo.setCurrentIndex(port_index)
                
                # Set baud rate
                if hasattr(widget, 'baud_combo') and widget.baud_combo:
                    baud_rate = port_config["baud"]
                    baud_index = widget.baud_combo.findText(baud_rate)
                    if baud_index != -1:
                        widget.baud_combo.setCurrentIndex(baud_index)
        
        # Enable two-way routing by default
        self.app_state['route_settings']['mode'] = 'two_way'
        
        self._update_status("Output routing configured: COM131 & COM141 @ 115200 baud, two-way mode enabled", component='com0com')
        QTimer.singleShot(200, self.update_preview)
    
    def _show_configuration_summary(self):
        """Show launch dialog to user if enabled in settings"""
        try:
            # Check if launch dialog should be shown
            from core.core import SettingsManager
            settings_manager = SettingsManager()
            
            if not settings_manager.get_show_launch_dialog():
                # Dialog is disabled, skip showing it
                return
            
            created_pairs = getattr(self, 'created_pairs_info', [])
            existing_pairs = getattr(self, 'existing_pairs_info', [])
            
            from ui.dialogs.launch_dialog import LaunchDialog
            dialog = LaunchDialog(
                parent=self,
                created_pairs=created_pairs,
                existing_pairs=existing_pairs
            )
            dialog.exec()
        except Exception as e:
            print(f"Error in _show_configuration_summary: {type(e).__name__}: {e}")
            # Fallback message
            self._show_message(
                "Configuration Summary",
                "Virtual COM port configuration completed successfully.\n\n"
                "• COM131↔COM132 and COM141↔COM142 pairs are ready\n"
                "• Output routing: COM131 & COM141 @ 115200 baud\n"
                "• Connect external applications to COM132 & COM142",
                "info"
            )
    
    def list_com0com_pairs(self):
        """List all com0com port pairs"""
        self._update_status(AppMessages.LISTING_PAIRS, component='com0com')
        self.ui_refs['port_pairs_list'].clear()
        
        thread = Com0comProcess(["list"])
        thread.command_completed.connect(lambda s, o: self._handle_com0com_operation(s, o, OperationType.LIST_PAIRS))
        self.thread_registry.register('com0com_list', thread)
        thread.start()
    
    def create_com0com_pair(self):
        """Create a new com0com port pair"""
        accepted, cmd_args = PairCreationDialog.create_port_pair(self)
        
        if accepted and cmd_args:
            self._update_status(AppMessages.CREATING_PAIR, component='com0com')
            
            thread = Com0comProcess(cmd_args)
            thread.command_completed.connect(lambda s, o: self._handle_com0com_operation(s, o, OperationType.CREATE_PAIR))
            self.thread_registry.register('com0com_create', thread)
            thread.start()
    
    def remove_com0com_pair(self):
        """Remove selected com0com port pair"""
        current_item = self.ui_refs['port_pairs_list'].currentItem()
        if not current_item:
            return
        
        text = current_item.text()
        if "CNCA" in text:
            pair_num = text.split("CNCA")[1].split()[0]
            
            reply = QMessageBox.question(
                self,
                "Confirm Removal",
                f"Remove virtual port pair CNCA{pair_num} ↔ CNCB{pair_num}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._update_status(AppMessages.REMOVING_PAIR, component='com0com')
                
                thread = Com0comProcess(["remove", pair_num])
                thread.command_completed.connect(lambda s, o: self._handle_com0com_operation(s, o, OperationType.REMOVE_PAIR))
                self.thread_registry.register('com0com_remove', thread)
                thread.start()
    
    def _handle_com0com_operation(self, success: bool, output: str, operation: OperationType):
        """Generic handler for com0com operations"""
        if operation == OperationType.LIST_PAIRS:
            if success:
                pairs = self._parse_com0com_output(output)
                self._populate_pairs_list(pairs)
            else:
                self._update_status("Failed to list pairs", component='com0com')
                self._show_message("Error", f"Failed to list com0com pairs:\n{output}", "warning")
        
        else:
            operation_messages = {
                OperationType.CREATE_PAIR: ("create", AppMessages.PORT_PAIR_CREATED, "Virtual port pair created successfully!"),
                OperationType.REMOVE_PAIR: ("remove", AppMessages.PORT_PAIR_REMOVED, None),
                OperationType.MODIFY_PAIR: ("modify", "Properties modified successfully", None)
            }
            
            op_name, status_msg, info_msg = operation_messages.get(operation, ("", "", None))
            
            if success:
                if status_msg:
                    self._update_status(status_msg, component='com0com')
                if info_msg:
                    self._show_message("Success", info_msg)
                
                self.list_com0com_pairs()
                self.refresh_port_lists()
            else:
                self._update_status(f"Failed to {op_name} port pair", component='com0com')
                self._show_message("Error", f"Failed to {op_name} port pair:\n{output}", "error")
    
    def _parse_com0com_output(self, output: str) -> Dict:
        """Parse com0com list output"""
        pairs = {}
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('command>'):
                parts = line.split(None, 1)
                if len(parts) >= 1:
                    port = parts[0]
                    params = parts[1] if len(parts) > 1 else ""
                    
                    if port.startswith('CNCA'):
                        pair_num = port[4:]
                        if pair_num not in pairs:
                            pairs[pair_num] = {}
                        pairs[pair_num]['A'] = (port, params)
                    elif port.startswith('CNCB'):
                        pair_num = port[4:]
                        if pair_num not in pairs:
                            pairs[pair_num] = {}
                        pairs[pair_num]['B'] = (port, params)
        
        return pairs
    
    def _populate_pairs_list(self, pairs: Dict):
        """Populate the pairs list widget"""
        list_widget = self.ui_refs['port_pairs_list']
        list_widget.clear()
        
        if not pairs:
            self._update_status("No port pairs configured", component='com0com')
            no_pairs_item = QListWidgetItem(
                "No virtual port pairs found yet.\n\n"
                "Click 'Create New Pair' to create your first pair of connected virtual ports.\n"
                "This allows two applications to communicate through simulated serial ports."
            )
            no_pairs_item.setBackground(ThemeManager.get_accent_color('pair_info'))
            list_widget.addItem(no_pairs_item)
            return
        
        for pair_num, ports in sorted(pairs.items()):
            if 'A' in ports and 'B' in ports:
                self._add_pair_to_list(pair_num, ports)
        
        count = len(pairs)
        self._update_status(f"Found {count} port pair{'s' if count != 1 else ''}", component='com0com')
    
    def _add_pair_to_list(self, pair_num: str, ports: Dict):
        """Add a single pair to the list"""
        port_a, params_a = ports['A']
        port_b, params_b = ports['B']
        
        com_a = self._extract_actual_port_name(port_a, params_a)
        com_b = self._extract_actual_port_name(port_b, params_b)
        
        # Build display text
        if com_a != port_a or com_b != port_b:
            main_text = f"{com_a} ↔ {com_b}  [{port_a} ↔ {port_b}]"
        else:
            main_text = f"{port_a} ↔ {port_b}"
        
        # Add status indicators
        status_indicators = self._get_status_indicators(params_a, params_b)
        if status_indicators:
            main_text += f"  [Features: {', '.join(status_indicators)}]"
        
        # Create list item
        item = QListWidgetItem(main_text)
        tooltip = HelpManager.get_tooltip("pair_tooltip",
            port_a=port_a, 
            params_a=params_a or 'Standard settings (no special features)',
            port_b=port_b, 
            params_b=params_b or 'Standard settings (no special features)'
        )
        item.setToolTip(tooltip)
        
        if status_indicators:
            item.setBackground(ThemeManager.get_accent_color('pair_highlight'))
        
        self.ui_refs['port_pairs_list'].addItem(item)
    
    def _extract_actual_port_name(self, virtual_name: str, params: str) -> str:
        """Extract the actual COM port name from parameters"""
        if not params:
            return virtual_name
        
        if "RealPortName=" in params:
            real_name = params.split("RealPortName=")[1].split(",")[0]
            if real_name and real_name != "-":
                return real_name
        
        if "PortName=" in params:
            port_name = params.split("PortName=")[1].split(",")[0]
            if port_name and port_name not in ["-", "COM#"]:
                return port_name
        
        return virtual_name
    
    def _get_status_indicators(self, params_a: str, params_b: str) -> List[str]:
        """Get status indicators from parameters"""
        indicators = []
        params = params_a + " " + params_b
        
        indicators_map = {
            "EmuBR=yes": "Baud Rate Timing",
            "EmuOverrun=yes": "Buffer Overrun",
            "ExclusiveMode=yes": "Exclusive Mode",
            "PlugInMode=yes": "Plug-In Mode"
        }
        
        for param, name in indicators_map.items():
            if param in params:
                indicators.append(name)
        
        return indicators
    
    def on_pair_selected(self):
        """Handle port pair selection"""
        has_selection = self.ui_refs['port_pairs_list'].currentItem() is not None
        self.ui_refs['remove_pair_btn'].setEnabled(has_selection)
        self.ui_refs['settings_btn'].setEnabled(has_selection)
    
    def on_pair_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on port pair"""
        if not item or "No virtual port pairs found" in item.text():
            return
        
        dialog = self._create_pair_details_dialog(item)
        dialog.exec()
    
    def _create_pair_details_dialog(self, item: QListWidgetItem) -> QDialog:
        """Create port pair details dialog using theme system"""
        dialog = ThemeManager.create_dialog_window("Port Pair Details", 500, 300)
        
        layout = QVBoxLayout(dialog)
        ThemeManager.set_widget_margins(layout, "dialog")
        layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        details_text = ThemeManager.create_textedit("console_large")
        details_text.setReadOnly(True)
        
        # Format information
        tooltip = item.toolTip()
        formatted_text = "COM0COM Virtual Port Pair Details\n"
        formatted_text += "=" * 40 + "\n\n"
        formatted_text += tooltip.replace("Port A (", "📍 Port A (").replace("Port B (", "📍 Port B (")
        formatted_text += "\n\n"
        
        # Add parameter explanations
        param_explanations = {
            "EmuBR=yes": ("BAUD RATE TIMING: ENABLED\n"
                        "   - Port behaves with realistic serial port timing\n\n"),
            "EmuOverrun=yes": ("BUFFER OVERRUN PROTECTION: ENABLED\n"
                            "   - Data can be lost if not read fast enough (like real ports)\n\n"),
            "ExclusiveMode=yes": ("EXCLUSIVE ACCESS MODE: ENABLED\n"
                                "   - Port is hidden until the paired port is opened\n\n"),
            "PlugInMode=yes": ("PLUG-IN MODE: ENABLED\n"
                            "   - Port appears/disappears when paired port opens/closes\n\n")
        }
        
        for param, explanation in param_explanations.items():
            if param in tooltip:
                formatted_text += explanation
        
        formatted_text += "\nHELPFUL TIPS:\n"
        formatted_text += "• Turn ON 'Baud Rate Timing' for applications that need realistic serial timing\n"
        formatted_text += "• Turn ON 'Buffer Overrun Protection' to test how apps handle data loss\n"
        formatted_text += "• For most users: Leave all settings OFF for best performance\n"
        formatted_text += "• Check Device Manager to verify port names are correct"
        
        details_text.setPlainText(formatted_text)
        layout.addWidget(details_text)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        button_layout.addStretch()
        close_btn = ThemeManager.create_button("Close", dialog.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        return dialog
    
    def show_settings_menu(self):
        """Show dynamic settings menu for selected pair"""
        current_item = self.ui_refs['port_pairs_list'].currentItem()
        if not current_item or "No virtual port pairs found" in current_item.text():
            return
        
        # Parse port names and settings
        item_text = current_item.text()
        port_a, port_b = self.port_manager.extract_port_info(item_text)
        
        if not port_a or not port_b:
            return
        
        current_settings = self._parse_current_settings(current_item.toolTip())
        
        # Create and show menu
        menu = self._create_settings_menu(port_a, port_b, current_settings)
        menu.exec(self.ui_refs['settings_btn'].mapToGlobal(self.ui_refs['settings_btn'].rect().bottomLeft()))
    
    def _parse_current_settings(self, tooltip_text: str) -> Dict[str, str]:
        """Parse current settings from tooltip text"""
        settings = {}
        if not tooltip_text:
            return settings
        
        for line in tooltip_text.split('\n'):
            for param in ['EmuBR', 'EmuOverrun', 'ExclusiveMode', 'PlugInMode']:
                if f'{param}=yes' in line:
                    settings[param] = 'yes'
                elif f'{param}=no' in line:
                    settings[param] = 'no'
        
        return settings
    
    def _create_settings_menu(self, port_a: str, port_b: str, current_settings: Dict) -> QMenu:
        """Create settings menu for port pair"""
        menu = QMenu(self)
        
        # Header
        header_action = menu.addAction(f"Configure Settings for {port_a} <-> {port_b}")
        header_action.setEnabled(False)
        menu.addSeparator()
        
        # Settings with proper Windows 10 checkboxes
        settings_config = [
            ("EmuBR", "Baud Rate Timing"),
            ("EmuOverrun", "Buffer Overrun Protection"),
            ("ExclusiveMode", "Exclusive Access Mode"),
            ("PlugInMode", "Plug-In Mode")
        ]
        
        for param, display_name in settings_config:
            is_enabled = current_settings.get(param) == "yes"
            new_value = "no" if is_enabled else "yes"
            
            menu.addAction(self.checkbox_icon(is_enabled), display_name, 
                        partial(self.quick_modify_pair, param, new_value))
        
        menu.addSeparator()
        menu.addAction("Help", lambda: self._show_help(HelpTopic.COM0COM_SETTINGS))
        return menu

    def show_port_pair_context_menu(self, position):
        """Show context menu for port pair right-click"""
        # Get the item at the clicked position
        item = self.ui_refs['port_pairs_list'].itemAt(position)
        if not item or "No virtual port pairs found" in item.text():
            return
        
        # Select the item to maintain consistency with existing behavior
        self.ui_refs['port_pairs_list'].setCurrentItem(item)
        
        # Parse port names and settings for the clicked item
        item_text = item.text()
        port_a, port_b = self.port_manager.extract_port_info(item_text)
        
        if not port_a or not port_b:
            return
        
        current_settings = self._parse_current_settings(item.toolTip())
        
        # Create and show the same menu as the settings button
        menu = self._create_settings_menu(port_a, port_b, current_settings)
        
        # Add separator and additional context menu actions
        menu.addSeparator()
        menu.addAction("Remove Pair", self.remove_com0com_pair)
        
        # Show menu at the clicked position
        menu.exec(self.ui_refs['port_pairs_list'].mapToGlobal(position))

    def quick_modify_pair(self, param: str, value: str):
        """Quick modify a parameter for selected pair"""
        current_item = self.ui_refs['port_pairs_list'].currentItem()
        if not current_item:
            return
        
        port_a, port_b = self.port_manager.extract_port_info(current_item.text())
        if not port_a or not port_b:
            return
        
        self._update_status(f"Setting {param}={value} for {port_a} ↔ {port_b}...", component='com0com')
        
        # Modify both ports
        self.app_state['pending_modifications'] = 2
        self.app_state['modification_success'] = True
        
        thread_count = 0
        for port in [port_a, port_b]:
            thread = Com0comProcess(["change", port, f"{param}={value}"])
            thread.command_completed.connect(self.on_modify_completed)
            self.thread_registry.register(f'com0com_modify_{thread_count}', thread)
            thread_count += 1
            thread.start()
    
    def on_modify_completed(self, success: bool, output: str):
        """Handle modify command completion"""
        self.app_state['pending_modifications'] -= 1
        if not success:
            self.app_state['modification_success'] = False
        
        if self.app_state['pending_modifications'] == 0:
            if self.app_state['modification_success']:
                self._update_status("Properties modified successfully", component='com0com')
                QTimer.singleShot(500, self.list_com0com_pairs)
            else:
                self._update_status("Failed to modify properties", component='com0com')
                self._show_message("Error", "Some modifications failed", "warning")
    
    # ========================================================================
    # MENU MANAGEMENT
    # ========================================================================
    
    def show_hub4com_settings_menu(self):
        """Show consolidated hub4com settings menu"""
        menu = self._create_hub4com_menu()
        menu.exec(self.ui_refs['hub4com_settings_btn'].mapToGlobal(
            self.ui_refs['hub4com_settings_btn'].rect().bottomLeft()))
    
    def _create_hub4com_menu(self) -> QMenu:
        """Create hub4com settings menu"""
        menu = QMenu(self)
        settings = self.app_state['route_settings']
        
        # Header
        menu.addAction("Hub4com Settings").setEnabled(False)
        menu.addSeparator()
        
        # Route Configuration
        menu.addAction("Route Configuration").setEnabled(False)
        
        # Route mode options
        route_modes = [
            ('one_way', "One-Way Splitting"),
            ('two_way', "Two-Way Communication"),
            ('full_network', "Full Network Mode")
        ]
        
        for mode, label in route_modes:
            is_checked = settings['mode'] == mode
            action = menu.addAction(self.checkbox_icon(is_checked), label)
            action.triggered.connect(lambda checked, m=mode: self.set_route_mode(m))
        
        menu.addSeparator()
        
        # Advanced Routing
        menu.addAction("Advanced Routing").setEnabled(False)
        
        advanced_options = [
            ('echo_enabled', "Echo Back to Source", self.toggle_route_setting),
            ('flow_control_enabled', "Enable Flow Control", self.toggle_route_setting),
            ('disable_default_fc', "Disable Default Flow Control", self.toggle_route_setting)
        ]
        
        for key, label, callback in advanced_options:
            is_checked = settings.get(key, False)
            action = menu.addAction(self.checkbox_icon(is_checked), label)
            action.triggered.connect(lambda checked, k=key: callback(k))
        
        menu.addSeparator()
        
        # Port Settings
        menu.addAction("Port Settings").setEnabled(False)
        
        port_options = [
            (self.ui_refs['disable_cts'], "Disable CTS Handshaking"),
            (self.ui_refs['sync_baud_rates'], "Sync Baud Rates")
        ]
        
        for checkbox, label in port_options:
            is_checked = checkbox.isChecked()
            action = menu.addAction(self.checkbox_icon(is_checked), label)
            action.triggered.connect(lambda: checkbox.setChecked(not checkbox.isChecked()))
        
        menu.addSeparator()
        
        # Baud rate submenu
        baud_menu = menu.addMenu("Set All Baud Rates")
        self._create_baud_rate_menu(baud_menu)
        
        menu.addSeparator()
        menu.addAction("Help", lambda: self._show_help(HelpTopic.HUB4COM_ROUTES))
        
        return menu
    
    def _create_baud_rate_menu(self, menu: QMenu):
        """Create baud rate submenu"""
        for rate in Config.QUICK_BAUD_RATES:
            action = menu.addAction(f"{rate} baud")
            action.triggered.connect(lambda checked, r=rate: self.set_all_baud_rates(r))
        
        menu.addSeparator()
        all_rates_submenu = menu.addMenu("All Baud Rates")
        
        for rate in Config.BAUD_RATES:
            if rate not in Config.QUICK_BAUD_RATES:
                action = all_rates_submenu.addAction(f"{rate} baud")
                action.triggered.connect(lambda checked, r=rate: self.set_all_baud_rates(r))
    
    # ========================================================================
    # ROUTE OPTIONS MANAGEMENT
    # ========================================================================
    
    def set_route_mode(self, mode: str):
        """Set the route mode and update UI"""
        self.app_state['route_settings']['mode'] = mode
        self.update_preview()
    
    def toggle_route_setting(self, setting_key: str):
        """Toggle a route setting"""
        self.app_state['route_settings'][setting_key] = not self.app_state['route_settings'][setting_key]
        self.update_preview()
    
    def _show_help(self, topic: HelpTopic):
        """Show help dialog for specified topic"""
        HelpManager.show_help(topic, self)
    
    # ========================================================================
    # APPLICATION LIFECYCLE
    # ========================================================================
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop all threads
        failed_threads = self.thread_registry.stop_all()
        
        if failed_threads:
            print(f"Warning: The following threads did not stop gracefully: {', '.join(failed_threads)}")
        
        # Handle hub4com process
        if self.app_state['hub4com_process'] and self.app_state['hub4com_process'].isRunning():
            reply = QMessageBox.question(
                self,
                "Close Application",
                "hub4com is still running. Stop it before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_hub4com()
                if self.app_state['hub4com_process']:
                    self.app_state['hub4com_process'].wait(3000)
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()