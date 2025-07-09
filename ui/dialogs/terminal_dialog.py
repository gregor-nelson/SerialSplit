#!/usr/bin/env python3
"""
Terminal Dialog - Professional floating terminal window with split terminal support
Aligned with main GUI design patterns for cohesive user experience
"""

from typing import Optional, Dict, List
import threading

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame, QComboBox, QGroupBox, 
                             QMenu, QApplication, QWidget, QSizePolicy, QSplitter,
                             QScrollArea, QButtonGroup, QRadioButton, QMessageBox,
                             QFileDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal, QByteArray, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QTextCursor, QAction, QFont, QIcon, QColor

from core.core import SerialPortInfo, SerialPortMonitor, PortScanner, WINREG_AVAILABLE
from ui.theme.theme import (
    ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts, IconManager
)
from ui.theme.icons.icons import AppIcons
from ui.windows.terminal_formatter import TerminalStreamFormatter
from ui.utils import ButtonConfig, ControlPanelColumn, StatusIndicator, ControlPanelBuilder


class TerminalSplitMode:
    """Terminal split mode constants"""
    NONE = "none"
    HORIZONTAL = "horizontal"
    THREE_WAY = "three_way"
    GRID = "grid"
    
    @staticmethod
    def get_display_name(mode: str) -> str:
        """Get display name for split mode"""
        names = {
            TerminalSplitMode.NONE: "No Split",
            TerminalSplitMode.HORIZONTAL: "Horizontal Split",
            TerminalSplitMode.THREE_WAY: "Three-Way Split",
            TerminalSplitMode.GRID: "Grid (2x2)"
        }
        return names.get(mode, "No Split")
    
    @staticmethod
    def get_terminal_count(mode: str) -> int:
        """Get number of terminals for split mode"""
        counts = {
            TerminalSplitMode.NONE: 1,
            TerminalSplitMode.HORIZONTAL: 2,
            TerminalSplitMode.THREE_WAY: 3,
            TerminalSplitMode.GRID: 4
        }
        return counts.get(mode, 1)


class TerminalInstanceWidget(QWidget):
    """Individual terminal instance with mini toolbar"""
    
    terminal_focused = pyqtSignal(int)  # Emits terminal ID when focused
    
    def __init__(self, terminal_id: int, parent=None):
        super().__init__(parent)
        self.terminal_id = terminal_id
        self.is_paused = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the terminal instance UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Terminal header with mini controls
        header = self.create_terminal_header()
        layout.addWidget(header)
        
        # Terminal display
        self.terminal_display = self.create_terminal_display()
        layout.addWidget(self.terminal_display)
        
        # Apply container styling
        self.setStyleSheet(f"""
            TerminalInstanceWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
                border: 1px solid {AppColors.BORDER_DEFAULT};
            }}
        """)
        
    def create_terminal_header(self) -> QWidget:
        """Create minimal header for terminal instance"""
        header = QWidget()
        header.setFixedHeight(32)  # Slightly taller for better alignment
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border-bottom: 1px solid {AppColors.BORDER_LIGHT};
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 0, 12, 0)  # Consistent margins
        layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # Terminal number badge
        self.terminal_badge = QLabel(f"Terminal {self.terminal_id}")
        self.terminal_badge.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-weight: {AppFonts.BOLD_WEIGHT};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        layout.addWidget(self.terminal_badge)
        
        # Connection status indicator
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.ERROR_PRIMARY};
                font-size: 12pt;
            }}
        """)
        self.connection_indicator.setToolTip("Disconnected")
        layout.addWidget(self.connection_indicator)
        
        # Port info label
        self.port_info_label = QLabel("No connection")
        self.port_info_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        layout.addWidget(self.port_info_label)
        
        layout.addStretch()
        
        # Mini controls - using consistent button creation
        self.pause_btn = self._create_mini_button("pause", f"Pause Terminal {self.terminal_id}")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_btn)
        
        self.clear_btn = self._create_mini_button("clear", f"Clear Terminal {self.terminal_id}")
        self.clear_btn.clicked.connect(self.clear_terminal)
        layout.addWidget(self.clear_btn)
        
        return header
    
    def _create_mini_button(self, icon_name: str, tooltip: str) -> QPushButton:
        """Create mini button with consistent styling"""
        btn = QPushButton()
        btn.setFixedSize(24, 24)
        btn.setToolTip(tooltip)
        
        # Apply icon
        icon_template = getattr(AppIcons, icon_name.upper(), None)
        if icon_template:
            icon = IconManager.create_svg_icon(icon_template, AppColors.ICON_DEFAULT, QSize(16, 16))
            btn.setIcon(icon)
            btn.setIconSize(QSize(16, 16))
        
        # Apply mini button styling
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                padding: {AppDimensions.PADDING_TINY};
                border-radius: 2px;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_HOVER};
                border: 1px solid {AppColors.BORDER_DEFAULT};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_PRESSED};
            }}
            QPushButton:checked {{
                background-color: {AppColors.ACCENT_BLUE};
                border: 1px solid {AppColors.ACCENT_BLUE};
            }}
        """)
        
        return btn
    
    def create_terminal_display(self) -> QTextEdit:
        """Create the terminal display widget"""
        terminal = QTextEdit()
        terminal.setReadOnly(True)
        terminal.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        
        # Apply main GUI text edit styling
        terminal.setStyleSheet(AppStyles.textedit())
        
        # Set console font
        terminal.setFont(AppFonts.CONSOLE)
        
        # Set up focus handling
        terminal.focusInEvent = lambda e: self._handle_focus_in(e)
        
        return terminal
    
    def _handle_focus_in(self, event):
        """Handle focus in event"""
        self.terminal_focused.emit(self.terminal_id)
        super(QTextEdit, self.terminal_display).focusInEvent(event)
    
    def toggle_pause(self):
        """Toggle terminal pause state"""
        self.is_paused = self.pause_btn.isChecked()
        if self.is_paused:
            self.pause_btn.setToolTip(f"Resume Terminal {self.terminal_id}")
        else:
            self.pause_btn.setToolTip(f"Pause Terminal {self.terminal_id}")
    
    def clear_terminal(self):
        """Clear this terminal's display"""
        self.terminal_display.clear()
    
    def set_focused(self, focused: bool):
        """Update terminal appearance based on focus state"""
        if focused:
            self.setStyleSheet(f"""
                TerminalInstanceWidget {{
                    background-color: {AppColors.BACKGROUND_WHITE};
                    border: 2px solid {AppColors.BORDER_FOCUS};
                }}
            """)
            self.terminal_badge.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.ACCENT_BLUE};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    font-weight: {AppFonts.BOLD_WEIGHT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                TerminalInstanceWidget {{
                    background-color: {AppColors.BACKGROUND_WHITE};
                    border: 1px solid {AppColors.BORDER_DEFAULT};
                }}
            """)
            self.terminal_badge.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DISABLED};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    font-weight: {AppFonts.BOLD_WEIGHT};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                }}
            """)
    
    def update_connection_status(self, is_connected: bool, port_info: str = ""):
        """Update the connection status indicator"""
        if is_connected:
            self.connection_indicator.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.SUCCESS_PRIMARY};
                    font-size: 12pt;
                }}
            """)
            self.connection_indicator.setToolTip("Connected")
            self.port_info_label.setText(port_info)
            self.port_info_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                }}
            """)
        else:
            self.connection_indicator.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.ERROR_PRIMARY};
                    font-size: 12pt;
                }}
            """)
            self.connection_indicator.setToolTip("Disconnected")
            self.port_info_label.setText("No connection")
            self.port_info_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DISABLED};
                    font-size: {AppFonts.DEFAULT_SIZE};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                }}
            """)


class TerminalConnection:
    """Encapsulates connection state for a single terminal"""
    def __init__(self, terminal_id: int):
        self.terminal_id = terminal_id
        self.port_info: Optional[SerialPortInfo] = None
        self.port_monitor: Optional[SerialPortMonitor] = None
        self.baud_rate: int = 115200
        self.is_connected: bool = False
        self.bytes_sent: int = 0
        self.bytes_received: int = 0
        
    def cleanup(self):
        """Clean up connection resources"""
        if self.port_monitor:
            self.port_monitor.stop_monitoring()
            self.port_monitor = None
        self.is_connected = False


class TerminalDialog(QDialog):
    """
    Professional terminal dialog aligned with main GUI design patterns
    """
    
    # Button configuration constants (matching main GUI pattern)
    BUTTON_CONFIG = {
        'icons': {
            "refresh": "REFRESH", "connect": "PLAY", "disconnect": "STOP",
            "clear": "CLEAR", "export": "EXPORT", "settings": "SETTINGS",
            "split": "SPLIT"
        },
        'text': {
            "refresh": "Refresh", "connect": "Connect", "disconnect": "Disconnect",
            "clear": "Clear All", "export": "Export", "settings": "Settings",
            "split": "Split"
        },
        'primary_actions': ["connect"]
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.encoding = 'utf-8'
        
        # Core components
        self.control_panel_builder = ControlPanelBuilder(self)
        
        # Available ports
        self.available_ports = []
        self.baud_rates = ["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"]
        
        # User preferences (global defaults)
        self.default_auto_scroll = True
        self.default_font_size = AppFonts.FONT_SIZE_LARGE
        self.default_word_wrap = False
        self.default_show_timestamps = True
        self.show_settings_panel = True
        
        # Terminal Management
        self.terminal_widgets: Dict[int, TerminalInstanceWidget] = {}
        self.terminal_formatters: Dict[int, TerminalStreamFormatter] = {}
        self.terminal_connections: Dict[int, TerminalConnection] = {}
        self.terminal_states: Dict[int, dict] = {}
        self.active_terminal_id = 1
        self.current_split_mode = TerminalSplitMode.NONE
        
        # Buffer timers for each terminal
        self.buffer_timers: Dict[int, QTimer] = {}
        
        # Layout management
        self.main_splitter: Optional[QSplitter] = None
        self.terminal_container: Optional[QWidget] = None
        
        # UI references
        self.ui_refs = {}
        
        # Saved splitter positions
        self.splitter_positions = {
            TerminalSplitMode.HORIZONTAL: [50, 50],
            TerminalSplitMode.THREE_WAY: {'top': [50, 50], 'main': [50, 50]},
            TerminalSplitMode.GRID: {'top': [50, 50], 'bottom': [50, 50], 'main': [50, 50]}
        }
        
        self.init_ui()
        self.refresh_ports()
    
    def init_ui(self):
        """Initialize the professional terminal UI"""
        self.setWindowTitle("Multi-Terminal Monitor")
        self.setMinimumSize(900, 600)
        self.resize(1200, 700)
        
        # Apply dialog styling
        ThemeManager.style_dialog(self)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section with control panel
        header_widget = self.create_header_section()
        main_layout.addWidget(header_widget)
        
        # Separator
        main_layout.addWidget(ThemeManager.create_separator("horizontal"))
        
        # Content section with splitter
        content_widget = self.create_content_section()
        main_layout.addWidget(content_widget)
        
        # Status bar
        status_bar = self.create_status_bar()
        main_layout.addWidget(status_bar)
        
        # Initialize first terminal
        self._initialize_first_terminal()
    
    def _create_groupbox_with_layout(self, title: str, layout_class=QVBoxLayout) -> tuple:
        """Create a styled groupbox with layout - matching main GUI pattern"""
        group = ThemeManager.create_groupbox(title)
        
        # Match main GUI's groupbox styling
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: normal;
                color: {AppColors.TEXT_DEFAULT};
                border: {AppDimensions.BORDER_WIDTH_STANDARD}px solid {AppColors.BORDER_DEFAULT};
                margin-top: 12px;
                padding-top: 2px;
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
            layout.setContentsMargins(8, 4, 8, 8)
        return group, layout
    
    def create_header_section(self) -> QWidget:
        """Create professional header with control panel pattern"""
        header = QWidget()
        header.setFixedHeight(120)  # Taller to accommodate control panel
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
                border-bottom: 1px solid {AppColors.BORDER_LIGHT};
            }}
        """)
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        title_bar = self._create_title_bar()
        layout.addWidget(title_bar)
        
        # Control panel using ControlPanelBuilder
        columns = [
            ControlPanelColumn(
                title="Connection",
                buttons=[
                    ButtonConfig("refresh", self.refresh_ports, "Refresh available ports", True),
                    ButtonConfig("connect", self.toggle_connection, "Connect to selected port", True, "connect_btn"),
                    ButtonConfig("disconnect", self.toggle_connection, "Disconnect from port", False, "disconnect_btn")
                ],
                width_hint=140
            ),
            ControlPanelColumn(
                title="Terminal Control",
                buttons=[
                    ButtonConfig("split", self._show_split_menu, "Configure terminal split mode", True, "split_btn"),
                    ButtonConfig("clear", self.clear_all_terminals, "Clear all terminal displays", True),
                    ButtonConfig("export", self.export_terminal_content, "Export terminal content", True)
                ],
                width_hint=160
            ),
            ControlPanelColumn(
                title="Settings",
                buttons=[
                    ButtonConfig("settings", self.toggle_settings_panel, "Toggle settings panel", True, "settings_toggle_btn")
                ],
                width_hint=100
            )
        ]
        
        # Status indicators
        status_indicators = [
            StatusIndicator("connection_status", "Disconnected"),
            StatusIndicator("terminal_status", "Ready")
        ]
        
        control_panel = self.control_panel_builder.create_control_panel(columns, status_indicators)
        layout.addWidget(control_panel)
        
        return header
    
    def _create_title_bar(self) -> QWidget:
        """Create title bar section"""
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(16, 8, 16, 8)
        
        # Title
        title_label = QLabel("Multi-Terminal Monitor")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-size: 16pt;
                font-weight: {AppFonts.BOLD_WEIGHT};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Terminal count info
        self.terminal_info_label = QLabel("1 Terminal")
        self.terminal_info_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        layout.addWidget(self.terminal_info_label)
        
        return title_bar
    
    def _show_split_menu(self):
        """Show split mode menu"""
        menu = QMenu(self)
        menu.setStyleSheet(self._get_menu_style())
        
        # Add split mode options
        for mode in [TerminalSplitMode.NONE, TerminalSplitMode.HORIZONTAL, 
                     TerminalSplitMode.THREE_WAY, TerminalSplitMode.GRID]:
            name = TerminalSplitMode.get_display_name(mode)
            action = menu.addAction(name)
            action.triggered.connect(lambda checked, m=mode: self._change_split_mode(m))
            if mode == self.current_split_mode:
                action.setCheckmark = True
                # Add checkmark visual
                action.setText(f"✓ {name}")
                action.setEnabled(False)
        
        # Show menu below button
        menu.exec(self.ui_refs['split_btn'].mapToGlobal(
            self.ui_refs['split_btn'].rect().bottomLeft()))
    
    def _get_menu_style(self) -> str:
        """Get Windows 10 dark mode menu styling - matching main GUI"""
        return f"""
        QMenu {{
            background-color: {AppColors.BACKGROUND_MENU};
            color: {AppColors.TEXT_MENU};
            border: 1px solid {AppColors.BORDER_DEFAULT};
            padding: 2px;
        }}
        QMenu::item {{
            padding: 4px 20px 4px 20px;
            margin: 2px;
            min-height: 20px;
        }}
        QMenu::item:selected {{
            background-color: {AppColors.SELECTION_MENU};
            color: {AppColors.TEXT_DEFAULT};
        }}
        QMenu::item:disabled {{
            color: {AppColors.TEXT_DISABLED};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {AppColors.BORDER_LIGHT};
            margin: 5px 10px;
        }}
        """
    
    def create_content_section(self) -> QWidget:
        """Create main content area with settings panel and terminal"""
        content_widget = QWidget()
        layout = QHBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter
        self.splitter = ThemeManager.create_splitter(Qt.Orientation.Horizontal)
        
        # Left panel - Settings
        self.settings_panel = self.create_settings_panel()
        self.splitter.addWidget(self.settings_panel)
        
        # Right panel - Terminal container
        self.terminal_container = self.create_terminal_section()
        self.splitter.addWidget(self.terminal_container)
        
        # Configure splitter
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([320, 880])
        
        layout.addWidget(self.splitter)
        return content_widget
    
    def create_settings_panel(self) -> QWidget:
        """Create professional settings panel matching main GUI pattern"""
        panel = QWidget()
        panel.setMinimumWidth(280)
        panel.setMaximumWidth(400)
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border-right: 1px solid {AppColors.BORDER_LIGHT};
            }}
        """)
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(AppStyles.scroll_area())
        
        # Settings container
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(16, 16, 16, 16)
        settings_layout.setSpacing(16)
        
        # Active Terminal Card
        active_group, active_layout = self._create_settings_card("Active Terminal")
        
        # Active terminal indicator
        self.ui_refs['active_terminal_label'] = QLabel(f"Terminal {self.active_terminal_id}")
        self.ui_refs['active_terminal_label'].setStyleSheet(f"""
            QLabel {{
                color: {AppColors.ACCENT_BLUE};
                font-size: 11pt;
                font-weight: {AppFonts.BOLD_WEIGHT};
                padding: 6px 12px;
                background-color: {AppColors.BACKGROUND_WHITE};
                border: 2px solid {AppColors.ACCENT_BLUE};
                border-radius: 4px;
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        active_layout.addWidget(self.ui_refs['active_terminal_label'])
        
        settings_layout.addWidget(active_group)
        
        # Connection Settings Card
        connection_group, connection_layout = self._create_settings_card("Connection Settings")
        
        # Port selection
        port_label = QLabel("Serial Port:")
        port_label.setStyleSheet(f"color: {AppColors.TEXT_DEFAULT}; font-weight: 500;")
        connection_layout.addWidget(port_label)
        
        port_layout = QHBoxLayout()
        self.ui_refs['port_combo'] = ThemeManager.create_combobox()
        self.ui_refs['port_combo'].setMinimumWidth(180)
        self.ui_refs['port_combo'].currentIndexChanged.connect(self._on_port_selection_changed)
        port_layout.addWidget(self.ui_refs['port_combo'])
        
        refresh_btn = self._create_icon_button("refresh", "Refresh ports")
        refresh_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(refresh_btn)
        
        connection_layout.addLayout(port_layout)
        
        # Baud rate
        baud_label = QLabel("Baud Rate:")
        baud_label.setStyleSheet(f"color: {AppColors.TEXT_DEFAULT}; font-weight: 500;")
        connection_layout.addWidget(baud_label)
        
        self.ui_refs['baud_combo'] = ThemeManager.create_combobox()
        self.ui_refs['baud_combo'].addItems(self.baud_rates)
        self.ui_refs['baud_combo'].setCurrentText("115200")
        self.ui_refs['baud_combo'].currentTextChanged.connect(self._on_baud_rate_changed)
        connection_layout.addWidget(self.ui_refs['baud_combo'])
        
        settings_layout.addWidget(connection_group)
        
        # Display Settings Card
        display_group, display_layout = self._create_settings_card("Display Settings")
        
        # Checkboxes
        self.ui_refs['auto_scroll_cb'] = ThemeManager.create_checkbox("Auto-scroll to bottom")
        self.ui_refs['auto_scroll_cb'].setChecked(self.default_auto_scroll)
        self.ui_refs['auto_scroll_cb'].toggled.connect(self.toggle_auto_scroll)
        display_layout.addWidget(self.ui_refs['auto_scroll_cb'])
        
        self.ui_refs['word_wrap_cb'] = ThemeManager.create_checkbox("Word wrap")
        self.ui_refs['word_wrap_cb'].setChecked(self.default_word_wrap)
        self.ui_refs['word_wrap_cb'].toggled.connect(self.toggle_word_wrap)
        display_layout.addWidget(self.ui_refs['word_wrap_cb'])
        
        self.ui_refs['timestamps_cb'] = ThemeManager.create_checkbox("Show timestamps")
        self.ui_refs['timestamps_cb'].setChecked(self.default_show_timestamps)
        self.ui_refs['timestamps_cb'].toggled.connect(self.toggle_timestamps)
        display_layout.addWidget(self.ui_refs['timestamps_cb'])
        
        # Font size controls
        font_label = QLabel("Font Size:")
        font_label.setStyleSheet(f"color: {AppColors.TEXT_DEFAULT}; font-weight: 500;")
        display_layout.addWidget(font_label)
        
        font_layout = QHBoxLayout()
        decrease_btn = ThemeManager.create_button("-", self.decrease_font_size, "compact")
        decrease_btn.setFixedWidth(32)
        font_layout.addWidget(decrease_btn)
        
        self.ui_refs['font_size_label'] = QLabel(f"{self.default_font_size}pt")
        self.ui_refs['font_size_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui_refs['font_size_label'].setStyleSheet(f"color: {AppColors.TEXT_DEFAULT};")
        font_layout.addWidget(self.ui_refs['font_size_label'])
        
        increase_btn = ThemeManager.create_button("+", self.increase_font_size, "compact")
        increase_btn.setFixedWidth(32)
        font_layout.addWidget(increase_btn)
        
        font_layout.addStretch()
        display_layout.addLayout(font_layout)
        
        settings_layout.addWidget(display_group)
        
        # Data Format Card
        format_group, format_layout = self._create_settings_card("Data Format")
        
        # Display mode radio buttons
        self.ui_refs['ascii_radio'] = QRadioButton("ASCII")
        self.ui_refs['ascii_radio'].setChecked(True)
        self.ui_refs['ascii_radio'].toggled.connect(lambda checked: self.set_display_mode("ascii" if checked else "hex"))
        format_layout.addWidget(self.ui_refs['ascii_radio'])
        
        self.ui_refs['hex_radio'] = QRadioButton("Hexadecimal")
        self.ui_refs['hex_radio'].setChecked(False)
        format_layout.addWidget(self.ui_refs['hex_radio'])
        
        # Encoding selection
        encoding_label = QLabel("Text Encoding:")
        encoding_label.setStyleSheet(f"color: {AppColors.TEXT_DEFAULT}; font-weight: 500;")
        format_layout.addWidget(encoding_label)
        
        self.ui_refs['encoding_combo'] = ThemeManager.create_combobox()
        self.ui_refs['encoding_combo'].addItems(["utf-8", "ascii", "latin-1", "cp1252"])
        self.ui_refs['encoding_combo'].setCurrentText(self.encoding)
        self.ui_refs['encoding_combo'].currentTextChanged.connect(self.change_encoding)
        format_layout.addWidget(self.ui_refs['encoding_combo'])
        
        settings_layout.addWidget(format_group)
        
        settings_layout.addStretch()
        
        scroll.setWidget(settings_widget)
        
        # Main panel layout
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll)
        
        return panel
    
    def _create_settings_card(self, title: str) -> tuple:
        """Create settings card matching main GUI pattern"""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: {AppFonts.BOLD_WEIGHT};
                color: {AppColors.TEXT_DEFAULT};
                border: 1px solid {AppColors.BORDER_LIGHT};
                border-radius: 4px;
                margin-top: 16px;
                padding-top: 8px;
                background-color: {AppColors.BACKGROUND_WHITE};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background-color: {AppColors.BACKGROUND_LIGHT};
                color: {AppColors.TEXT_DEFAULT};
            }}
        """)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 24, 12, 12)
        layout.setSpacing(12)
        
        return group, layout
    
    def _create_icon_button_group(self, buttons: List[ButtonConfig], 
                                  layout: QHBoxLayout) -> Dict[str, QPushButton]:
        """Create a group of Windows Explorer style compact buttons with SVG icons"""
        created_buttons = {}
        
        for config in buttons:
            btn = self._create_single_button(config)
            layout.addWidget(btn)
            
            if config.reference_name:
                created_buttons[config.reference_name] = btn
                
        return created_buttons
    
    def _create_single_button(self, config: ButtonConfig) -> QPushButton:
        """Create a single button with consistent styling"""
        btn = QPushButton()
        self._configure_button_size(btn)
        self._configure_button_content(btn, config)
        self._configure_button_style(btn, config.icon_name)
        
        btn.clicked.connect(config.callback)
        btn.setEnabled(config.enabled)
        return btn
    
    def _configure_button_size(self, btn: QPushButton):
        """Configure button size using theme dimensions"""
        btn.setMinimumWidth(AppDimensions.BUTTON_MIN_WIDTH)
        btn.setMaximumWidth(AppDimensions.BUTTON_MAX_WIDTH)
        btn.setMinimumHeight(AppDimensions.BUTTON_HEIGHT_CONTROL)
        btn.setMaximumHeight(AppDimensions.BUTTON_HEIGHT_CONTROL)
        btn.setFont(QFont(AppFonts.DEFAULT_FAMILY, AppFonts.FONT_SIZE_SMALL))
    
    def _configure_button_content(self, btn: QPushButton, config: ButtonConfig):
        """Configure button text, tooltip, and icon"""
        button_text = self.BUTTON_CONFIG['text'].get(config.icon_name, config.icon_name.title())
        btn.setText(button_text)
        btn.setToolTip(config.tooltip)
        
        # Add SVG icon if available
        svg_name = self.BUTTON_CONFIG['icons'].get(config.icon_name)
        if svg_name:
            self._add_button_icon(btn, svg_name)
    
    def _add_button_icon(self, btn: QPushButton, svg_name: str):
        """Add SVG icon to button"""
        try:
            icon_template = getattr(AppIcons, svg_name, None)
            if icon_template:
                icon_size = QSize(16, 16)
                icon = IconManager.create_svg_icon(icon_template, AppColors.ICON_DEFAULT, icon_size)
                btn.setIcon(icon)
                btn.setIconSize(icon_size)
        except Exception as e:
            print(f"Warning: Could not load icon {svg_name}: {e}")
    
    def _configure_button_style(self, btn: QPushButton, icon_name: str):
        """Apply appropriate styling based on button type"""
        if icon_name in self.BUTTON_CONFIG['primary_actions']:
            self._apply_primary_button_style(btn)
        else:
            self._apply_default_button_style(btn)
    
    def _apply_default_button_style(self, btn: QPushButton):
        """Apply default button styling"""
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.BUTTON_TRANSPARENT};
                border: 1px solid {AppColors.BUTTON_TRANSPARENT};
                padding: {AppDimensions.PADDING_BUTTON_DETAILED};
                text-align: left;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.FONT_SIZE_SMALL}pt;
                color: {AppColors.CONTROL_PANEL_TEXT};
                line-height: 1.2;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_BLUE_LIGHT};
                border-color: {AppColors.BUTTON_BLUE_BORDER};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_BLUE_BORDER};
                border-color: {AppColors.BUTTON_BLUE_BORDER_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {AppColors.BUTTON_TRANSPARENT};
                color: {AppColors.TEXT_DISABLED};
                border-color: {AppColors.BUTTON_TRANSPARENT};
            }}
        """)
    
    def _apply_primary_button_style(self, btn: QPushButton):
        """Apply primary button styling"""
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppColors.BUTTON_BLUE_LIGHT};
                border: 1px solid {AppColors.BUTTON_BLUE_BORDER};
                padding: {AppDimensions.PADDING_BUTTON_DETAILED};
                text-align: left;
                font-family: "Segoe UI";
                font-size: 8pt;
                color: {AppColors.BUTTON_ACCENT_TEXT};
                font-weight: normal;
                line-height: 1.2;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_BLUE_HOVER};
                border-color: {AppColors.BUTTON_BLUE_BORDER_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_BLUE_PRESSED};
                border-color: {AppColors.BUTTON_BLUE_BORDER_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {AppColors.GRAY_100};
                color: {AppColors.TEXT_DISABLED};
                border-color: {AppColors.BORDER_DISABLED};
            }}
        """)
    
    def _create_icon_button(self, icon_name: str, tooltip: str) -> QPushButton:
        """Create icon button matching main GUI pattern"""
        btn = QPushButton()
        btn.setFixedSize(28, 28)
        btn.setToolTip(tooltip)
        
        # Apply icon
        svg_name = self.BUTTON_CONFIG['icons'].get(icon_name)
        if svg_name:
            icon_template = getattr(AppIcons, svg_name, None)
            if icon_template:
                icon = IconManager.create_svg_icon(icon_template, AppColors.ICON_DEFAULT, QSize(16, 16))
                btn.setIcon(icon)
                btn.setIconSize(QSize(16, 16))
        
        # Apply icon button styling
        btn.setStyleSheet(AppStyles.icon_button())
        
        return btn
    
    def create_terminal_section(self) -> QWidget:
        """Create the terminal display section"""
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Terminal toolbar
        toolbar = self.create_terminal_toolbar()
        layout.addWidget(toolbar)
        
        # Terminal display area
        self.terminal_area = QWidget()
        self.terminal_area_layout = QVBoxLayout(self.terminal_area)
        self.terminal_area_layout.setContentsMargins(0, 0, 0, 0)
        self.terminal_area_layout.setSpacing(0)
        
        layout.addWidget(self.terminal_area)
        
        return container
    
    def create_terminal_toolbar(self) -> QWidget:
        """Create terminal toolbar matching main GUI style"""
        toolbar = QWidget()
        toolbar.setFixedHeight(40)
        toolbar.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border-bottom: 1px solid {AppColors.BORDER_LIGHT};
            }}
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)
        
        # Send to label
        send_label = QLabel("Send to Active:")
        send_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-size: {AppFonts.DEFAULT_SIZE};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        layout.addWidget(send_label)
        
        # Send data input
        self.ui_refs['send_input'] = ThemeManager.create_lineedit()
        self.ui_refs['send_input'].setPlaceholderText("Enter data to send...")
        self.ui_refs['send_input'].returnPressed.connect(self.send_data)
        layout.addWidget(self.ui_refs['send_input'])
        
        self.ui_refs['send_btn'] = ThemeManager.create_button(
            "Send",
            self.send_data,
            "compact",
            "primary"
        )
        layout.addWidget(self.ui_refs['send_btn'])
        
        layout.addStretch()
        
        return toolbar
    
    def create_status_bar(self) -> QWidget:
        """Create professional status bar matching main GUI"""
        status_bar = QWidget()
        status_bar.setFixedHeight(28)
        status_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border-top: 1px solid {AppColors.BORDER_LIGHT};
            }}
        """)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(16)
        
        # Active terminal info
        self.ui_refs['status_active_label'] = QLabel("Terminal 1: No connection")
        self.ui_refs['status_active_label'].setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-size: {AppFonts.SMALL_SIZE};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        layout.addWidget(self.ui_refs['status_active_label'])
        
        layout.addWidget(self._create_status_separator())
        
        # Total connections
        self.ui_refs['connections_count_label'] = QLabel("Connections: 0")
        self.ui_refs['connections_count_label'].setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-size: {AppFonts.SMALL_SIZE};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        layout.addWidget(self.ui_refs['connections_count_label'])
        
        layout.addStretch()
        
        # Terminal count
        self.ui_refs['terminal_count_label'] = QLabel("Terminals: 1")
        self.ui_refs['terminal_count_label'].setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-size: {AppFonts.SMALL_SIZE};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        layout.addWidget(self.ui_refs['terminal_count_label'])
        
        layout.addWidget(self._create_status_separator())
        
        # Total data
        self.ui_refs['total_data_label'] = QLabel("Total: 0 KB")
        self.ui_refs['total_data_label'].setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-size: {AppFonts.SMALL_SIZE};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        layout.addWidget(self.ui_refs['total_data_label'])
        
        return status_bar
    
    def _create_status_separator(self) -> QLabel:
        """Create a status bar separator"""
        sep = QLabel("•")
        sep.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-size: {AppFonts.SMALL_SIZE};
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        return sep
    
    # === UI Feedback Methods ===
    def _ui_feedback(self, message: str, title: str = None, msg_type: str = "status", component: str = None):
        """Unified UI feedback method matching main GUI"""
        if msg_type == "status":
            # Status update
            widget = None
            if component == "connection":
                widget = self.ui_refs.get('connection_status')
            elif component == "terminal":
                widget = self.ui_refs.get('terminal_status')
            else:
                widget = self.ui_refs.get('status_active_label')
            
            if widget:
                widget.setText(message)
        else:
            # Dark-themed message box
            return ThemeManager.create_dark_message_box(self, title or "Information", message, msg_type)
    
    def _update_status(self, message: str, component: str = None):
        """Update status label"""
        self._ui_feedback(message, component=component)
    
    # === Terminal Management Methods ===
    
    def _initialize_first_terminal(self):
        """Initialize the first terminal instance"""
        # Create first terminal
        terminal_widget = self._create_terminal_instance(1)
        self.terminal_widgets[1] = terminal_widget
        
        # Create formatter
        formatter = TerminalStreamFormatter()
        self.terminal_formatters[1] = formatter
        
        # Create connection
        connection = TerminalConnection(1)
        self.terminal_connections[1] = connection
        
        # Create buffer timer
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._flush_buffer(1))
        self.buffer_timers[1] = timer
        timer.start(100)
        
        # Initialize state
        self.terminal_states[1] = {
            'auto_scroll': self.default_auto_scroll,
            'word_wrap': self.default_word_wrap,
            'show_timestamps': self.default_show_timestamps,
            'font_size': self.default_font_size,
            'is_paused': False,
            'line_buffer': "",
            'display_mode': 'ascii',
            'selected_port': None,
            'selected_baud': "115200"
        }
        
        # Apply initial styling
        self._update_terminal_display_style(terminal_widget.terminal_display, 1)
        self._update_terminal_focus(1, True)
        
        # Add to layout
        self.terminal_area_layout.addWidget(terminal_widget)
    
    def _create_terminal_instance(self, terminal_id: int) -> TerminalInstanceWidget:
        """Create a single terminal instance"""
        terminal_widget = TerminalInstanceWidget(terminal_id)
        terminal_widget.terminal_focused.connect(self._handle_terminal_focus)
        return terminal_widget
    
    def _change_split_mode(self, new_mode: str):
        """Change the terminal split mode"""
        if new_mode == self.current_split_mode:
            return
        
        # Save current splitter state
        self._save_splitter_state()
        
        # Update mode
        old_mode = self.current_split_mode
        self.current_split_mode = new_mode
        
        # Create any needed terminal instances
        terminal_count = TerminalSplitMode.get_terminal_count(new_mode)
        for i in range(1, terminal_count + 1):
            if i not in self.terminal_widgets:
                # Create new terminal
                terminal_widget = self._create_terminal_instance(i)
                self.terminal_widgets[i] = terminal_widget
                
                # Create formatter
                formatter = TerminalStreamFormatter()
                self.terminal_formatters[i] = formatter
                
                # Create connection
                connection = TerminalConnection(i)
                self.terminal_connections[i] = connection
                
                # Create buffer timer
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(lambda tid=i: self._flush_buffer(tid))
                self.buffer_timers[i] = timer
                timer.start(100)
                
                # Initialize state
                self.terminal_states[i] = {
                    'auto_scroll': self.default_auto_scroll,
                    'word_wrap': self.default_word_wrap,
                    'show_timestamps': self.default_show_timestamps,
                    'font_size': self.default_font_size,
                    'is_paused': False,
                    'line_buffer': "",
                    'display_mode': 'ascii' if self.ui_refs['ascii_radio'].isChecked() else 'hex',
                    'selected_port': None,
                    'selected_baud': "115200"
                }
                
                # Apply styling
                self._update_terminal_display_style(terminal_widget.terminal_display, i)
        
        # Setup new layout
        self._setup_split_layout(new_mode)
        
        # Update UI
        self.terminal_info_label.setText(f"{terminal_count} Terminal{'s' if terminal_count > 1 else ''}")
        self.ui_refs['terminal_count_label'].setText(f"Terminals: {terminal_count}")
        self._update_terminal_info()
        self._update_connection_count()
    
    def _setup_split_layout(self, mode: str):
        """Configure the terminal layout for the specified split mode"""
        # Clear current layout
        while self.terminal_area_layout.count():
            item = self.terminal_area_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Hide all terminals first
        for widget in self.terminal_widgets.values():
            widget.hide()
        
        if mode == TerminalSplitMode.NONE:
            # Single terminal
            self.terminal_widgets[1].show()
            self.terminal_area_layout.addWidget(self.terminal_widgets[1])
            
        elif mode == TerminalSplitMode.HORIZONTAL:
            # Horizontal split
            self.main_splitter = ThemeManager.create_splitter(Qt.Orientation.Vertical)
            self.main_splitter.addWidget(self.terminal_widgets[1])
            self.main_splitter.addWidget(self.terminal_widgets[2])
            self.terminal_widgets[1].show()
            self.terminal_widgets[2].show()
            self.terminal_area_layout.addWidget(self.main_splitter)
            self._restore_splitter_state()
            
        elif mode == TerminalSplitMode.THREE_WAY:
            # Three-way split
            self.main_splitter = ThemeManager.create_splitter(Qt.Orientation.Vertical)
            top_splitter = ThemeManager.create_splitter(Qt.Orientation.Horizontal)
            
            top_splitter.addWidget(self.terminal_widgets[1])
            top_splitter.addWidget(self.terminal_widgets[2])
            self.main_splitter.addWidget(top_splitter)
            self.main_splitter.addWidget(self.terminal_widgets[3])
            
            self.terminal_widgets[1].show()
            self.terminal_widgets[2].show()
            self.terminal_widgets[3].show()
            
            self.terminal_area_layout.addWidget(self.main_splitter)
            self._restore_splitter_state()
            
        elif mode == TerminalSplitMode.GRID:
            # Grid split (2x2)
            self.main_splitter = ThemeManager.create_splitter(Qt.Orientation.Vertical)
            top_splitter = ThemeManager.create_splitter(Qt.Orientation.Horizontal)
            bottom_splitter = ThemeManager.create_splitter(Qt.Orientation.Horizontal)
            
            top_splitter.addWidget(self.terminal_widgets[1])
            top_splitter.addWidget(self.terminal_widgets[2])
            bottom_splitter.addWidget(self.terminal_widgets[3])
            bottom_splitter.addWidget(self.terminal_widgets[4])
            
            self.main_splitter.addWidget(top_splitter)
            self.main_splitter.addWidget(bottom_splitter)
            
            self.terminal_widgets[1].show()
            self.terminal_widgets[2].show()
            self.terminal_widgets[3].show()
            self.terminal_widgets[4].show()
            
            self.terminal_area_layout.addWidget(self.main_splitter)
            self._restore_splitter_state()
    
    def _save_splitter_state(self):
        """Save current splitter positions"""
        # Implementation remains the same
        pass
    
    def _restore_splitter_state(self):
        """Restore splitter positions for current mode"""
        # Implementation remains the same
        pass
    
    def _handle_terminal_focus(self, terminal_id: int):
        """Handle terminal focus changes"""
        old_active = self.active_terminal_id
        self.active_terminal_id = terminal_id
        
        # Update visual indicators
        if old_active in self.terminal_widgets:
            self._update_terminal_focus(old_active, False)
        
        self._update_terminal_focus(terminal_id, True)
        
        # Update active terminal label
        self.ui_refs['active_terminal_label'].setText(f"Terminal {terminal_id}")
        
        # Update connection settings to reflect active terminal
        self._update_settings_for_terminal(terminal_id)
        
        # Update status bar
        self._update_status_bar()
        
        # Update send button state
        connection = self.terminal_connections[terminal_id]
        self.ui_refs['send_btn'].setEnabled(connection.is_connected)
        self.ui_refs['send_input'].setEnabled(connection.is_connected)
    
    def _update_terminal_focus(self, terminal_id: int, focused: bool):
        """Update terminal visual focus state"""
        if terminal_id in self.terminal_widgets:
            self.terminal_widgets[terminal_id].set_focused(focused)
    
    def _update_settings_for_terminal(self, terminal_id: int):
        """Update settings panel to reflect the specified terminal's state"""
        state = self.terminal_states.get(terminal_id, {})
        connection = self.terminal_connections.get(terminal_id)
        
        # Update connection settings
        if connection:
            # Block signals to prevent triggering changes
            self.ui_refs['port_combo'].blockSignals(True)
            self.ui_refs['baud_combo'].blockSignals(True)
            
            # Update port selection
            if state.get('selected_port'):
                index = self.ui_refs['port_combo'].findData(state['selected_port'])
                if index >= 0:
                    self.ui_refs['port_combo'].setCurrentIndex(index)
            else:
                self.ui_refs['port_combo'].setCurrentIndex(0)
            
            # Update baud rate
            self.ui_refs['baud_combo'].setCurrentText(state.get('selected_baud', "115200"))
            
            # Update connect button
            if connection.is_connected:
                self.ui_refs['connect_btn'].setEnabled(False)
                self.ui_refs['disconnect_btn'].setEnabled(True)
            else:
                self.ui_refs['connect_btn'].setEnabled(True)
                self.ui_refs['disconnect_btn'].setEnabled(False)
            
            # Re-enable signals
            self.ui_refs['port_combo'].blockSignals(False)
            self.ui_refs['baud_combo'].blockSignals(False)
        
        # Update display settings
        self.ui_refs['auto_scroll_cb'].setChecked(state.get('auto_scroll', True))
        self.ui_refs['word_wrap_cb'].setChecked(state.get('word_wrap', False))
        self.ui_refs['timestamps_cb'].setChecked(state.get('show_timestamps', True))
        
        # Update font size
        font_size = state.get('font_size', self.default_font_size)
        self.ui_refs['font_size_label'].setText(f"{font_size}pt")
        
        # Update display mode
        display_mode = state.get('display_mode', 'ascii')
        if display_mode == 'ascii':
            self.ui_refs['ascii_radio'].setChecked(True)
        else:
            self.ui_refs['hex_radio'].setChecked(True)
    
    def _get_visible_terminal_ids(self) -> List[int]:
        """Get list of currently visible terminal IDs"""
        count = TerminalSplitMode.get_terminal_count(self.current_split_mode)
        return list(range(1, count + 1))
    
    def _update_terminal_info(self):
        """Update terminal info label"""
        visible_count = len(self._get_visible_terminal_ids())
        connected_count = sum(1 for tid in self._get_visible_terminal_ids() 
                            if self.terminal_connections[tid].is_connected)
        
        if connected_count > 0:
            self._update_status(f"Connected: {connected_count}/{visible_count}", "terminal")
        else:
            self._update_status("Ready", "terminal")
    
    def _update_connection_count(self):
        """Update total connections count"""
        connected_count = sum(1 for conn in self.terminal_connections.values() 
                            if conn.is_connected)
        self.ui_refs['connections_count_label'].setText(f"Connections: {connected_count}")
    
    def _update_status_bar(self):
        """Update status bar with active terminal info"""
        connection = self.terminal_connections[self.active_terminal_id]
        
        if connection.is_connected:
            port_name = connection.port_info.port_name if connection.port_info else "Unknown"
            self.ui_refs['status_active_label'].setText(
                f"Terminal {self.active_terminal_id}: {port_name} @ {connection.baud_rate} baud"
            )
            self.ui_refs['status_active_label'].setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DEFAULT};
                    font-size: {AppFonts.SMALL_SIZE};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                }}
            """)
        else:
            self.ui_refs['status_active_label'].setText(f"Terminal {self.active_terminal_id}: No connection")
            self.ui_refs['status_active_label'].setStyleSheet(f"""
                QLabel {{
                    color: {AppColors.TEXT_DISABLED};
                    font-size: {AppFonts.SMALL_SIZE};
                    font-family: {AppFonts.DEFAULT_FAMILY};
                }}
            """)
        
        # Update total data
        total_rx = sum(conn.bytes_received for conn in self.terminal_connections.values()) / 1024
        total_tx = sum(conn.bytes_sent for conn in self.terminal_connections.values()) / 1024
        self.ui_refs['total_data_label'].setText(f"Total: ↓{total_rx:.1f} KB ↑{total_tx:.1f} KB")
    
    # === Connection Management Methods ===
    
    def _on_port_selection_changed(self, index: int):
        """Handle port selection change for active terminal"""
        if self.active_terminal_id in self.terminal_states:
            self.terminal_states[self.active_terminal_id]['selected_port'] = self.ui_refs['port_combo'].currentData()
    
    def _on_baud_rate_changed(self, baud: str):
        """Handle baud rate change for active terminal"""
        if self.active_terminal_id in self.terminal_states:
            self.terminal_states[self.active_terminal_id]['selected_baud'] = baud
    
    def toggle_connection(self):
        """Toggle connection for active terminal"""
        connection = self.terminal_connections[self.active_terminal_id]
        
        if connection.is_connected:
            self.disconnect_terminal(self.active_terminal_id)
        else:
            self.connect_terminal(self.active_terminal_id)
    
    def connect_terminal(self, terminal_id: int):
        """Connect a specific terminal"""
        state = self.terminal_states[terminal_id]
        connection = self.terminal_connections[terminal_id]
        
        # Get selected port
        port_data = state.get('selected_port')
        if not port_data:
            port_data = self.ui_refs['port_combo'].currentData()
            state['selected_port'] = port_data
        
        if port_data is None:
            return
        
        # Find port info
        port_info = next((p for p in self.available_ports if p.port_name == port_data), None)
        if not port_info:
            # Create minimal port info
            from core.core import SerialPortInfo
            port_info = SerialPortInfo(port_data, f"Port {port_data}", "Unknown")
        
        connection.port_info = port_info
        connection.baud_rate = int(state.get('selected_baud', "115200"))
        
        # Update terminal status
        widget = self.terminal_widgets[terminal_id]
        widget.update_connection_status(False, f"Connecting to {connection.port_info.port_name}...")
        
        # Create and start monitor
        connection.port_monitor = SerialPortMonitor(connection.port_info.port_name, connection.baud_rate)
        connection.port_monitor.data_received.connect(
            lambda data, tid=terminal_id: self._handle_incoming_data(tid, data)
        )
        connection.port_monitor.error_occurred.connect(
            lambda error, tid=terminal_id: self._handle_monitor_error(tid, error)
        )
        
        if not connection.port_monitor.start_monitoring():
            connection.port_monitor = None
            widget.update_connection_status(False)
            return
        
        # Update connection state
        connection.is_connected = True
        connection.bytes_sent = 0
        connection.bytes_received = 0
        
        # Update UI
        widget.update_connection_status(True, f"{connection.port_info.port_name} @ {connection.baud_rate}")
        
        # If this is the active terminal, update controls
        if terminal_id == self.active_terminal_id:
            self.ui_refs['connect_btn'].setEnabled(False)
            self.ui_refs['disconnect_btn'].setEnabled(True)
            self.ui_refs['send_btn'].setEnabled(True)
            self.ui_refs['send_input'].setEnabled(True)
        
        # Show connection message
        formatter = self.terminal_formatters[terminal_id]
        terminal_display = widget.terminal_display
        formatter.format_connection_start(terminal_display, connection.port_info.port_name, connection.baud_rate)
        
        # Update status displays
        self._update_terminal_info()
        self._update_connection_count()
        self._update_status_bar()
        self._update_status("Connected", "connection")
    
    def disconnect_terminal(self, terminal_id: int):
        """Disconnect a specific terminal"""
        connection = self.terminal_connections[terminal_id]
        widget = self.terminal_widgets[terminal_id]
        
        if connection.port_monitor:
            connection.port_monitor.stop_monitoring()
            connection.port_monitor = None
        
        # Show disconnection message
        if connection.port_info:
            formatter = self.terminal_formatters[terminal_id]
            terminal_display = widget.terminal_display
            formatter.format_connection_end(terminal_display, connection.port_info.port_name)
        
        # Update connection state
        connection.is_connected = False
        
        # Update UI
        widget.update_connection_status(False)
        
        # If this is the active terminal, update controls
        if terminal_id == self.active_terminal_id:
            self.ui_refs['connect_btn'].setEnabled(True)
            self.ui_refs['disconnect_btn'].setEnabled(False)
            self.ui_refs['send_btn'].setEnabled(False)
            self.ui_refs['send_input'].setEnabled(False)
        
        # Update status displays
        self._update_terminal_info()
        self._update_connection_count()
        self._update_status_bar()
        self._update_status("Disconnected", "connection")
    
    # === Data Handling Methods ===
    
    def _handle_incoming_data(self, terminal_id: int, data: bytes):
        """Handle incoming serial data for a specific terminal"""
        connection = self.terminal_connections[terminal_id]
        widget = self.terminal_widgets[terminal_id]
        
        # Update statistics
        connection.bytes_received += len(data)
        
        # Skip if terminal is paused
        if widget.is_paused:
            return
        
        # Get terminal state
        state = self.terminal_states[terminal_id]
        formatter = self.terminal_formatters[terminal_id]
        terminal_display = widget.terminal_display
        
        try:
            if state['display_mode'] == 'hex':
                # Display raw hex data
                hex_data = ' '.join(f'{b:02X}' for b in data)
                ascii_data = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
                formatted_data = f"HEX: {hex_data} | ASCII: {ascii_data}"
                
                formatter.append_data(
                    terminal_display,
                    formatted_data,
                    "incoming",
                    show_timestamp=state['show_timestamps']
                )
                return
            
            # Decode bytes
            try:
                text_data = data.decode(self.encoding)
            except UnicodeDecodeError:
                text_data = data.decode(self.encoding, errors='replace')
            
            # Normalize line endings
            text_data = text_data.replace('\r\n', '\n').replace('\r', '\n')
            
            # Add to line buffer
            state['line_buffer'] += text_data
            
            # Process complete lines
            lines = state['line_buffer'].split('\n')
            
            # Display all complete lines
            for line in lines[:-1]:
                if line:  # Only display non-empty lines
                    formatter.append_data(
                        terminal_display,
                        line,
                        "incoming",
                        show_timestamp=state['show_timestamps']
                    )
            
            # Keep the last (potentially incomplete) line
            state['line_buffer'] = lines[-1]
                
        except Exception as e:
            formatter.append_status(
                terminal_display,
                f"Data processing error: {str(e)}",
                "error"
            )
        
        # Update status bar if this is active terminal
        if terminal_id == self.active_terminal_id:
            self._update_status_bar()
    
    def _flush_buffer(self, terminal_id: int):
        """Flush remaining data in buffer for specified terminal"""
        if terminal_id not in self.terminal_states:
            return
            
        state = self.terminal_states[terminal_id]
        if state['line_buffer'] and terminal_id in self.terminal_widgets:
            formatter = self.terminal_formatters[terminal_id]
            terminal_display = self.terminal_widgets[terminal_id].terminal_display
            
            formatter.append_data(
                terminal_display,
                state['line_buffer'],
                "incoming",
                show_timestamp=state['show_timestamps']
            )
            state['line_buffer'] = ""
        
        # Restart timer
        if terminal_id in self.buffer_timers:
            self.buffer_timers[terminal_id].start(100)
    
    def _handle_monitor_error(self, terminal_id: int, error: str):
        """Handle monitor errors for specific terminal"""
        if terminal_id in self.terminal_formatters and terminal_id in self.terminal_widgets:
            formatter = self.terminal_formatters[terminal_id]
            terminal_display = self.terminal_widgets[terminal_id].terminal_display
            formatter.append_data(terminal_display, f"Error: {error}\n", "error")
    
    def send_data(self):
        """Send data to active terminal's serial port"""
        connection = self.terminal_connections[self.active_terminal_id]
        
        if not connection.is_connected or not connection.port_monitor:
            return
            
        data = self.ui_refs['send_input'].text()
        if not data:
            return
            
        try:
            # Add line ending if needed
            if not data.endswith('\n'):
                data += '\n'
                
            # Send data
            if connection.port_monitor.send_data(data.encode(self.encoding)):
                connection.bytes_sent += len(data.encode(self.encoding))
                
                # Show in terminal
                formatter = self.terminal_formatters[self.active_terminal_id]
                terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
                state = self.terminal_states[self.active_terminal_id]
                
                formatter.append_data(
                    terminal_display,
                    data.strip(),
                    "outgoing",
                    show_timestamp=state['show_timestamps']
                )
                
                self.ui_refs['send_input'].clear()
                self._update_status_bar()
            else:
                # Show error
                formatter = self.terminal_formatters[self.active_terminal_id]
                terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
                formatter.append_status(
                    terminal_display,
                    "Failed to send data",
                    "error"
                )
                
        except Exception as e:
            # Show error
            formatter = self.terminal_formatters[self.active_terminal_id]
            terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
            formatter.append_status(
                terminal_display,
                f"Send error: {str(e)}",
                "error"
            )
    
    # === Terminal Control Methods ===
    
    def clear_all_terminals(self):
        """Clear all terminal displays"""
        for terminal_id in self._get_visible_terminal_ids():
            if terminal_id in self.terminal_widgets:
                widget = self.terminal_widgets[terminal_id]
                widget.clear_terminal()
                
                formatter = self.terminal_formatters[terminal_id]
                formatter.clear(widget.terminal_display)
                
                self.terminal_states[terminal_id]['line_buffer'] = ""
    
    # === Settings Update Methods ===
    
    def toggle_auto_scroll(self, checked: bool):
        """Toggle auto-scroll setting for active terminal"""
        if self.active_terminal_id in self.terminal_states:
            self.terminal_states[self.active_terminal_id]['auto_scroll'] = checked
            formatter = self.terminal_formatters[self.active_terminal_id]
            formatter.set_auto_scroll_enabled(checked)
            
            if checked:
                terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
                formatter.force_scroll_to_bottom(terminal_display)
    
    def toggle_word_wrap(self, checked: bool):
        """Toggle word wrap setting for active terminal"""
        if self.active_terminal_id in self.terminal_states:
            self.terminal_states[self.active_terminal_id]['word_wrap'] = checked
            terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
            self._update_terminal_display_style(terminal_display, self.active_terminal_id)
    
    def toggle_timestamps(self, checked: bool):
        """Toggle timestamp display for active terminal"""
        if self.active_terminal_id in self.terminal_states:
            self.terminal_states[self.active_terminal_id]['show_timestamps'] = checked
    
    def set_display_mode(self, mode: str):
        """Set display mode (ascii/hex) for active terminal"""
        if self.active_terminal_id in self.terminal_states:
            self.terminal_states[self.active_terminal_id]['display_mode'] = mode
            
            # Show status message
            formatter = self.terminal_formatters[self.active_terminal_id]
            terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
            status_msg = f"{mode.upper()} display mode enabled"
            formatter.append_status(terminal_display, status_msg, "status")
    
    def change_encoding(self, encoding: str):
        """Change text encoding (affects all terminals)"""
        self.encoding = encoding
        
        # Show in active terminal
        formatter = self.terminal_formatters[self.active_terminal_id]
        terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
        formatter.append_status(
            terminal_display,
            f"Encoding changed to {encoding}",
            "status"
        )
    
    def increase_font_size(self):
        """Increase terminal font size for active terminal"""
        if self.active_terminal_id in self.terminal_states:
            current_size = self.terminal_states[self.active_terminal_id]['font_size']
            if current_size < 24:
                new_size = current_size + 1
                self.terminal_states[self.active_terminal_id]['font_size'] = new_size
                self.ui_refs['font_size_label'].setText(f"{new_size}pt")
                
                terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
                self._update_terminal_display_style(terminal_display, self.active_terminal_id)
    
    def decrease_font_size(self):
        """Decrease terminal font size for active terminal"""
        if self.active_terminal_id in self.terminal_states:
            current_size = self.terminal_states[self.active_terminal_id]['font_size']
            if current_size > 8:
                new_size = current_size - 1
                self.terminal_states[self.active_terminal_id]['font_size'] = new_size
                self.ui_refs['font_size_label'].setText(f"{new_size}pt")
                
                terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
                self._update_terminal_display_style(terminal_display, self.active_terminal_id)
    
    def _update_terminal_display_style(self, terminal_widget, terminal_id: int):
        """Update terminal display style with current settings"""
        if terminal_id in self.terminal_states:
            state = self.terminal_states[terminal_id]
            font_size = state['font_size']
            word_wrap = state['word_wrap']
        else:
            font_size = self.default_font_size
            word_wrap = self.default_word_wrap
            
        font = QFont(AppFonts.CONSOLE_FAMILY.split(',')[0], font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        terminal_widget.setFont(font)
        
        # Apply professional terminal styling
        terminal_widget.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppColors.BACKGROUND_WHITE};
                color: {AppColors.TEXT_DEFAULT};
                border: none;
                selection-background-color: {AppColors.SELECTION_BG};
                selection-color: {AppColors.SELECTION_TEXT};
                padding: 12px;
            }}
            {AppStyles.scrollbar()}
        """)
        
        if word_wrap:
            terminal_widget.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            terminal_widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    
    # === Other Methods ===
    
    def export_terminal_content(self):
        """Export terminal content to file"""
        # Check if multiple terminals
        visible_terminals = self._get_visible_terminal_ids()
        
        if len(visible_terminals) > 1:
            # Ask user which terminals to export
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Export Options")
            msg_box.setText("Export terminal content")
            msg_box.setInformativeText("Which terminal(s) would you like to export?")
            
            active_btn = msg_box.addButton(f"Active Terminal ({self.active_terminal_id})", QMessageBox.ButtonRole.ActionRole)
            all_btn = msg_box.addButton("All Terminals", QMessageBox.ButtonRole.ActionRole)
            cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == cancel_btn:
                return
            elif msg_box.clickedButton() == active_btn:
                terminal_ids = [self.active_terminal_id]
            else:
                terminal_ids = visible_terminals
        else:
            terminal_ids = [1]
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Terminal Content",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for terminal_id in terminal_ids:
                        if terminal_id in self.terminal_widgets:
                            terminal_display = self.terminal_widgets[terminal_id].terminal_display
                            connection = self.terminal_connections[terminal_id]
                            
                            if len(terminal_ids) > 1:
                                f.write(f"{'='*60}\n")
                                f.write(f"Terminal {terminal_id}")
                                if connection.is_connected and connection.port_info:
                                    f.write(f" - {connection.port_info.port_name} @ {connection.baud_rate} baud")
                                f.write(f"\n{'='*60}\n\n")
                            
                            f.write(terminal_display.toPlainText())
                            
                            if len(terminal_ids) > 1:
                                f.write("\n\n")
                
                # Show success in active terminal
                formatter = self.terminal_formatters[self.active_terminal_id]
                terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
                formatter.append_status(
                    terminal_display,
                    f"Content exported to {filename}",
                    "status"
                )
            except Exception as e:
                formatter = self.terminal_formatters[self.active_terminal_id]
                terminal_display = self.terminal_widgets[self.active_terminal_id].terminal_display
                formatter.append_status(
                    terminal_display,
                    f"Export failed: {str(e)}",
                    "error"
                )
    
    def toggle_settings_panel(self):
        """Toggle settings panel visibility"""
        self.show_settings_panel = not self.show_settings_panel
        
        if self.show_settings_panel:
            self.settings_panel.show()
            self.splitter.setSizes([320, 880])
            self.ui_refs['settings_toggle_btn'].setText("Hide Settings")
        else:
            self.settings_panel.hide()
            self.ui_refs['settings_toggle_btn'].setText("Show Settings")
    
    def refresh_ports(self):
        """Refresh available COM ports"""
        self.available_ports = []
        
        if WINREG_AVAILABLE:
            try:
                scanner = PortScanner()
                ports = scanner.scan_registry_ports()
                self.available_ports = ports
            except Exception as e:
                print(f"Error scanning ports: {e}")
        
        # Save current selection
        current_data = self.ui_refs['port_combo'].currentData()
        
        # Update port combo
        self.ui_refs['port_combo'].clear()
        if self.available_ports:
            for port in self.available_ports:
                self.ui_refs['port_combo'].addItem(port.port_name, port.port_name)
            
            # Try to restore selection
            if current_data:
                index = self.ui_refs['port_combo'].findData(current_data)
                if index >= 0:
                    self.ui_refs['port_combo'].setCurrentIndex(index)
        else:
            self.ui_refs['port_combo'].addItem("No COM ports found", None)
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        # Disconnect all terminals
        for terminal_id, connection in self.terminal_connections.items():
            if connection.is_connected:
                self.disconnect_terminal(terminal_id)
        
        # Stop all timers
        for timer in self.buffer_timers.values():
            timer.stop()
        
        super().closeEvent(event)