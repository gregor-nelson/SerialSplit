#!/usr/bin/env python3
"""
Main GUI window for Hub4com GUI Launcher
Contains the primary application interface - Fully themed version
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Callable
from functools import partial

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QComboBox, QPushButton, QCheckBox, 
                             QTextEdit, QFileDialog, QGroupBox, QGridLayout,
                             QMessageBox, QProgressBar, QFrame, QSplitter,
                             QTabWidget, QScrollArea, QListWidget, QListWidgetItem, 
                             QAbstractItemView, QMenu, QDialog)
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QAction

from core.components import (
    ResponsiveWindowManager, SerialPortInfo, PortScanner, Hub4comProcess,
    WINREG_AVAILABLE, PortConfig, Com0comProcess
)
from ui.theme.theme import (
    ThemeManager, AppStyles, AppFonts, AppDimensions, AppColors, 
    AppMessages, IconManager
)
from ui.dialogs import PortScanDialog, Com0ComHelpDialog, PairCreationDialog
from ui.widgets import OutputPortWidget


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Application configuration constants"""
    BAUD_RATES = ["1200", "2400", "4800", "9600", "14400", "19200", 
                  "38400", "57600", "115200", "230400", "460800", "921600"]
    QUICK_BAUD_RATES = ["9600", "19200", "38400", "57600", "115200"]
    DEFAULT_BAUD = "115200"
    MIN_OUTPUT_PORTS = 1


# ============================================================================
# MAIN GUI CLASS
# ============================================================================

class Hub4comGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hub4com_process = None
        self.port_scanner_thread = None
        self.scanned_ports = []
        self.output_port_widgets = []
        self.com0com_thread = None
        self.com0com_threads = []
        self.pending_modifications = 0
        self.modification_success = True
        
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
        layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        margins = ThemeManager.get_standard_margins()
        layout.setContentsMargins(*margins)
        
        # Add sections
        self._add_separator(layout)
        layout.addWidget(self._create_virtual_ports_section())
        layout.addWidget(self._create_configuration_section())
        layout.addLayout(self._create_control_buttons())
        layout.addWidget(self._create_output_section())
    
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
        QTimer.singleShot(50, self.update_route_mode_button)
        QTimer.singleShot(100, self.update_preview)
        QTimer.singleShot(1000, self._safe_refresh_ports)
        QTimer.singleShot(1500, self.add_output_port)
        QTimer.singleShot(2000, self.list_com0com_pairs)
    
    # ========================================================================
    # UI HELPER METHODS
    # ========================================================================
    
    def _create_groupbox_with_layout(self, title: str, layout_class=QVBoxLayout) -> tuple:
        """Create a styled groupbox with layout"""
        group = ThemeManager.create_groupbox(title)
        layout = layout_class(group) if layout_class else None
        if layout:
            layout.setSpacing(AppDimensions.SPACING_MEDIUM)
            margins = ThemeManager.get_standard_margins()
            layout.setContentsMargins(*margins)
        return group, layout
    
    def _add_separator(self, layout: QVBoxLayout):
        """Add a horizontal separator to layout"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_LIGHT};
                background-color: {AppColors.BORDER_LIGHT};
                max-height: 1px;
            }}
        """)
        layout.addWidget(line)
    
    def _show_message(self, title: str, message: str, msg_type: str = "info"):
        """Show message box with specified type"""
        msg_funcs = {
            "info": QMessageBox.information,
            "warning": QMessageBox.warning,
            "error": QMessageBox.critical,
            "question": QMessageBox.question
        }
        return msg_funcs.get(msg_type, QMessageBox.information)(self, title, message)
    
    def _update_status(self, message: str, widget: QLabel = None):
        """Update status label"""
        if not widget:
            widget = getattr(self, 'status_label', None)
        if widget:
            widget.setText(message)
    
    # ========================================================================
    # UI SECTION BUILDERS
    # ========================================================================
    
    def _create_virtual_ports_section(self) -> QGroupBox:
        """Create virtual ports management section"""
        group, layout = self._create_groupbox_with_layout(
            "Com0com Configuration"
        )
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        # Action buttons (refresh/create)
        action_buttons = [
            ("refresh", self.list_com0com_pairs, "Refresh port pairs list", True),
            ("create", self.create_com0com_pair, "Create new virtual port pair", True)
        ]
        
        for icon_name, callback, tooltip, enabled in action_buttons:
            btn = ThemeManager.create_icon_button(icon_name, tooltip, "medium")
            btn.clicked.connect(callback)
            btn.setEnabled(enabled)
            buttons_layout.addWidget(btn)
        
        # Vertical separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BORDER_DEFAULT};
                max-width: 1px;
                margin: {AppDimensions.PADDING_SMALL} {AppDimensions.PADDING_MEDIUM};
            }}
        """)
        buttons_layout.addWidget(separator)
        
        # Management buttons (delete/settings/help)
        management_buttons = [
            ("delete", self.remove_com0com_pair, "Delete selected pair", False),
            ("settings", self.show_settings_menu, "Configure selected pair", False),
            ("help", self.show_com0com_help, "Help and documentation", True)
        ]
        
        for icon_name, callback, tooltip, enabled in management_buttons:
            btn = ThemeManager.create_icon_button(icon_name, tooltip, "medium")
            btn.clicked.connect(callback)
            btn.setEnabled(enabled)
            buttons_layout.addWidget(btn)
            
            # Store references for buttons we need to access later
            if icon_name == "delete":
                self.remove_pair_btn = btn
            elif icon_name == "settings":
                self.settings_btn = btn
        
        # Status label (inline with control buttons, matching hub4com style)
        self.com0com_status = ThemeManager.create_label(AppMessages.READY, "status")
        self.com0com_status.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-style: italic;
                margin-left: {AppDimensions.PADDING_MEDIUM};
            }}
        """)
        buttons_layout.addWidget(self.com0com_status)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Port pairs list
        self.port_pairs_list = ThemeManager.create_listwidget()
        self.port_pairs_list.setMaximumHeight(AppDimensions.HEIGHT_LIST_LARGE)
        self.port_pairs_list.itemSelectionChanged.connect(self.on_pair_selected)
        self.port_pairs_list.itemDoubleClicked.connect(self.on_pair_double_clicked)
        layout.addWidget(self.port_pairs_list)
        
        self.com0com_progress = ThemeManager.create_progress_bar()
        self.com0com_progress.setRange(0, 100)
        self.com0com_progress.setVisible(False)
        layout.addWidget(self.com0com_progress)
        
        return group
    
    def _create_configuration_section(self) -> QGroupBox:
        """Create hub4com configuration section"""
        group, layout = self._create_groupbox_with_layout("Hub4com Configuration", QGridLayout)
        
        # Unified control bar - all hub4com controls in one row
        controls_layout = QHBoxLayout()
        
        # Port scanning buttons
        scan_buttons = [
            ("list", self.show_port_scanner, "Scan ports for detailed analysis", True),
            ("refresh", self.refresh_port_lists, "Refresh port lists", True)
        ]
        
        for icon_name, callback, tooltip, enabled in scan_buttons:
            btn = ThemeManager.create_icon_button(icon_name, tooltip, "medium")
            btn.clicked.connect(callback)
            btn.setEnabled(enabled)
            controls_layout.addWidget(btn)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        separator1.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BORDER_DEFAULT};
                max-width: 1px;
                margin: {AppDimensions.PADDING_SMALL} {AppDimensions.PADDING_MEDIUM};
            }}
        """)
        controls_layout.addWidget(separator1)
        
        # Port management buttons
        port_buttons = [
            ("create", self.add_output_port, "Add new output port", True),
            ("delete", self.remove_all_output_ports, "Remove all output ports", True)
        ]
        
        for icon_name, callback, tooltip, enabled in port_buttons:
            btn = ThemeManager.create_icon_button(icon_name, tooltip, "medium")
            btn.clicked.connect(callback)
            btn.setEnabled(enabled)
            controls_layout.addWidget(btn)
            
            # Store reference for remove all button
            if icon_name == "delete":
                self.remove_all_ports_btn = btn
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BORDER_DEFAULT};
                max-width: 1px;
                margin: {AppDimensions.PADDING_SMALL} {AppDimensions.PADDING_MEDIUM};
            }}
        """)
        controls_layout.addWidget(separator2)
        
        # Configuration checkboxes
        self.disable_cts = ThemeManager.create_checkbox("Disable CTS Handshaking")
        self.disable_cts.setChecked(True)
        self.disable_cts.stateChanged.connect(self.update_preview)
        self.disable_cts.setToolTip("Recommended for real COM ports - disables hardware handshaking")
        controls_layout.addWidget(self.disable_cts)
        
        self.sync_baud_rates = ThemeManager.create_checkbox("Sync Baud Rates")
        self.sync_baud_rates.stateChanged.connect(self.on_sync_baud_rates_changed)
        self.sync_baud_rates.setToolTip("Set all ports to the same baud rate automatically")
        controls_layout.addWidget(self.sync_baud_rates)
        
        # Route mode dropdown
        self.route_mode_btn = ThemeManager.create_button("Route Mode ▼", self.show_route_options_menu)
        self.route_mode_btn.setToolTip("Configure data routing between ports")
        controls_layout.addWidget(self.route_mode_btn)
        
        # Initialize route settings
        self.route_settings = {
            'mode': 'one_way',  # one_way, two_way, full_network
            'echo_enabled': False,
            'flow_control_enabled': False,
            'disable_default_fc': False
        }
        
        # Separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.VLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        separator3.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BORDER_DEFAULT};
                max-width: 1px;
                margin: {AppDimensions.PADDING_SMALL} {AppDimensions.PADDING_MEDIUM};
            }}
        """)
        controls_layout.addWidget(separator3)
        
        # Quick baud rate buttons
        baud_label = ThemeManager.create_label("Set All:")
        baud_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-weight: bold;
                margin-right: {AppDimensions.SPACING_SMALL};
            }}
        """)
        controls_layout.addWidget(baud_label)
        
        for rate in Config.QUICK_BAUD_RATES:
            btn = ThemeManager.create_button(rate, lambda checked, r=rate: self.set_all_baud_rates(r), "compact")
            btn.setFixedWidth(50)
            btn.setToolTip(f"Set all ports to {rate} baud")
            controls_layout.addWidget(btn)
        
        # Status label
        self.port_status_label = ThemeManager.create_label(AppMessages.SCANNING)
        self.port_status_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-style: italic;
                margin-left: {AppDimensions.PADDING_MEDIUM};
            }}
        """)
        controls_layout.addWidget(self.port_status_label)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout, 0, 0, 1, 4)
        
        # Port configuration
        ports_layout = QHBoxLayout()
        ports_layout.addWidget(self._create_incoming_port_section())
        ports_layout.addWidget(self._create_outgoing_ports_section())
        layout.addLayout(ports_layout, 1, 0, 1, 4)
        
        return group
    
    def _create_incoming_port_section(self) -> QGroupBox:
        """Create incoming port configuration"""
        group, layout = self._create_groupbox_with_layout("Incoming Port")
        
        self.incoming_port = ThemeManager.create_combobox(editable=True)
        self.incoming_port.currentTextChanged.connect(self.update_preview)
        self.incoming_port.currentTextChanged.connect(self.update_port_type_indicator)
        layout.addWidget(self.incoming_port)
        
        layout.addWidget(ThemeManager.create_label("Baud Rate:"))
        
        self.incoming_baud = ThemeManager.create_combobox()
        self._populate_baud_rates(self.incoming_baud)
        self.incoming_baud.currentTextChanged.connect(self.update_preview)
        self.incoming_baud.currentTextChanged.connect(self.on_incoming_baud_changed)
        layout.addWidget(self.incoming_baud)
        
        self.incoming_port_type = ThemeManager.create_label("")
        self.incoming_port_type.setWordWrap(True)
        self.incoming_port_type.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-style: italic;
                padding: {AppDimensions.PADDING_SMALL};
            }}
        """)
        layout.addWidget(self.incoming_port_type)
        
        return group
    
    def _create_outgoing_ports_section(self) -> QGroupBox:
        """Create outgoing ports configuration"""
        group, layout = self._create_groupbox_with_layout("Outgoing Ports")
        
        # Output ports container
        self.output_ports_widget = QWidget()
        self.output_ports_layout = QVBoxLayout(self.output_ports_widget)
        self.output_ports_layout.setSpacing(AppDimensions.SPACING_TINY)
        self.output_ports_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        output_scroll = QScrollArea()
        output_scroll.setWidgetResizable(True)
        output_scroll.setWidget(self.output_ports_widget)
        output_scroll.setMaximumHeight(AppDimensions.HEIGHT_TEXT_XLARGE)
        output_scroll.setStyleSheet(AppStyles.scroll_area())
        layout.addWidget(output_scroll)
        
        return group
    
    
    def _create_control_buttons(self) -> QHBoxLayout:
        """Create unified control buttons bar with inline status and output log"""
        layout = QHBoxLayout()
        layout.setSpacing(AppDimensions.SPACING_MEDIUM)
        layout.setContentsMargins(0, AppDimensions.SPACING_SMALL, 0, AppDimensions.SPACING_SMALL)
        
        # Preview control
        self.preview_btn = ThemeManager.create_icon_button("refresh", "Update command preview", "medium")
        self.preview_btn.clicked.connect(self.update_preview)
        layout.addWidget(self.preview_btn)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        separator1.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BORDER_DEFAULT};
                max-width: 1px;
                margin: {AppDimensions.PADDING_SMALL} {AppDimensions.PADDING_MEDIUM};
            }}
        """)
        layout.addWidget(separator1)
        
        # Hub4com controls
        self.start_btn = ThemeManager.create_icon_button("play", "Start hub4com routing", "medium")
        self.start_btn.clicked.connect(self.start_hub4com)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = ThemeManager.create_icon_button("stop", "Stop hub4com routing", "medium")
        self.stop_btn.clicked.connect(self.stop_hub4com)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BORDER_DEFAULT};
                max-width: 1px;
                margin: {AppDimensions.PADDING_SMALL} {AppDimensions.PADDING_MEDIUM};
            }}
        """)
        layout.addWidget(separator2)
        
        # Status label (inline with controls, matching other sections)
        self.status_label = ThemeManager.create_label(AppMessages.READY, "status")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-style: italic;
                margin-left: {AppDimensions.PADDING_MEDIUM};
            }}
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return layout
    
    def _create_output_section(self) -> QSplitter:
        """Create horizontal two-pane design with command preview and output log"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Command preview
        preview_group, preview_layout = self._create_groupbox_with_layout("Command Preview")
        self.command_preview = ThemeManager.create_textedit("console")
        self.command_preview.setMinimumHeight(AppDimensions.HEIGHT_TEXT_MEDIUM)
        self.command_preview.setMaximumHeight(AppDimensions.HEIGHT_TEXT_XLARGE)
        preview_layout.addWidget(self.command_preview)
        
        # Output log (always visible)
        output_group, output_layout = self._create_groupbox_with_layout("Output Log")
        self.output_text = ThemeManager.create_textedit("console")
        self.output_text.setMinimumHeight(AppDimensions.HEIGHT_TEXT_SMALL)
        self.output_text.setMaximumHeight(AppDimensions.HEIGHT_TEXT_LARGE)
        output_layout.addWidget(self.output_text)
        
        splitter.addWidget(preview_group)
        splitter.addWidget(output_group)
        splitter.setSizes([400, 400])  # Equal sizing
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
        """Add a new output port configuration"""
        port_number = len(self.output_port_widgets) + 1
        available_ports = self.get_available_ports()
        
        widget = OutputPortWidget(port_number, available_ports, self)
        widget.remove_btn.clicked.connect(lambda: self.remove_output_port(widget))
        widget.port_combo.currentTextChanged.connect(self.update_preview)
        widget.baud_combo.currentTextChanged.connect(self.update_preview)
        widget.port_changed.connect(self.update_preview)
        
        self.output_port_widgets.append(widget)
        self.output_ports_layout.addWidget(widget)
        
        self.renumber_output_ports()
        self.update_preview()
    
    def remove_output_port(self, widget: OutputPortWidget):
        """Remove an output port configuration"""
        if len(self.output_port_widgets) > Config.MIN_OUTPUT_PORTS:
            self.output_port_widgets.remove(widget)
            self.output_ports_layout.removeWidget(widget)
            widget.deleteLater()
            self.renumber_output_ports()
            self.update_preview()
        else:
            self._show_message("Cannot Remove", "At least one output port is required.")
    
    def remove_all_output_ports(self):
        """Remove all output ports except the minimum required"""
        if len(self.output_port_widgets) <= Config.MIN_OUTPUT_PORTS:
            self._show_message("Cannot Remove All", "At least one output port is required.")
            return
        
        # Remove all widgets except the first one
        widgets_to_remove = self.output_port_widgets[Config.MIN_OUTPUT_PORTS:]
        for widget in widgets_to_remove:
            self.output_port_widgets.remove(widget)
            self.output_ports_layout.removeWidget(widget)
            widget.deleteLater()
        
        self.renumber_output_ports()
        self.update_preview()
    
    def renumber_output_ports(self):
        """Update port numbers after add/remove"""
        for i, widget in enumerate(self.output_port_widgets):
            widget.port_number = i + 1
            widget.findChild(QLabel).setText(f"Port {i + 1}:")
    
    def get_available_ports(self) -> List[str]:
        """Get list of available ports"""
        return [p.port_name for p in self.scanned_ports] if self.scanned_ports else []
    
    def format_port_name(self, port: str) -> Optional[str]:
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
    
    def set_all_baud_rates(self, rate: str):
        """Set all ports to the same baud rate"""
        self.incoming_baud.setCurrentText(rate)
        for widget in self.output_port_widgets:
            widget.baud_combo.setCurrentText(rate)
        self.update_preview()
    
    def on_sync_baud_rates_changed(self):
        """Handle sync baud rates checkbox change"""
        if self.sync_baud_rates.isChecked():
            self.set_all_baud_rates(self.incoming_baud.currentText())
    
    def on_incoming_baud_changed(self):
        """Handle incoming baud rate change"""
        if self.sync_baud_rates.isChecked():
            self.set_all_baud_rates(self.incoming_baud.currentText())
    
    # ========================================================================
    # PORT SCANNING
    # ========================================================================
    
    def _safe_refresh_ports(self):
        """Safely refresh port lists with error handling"""
        try:
            self.refresh_port_lists()
        except Exception as e:
            print(f"Error during auto-scan: {e}")
            self._update_status(AppMessages.NO_DEVICES, self.port_status_label)
            self._update_port_combos_no_devices()
    
    def show_port_scanner(self):
        """Show the port scanner dialog"""
        dialog = PortScanDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.scanned_ports = dialog.ports
            self.refresh_port_lists()
    
    def refresh_port_lists(self):
        """Refresh all port combo boxes with scanned ports"""
        if self.port_scanner_thread and self.port_scanner_thread.isRunning():
            return
        
        try:
            self.port_scanner_thread = PortScanner()
            self.port_scanner_thread.scan_completed.connect(self.on_ports_scanned)
            self.port_scanner_thread.finished.connect(lambda: setattr(self, 'port_scanner_thread', None))
            self.port_scanner_thread.start()
        except Exception as e:
            print(f"Error starting port scan: {e}")
            self._update_status(AppMessages.NO_DEVICES, self.port_status_label)
            self._update_port_combos_no_devices()
    
    def _update_port_combos_no_devices(self):
        """Update port combos when no devices are found"""
        self.incoming_port.clear()
        self.incoming_port.addItem(AppMessages.NO_DEVICES)
        self.incoming_port.setEnabled(False)
        
        for widget in self.output_port_widgets:
            widget.populate_ports([])
    
    def on_ports_scanned(self, ports):
        """Handle completed port scan for combo boxes"""
        self.scanned_ports = ports
        
        if not ports:
            self._update_status(AppMessages.NO_DEVICES, self.port_status_label)
            self._update_port_combos_no_devices()
            return
        
        self._update_status(f"Found {len(ports)} ports", self.port_status_label)
        
        # Update incoming port combo
        current_incoming = self.incoming_port.currentText()
        self.incoming_port.clear()
        self.incoming_port.setEnabled(True)
        
        for port in ports:
            display_text = port.port_name
            if port.is_moxa:
                display_text += " (Moxa)"
            elif port.port_type.startswith("Virtual"):
                display_text += f" ({port.port_type.split(' ')[1]})"
            self.incoming_port.addItem(display_text, port.port_name)
        
        # Restore selection
        index = self.incoming_port.findData(current_incoming)
        if index >= 0:
            self.incoming_port.setCurrentIndex(index)
        elif self.incoming_port.count() > 0:
            self.incoming_port.setCurrentIndex(0)
        
        # Update output port widgets
        for widget in self.output_port_widgets:
            widget.populate_ports_enhanced(ports)
        
        self.update_port_type_indicator()
    
    def update_port_type_indicator(self):
        """Update the port type indicator"""
        current_port = self.incoming_port.currentData()
        if not current_port:
            self.incoming_port_type.setText("")
            return
        
        port_info = next((p for p in self.scanned_ports if p.port_name == current_port), None)
        if not port_info:
            self.incoming_port_type.setText("")
            return
        
        indicators = {
            "moxa": "MOXA Network Device - Make sure baud rate matches your source device",
            "physical": "PHYSICAL PORT - Connected to real hardware, verify device baud rate",
            "virtual": "VIRTUAL PORT - Software-created port for inter-application communication"
        }
        
        if port_info.is_moxa:
            text = indicators["moxa"]
        elif port_info.port_type == "Physical":
            text = indicators["physical"]
        else:
            text = indicators["virtual"]
        
        self.incoming_port_type.setText(text)
    
    # ========================================================================
    # HUB4COM MANAGEMENT
    # ========================================================================
    
    def build_command(self) -> Optional[List[str]]:
        """Build the hub4com command with baud rate support"""
        exe_path = "hub4com.exe"
        cmd = [exe_path]
        
        # Get incoming port and baud rate
        incoming = self.incoming_port.currentData() or self.incoming_port.currentText()
        incoming_baud = self.incoming_baud.currentText()
        
        if not incoming or "No COM" in incoming:
            return None
        
        # Get output ports
        output_configs = []
        for widget in self.output_port_widgets:
            config = widget.get_config()
            if config.port_name and "No COM" not in config.port_name:
                output_configs.append(config)
        
        if not output_configs:
            return None
        
        # Build route options based on user settings
        self._add_route_options(cmd, len(output_configs))
        
        # Add CTS option
        if self.disable_cts.isChecked():
            cmd.append('--octs=off')
        
        # Add incoming port
        cmd.append(f'--baud={incoming_baud}')
        formatted_incoming = self.format_port_name(incoming)
        if not formatted_incoming:
            return None
        cmd.append(formatted_incoming)
        
        # Add output ports
        for config in output_configs:
            cmd.append(f'--baud={config.baud_rate}')
            formatted_port = self.format_port_name(config.port_name)
            if not formatted_port:
                return None
            cmd.append(formatted_port)
        
        return cmd
    
    def _add_route_options(self, cmd: List[str], num_output_ports: int):
        """Add route options to command based on current settings"""
        output_indices = ','.join(str(i + 1) for i in range(num_output_ports))
        
        # Basic route mode
        if self.route_settings['mode'] == 'one_way':
            # Default: incoming port (0) to all output ports
            cmd.append(f'--route=0:{output_indices}')
        elif self.route_settings['mode'] == 'two_way':
            # Bidirectional: incoming port (0) to all output ports and vice versa
            cmd.append(f'--bi-route=0:{output_indices}')
        elif self.route_settings['mode'] == 'full_network':
            # All ports communicate with all other ports
            cmd.append('--route=All:All')
        
        # Advanced options
        if self.route_settings['echo_enabled']:
            # Echo back to source port
            cmd.append('--echo-route=0')
        
        if self.route_settings['flow_control_enabled']:
            # Enable flow control routing
            cmd.append(f'--fc-route=0:{output_indices}')
        
        if self.route_settings['disable_default_fc']:
            # Disable default flow control
            cmd.append(f'--no-default-fc-route=0:{output_indices}')
    
    def update_preview(self):
        """Update the command preview"""
        cmd = self.build_command()
        if not cmd:
            if not self.scanned_ports:
                self.command_preview.setPlainText(AppMessages.NO_DEVICES_FULL)
            else:
                self.command_preview.setPlainText("Please select valid ports for routing")
            return
        
        # Build command string
        command_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd)
        self.command_preview.setPlainText(command_str)
        
        # Add explanation
        incoming_display = self.incoming_port.currentData() or self.incoming_port.currentText()
        incoming_baud = self.incoming_baud.currentText()
        
        explanation = f"\nData Flow & Configuration:\n"
        
        # Add route mode explanation
        mode_descriptions = {
            'one_way': f"• ROUTING: One-way (FROM {incoming_display} TO all output ports)\n",
            'two_way': f"• ROUTING: Two-way (BETWEEN {incoming_display} AND all output ports)\n",
            'full_network': "• ROUTING: Full network (ALL ports communicate with ALL other ports)\n"
        }
        explanation += mode_descriptions.get(self.route_settings['mode'], mode_descriptions['one_way'])
        
        explanation += f"• INCOMING: {incoming_display} @ {incoming_baud} baud\n"
        explanation += "• OUTGOING: "
        
        output_info = []
        for widget in self.output_port_widgets:
            config = widget.get_config()
            if config.port_name and "No COM" not in config.port_name:
                output_info.append(f"{config.port_name} @ {config.baud_rate} baud")
        
        explanation += ", ".join(output_info) + "\n"
        
        # Add advanced options status
        if self.route_settings['echo_enabled']:
            explanation += "• ECHO: Enabled (data sent back to source)\n"
        if self.route_settings['flow_control_enabled']:
            explanation += "• FLOW CONTROL: Enabled (hardware handshaking)\n"
        if self.route_settings['disable_default_fc']:
            explanation += "• DEFAULT FLOW CONTROL: Disabled (advanced mode)\n"
        
        if self.disable_cts.isChecked():
            explanation += "• CTS handshaking: DISABLED\n"
        
        # Check for baud rate mismatches
        all_baud_rates = [incoming_baud] + [w.baud_combo.currentText() for w in self.output_port_widgets]
        if len(set(all_baud_rates)) > 1:
            explanation += "⚠️  WARNING: Baud rate mismatch detected!\n"
            explanation += "   Consider using the same baud rate for all ports.\n"
        
        self.command_preview.append(explanation)
    
    def start_hub4com(self):
        """Start the hub4com process"""
        cmd = self.build_command()
        if not cmd:
            if not self.scanned_ports:
                self._show_message("No Devices", AppMessages.NO_DEVICES_FULL, "warning")
            else:
                self._show_message("Error", "Please select valid ports for routing", "warning")
            return
        
        # Check if hub4com.exe exists
        if not self._verify_hub4com_exe(cmd):
            return
        
        # Check for Moxa port
        if not self._check_moxa_port():
            return
        
        # Check for baud rate mismatches
        if not self._check_baud_rates():
            return
        
        # Start process
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.output_text.clear()
        self._update_status(AppMessages.STARTING_HUBCOM)
        
        self.hub4com_process = Hub4comProcess(cmd)
        self.hub4com_process.output_received.connect(self.on_output_received)
        self.hub4com_process.process_started.connect(self.on_process_started)
        self.hub4com_process.process_stopped.connect(self.on_process_stopped)
        self.hub4com_process.error_occurred.connect(self.on_error_occurred)
        self.hub4com_process.start()
    
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
        incoming_port = self.incoming_port.currentData() or self.incoming_port.currentText()
        port_info = next((p for p in self.scanned_ports if p.port_name == incoming_port), None)
        
        if port_info and port_info.is_moxa and not self.disable_cts.isChecked():
            reply = QMessageBox.question(
                self,
                "Moxa Port Detected",
                "You're using a Moxa virtual port. It's recommended to disable CTS handshaking.\n\nDisable CTS handshaking now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.disable_cts.setChecked(True)
        return True
    
    def _check_baud_rates(self) -> bool:
        """Check for baud rate mismatches"""
        all_baud_rates = [self.incoming_baud.currentText()]
        for widget in self.output_port_widgets:
            all_baud_rates.append(widget.baud_combo.currentText())
        
        if len(set(all_baud_rates)) > 1:
            baud_info = f"Incoming: {self.incoming_baud.currentText()}\n"
            for i, widget in enumerate(self.output_port_widgets):
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
        if self.hub4com_process:
            self.hub4com_process.stop_process()
            self._update_status(AppMessages.STOPPING_HUBCOM)
    
    def on_output_received(self, text: str):
        """Handle output from hub4com process"""
        self.output_text.append(text)
    
    def on_process_started(self):
        """Handle successful process start"""
        self._update_status(AppMessages.HUBCOM_RUNNING)
        self.output_text.append("✓ hub4com started successfully!")
        self.output_text.append("✓ Data routing is now active between your ports.")
        
        self.output_text.append(f"✓ Configuration:")
        incoming_baud = self.incoming_baud.currentText()
        self.output_text.append(f"  • Incoming: {self.incoming_port.currentText()} @ {incoming_baud} baud")
        
        for i, widget in enumerate(self.output_port_widgets):
            config = widget.get_config()
            self.output_text.append(f"  • Output {i+1}: {config.port_name} @ {config.baud_rate} baud")
    
    def on_process_stopped(self):
        """Handle process stop"""
        self._update_status(AppMessages.HUBCOM_STOPPED)
        self.output_text.append("\n--- hub4com stopped ---")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def on_error_occurred(self, error_msg: str):
        """Handle process errors"""
        self._update_status(AppMessages.ERROR_OCCURRED)
        self.output_text.append(f"\n❌ ERROR: {error_msg}")
        
        self._show_message("Hub4com Error", error_msg, "error")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    # ========================================================================
    # COM0COM MANAGEMENT
    # ========================================================================
    
    def list_com0com_pairs(self):
        """List all com0com port pairs"""
        self._update_status(AppMessages.LISTING_PAIRS, self.com0com_status)
        self.port_pairs_list.clear()
        
        self.com0com_thread = Com0comProcess(["list"])
        self.com0com_thread.command_completed.connect(self.on_list_completed)
        self.com0com_thread.start()
    
    def on_list_completed(self, success: bool, output: str):
        """Handle list command completion"""
        if not success:
            self._update_status("Failed to list pairs", self.com0com_status)
            self._show_message("Error", f"Failed to list com0com pairs:\n{output}", "warning")
            return
        
        pairs = self._parse_com0com_output(output)
        self._populate_pairs_list(pairs)
    
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
        self.port_pairs_list.clear()
        
        if not pairs:
            self._update_status("No port pairs configured", self.com0com_status)
            no_pairs_item = QListWidgetItem(
                "No virtual port pairs found yet.\n\n"
                "💡 Click 'Create New Pair' to create your first pair of connected virtual ports.\n"
                "This allows two applications to communicate through simulated serial ports."
            )
            no_pairs_item.setBackground(ThemeManager.get_accent_color('pair_info'))
            self.port_pairs_list.addItem(no_pairs_item)
            return
        
        for pair_num, ports in sorted(pairs.items()):
            if 'A' in ports and 'B' in ports:
                self._add_pair_to_list(pair_num, ports)
        
        count = len(pairs)
        self._update_status(f"Found {count} port pair{'s' if count != 1 else ''}", self.com0com_status)
    
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
        tooltip = AppMessages.PAIR_TOOLTIP_TEMPLATE.format(
            port_a=port_a, 
            params_a=params_a or 'Standard settings (no special features)',
            port_b=port_b, 
            params_b=params_b or 'Standard settings (no special features)'
        )
        item.setToolTip(tooltip)
        
        if status_indicators:
            item.setBackground(ThemeManager.get_accent_color('pair_highlight'))
        
        self.port_pairs_list.addItem(item)
    
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
        
        if "EmuBR=yes" in params:
            indicators.append("Baud Rate Timing")
        if "EmuOverrun=yes" in params:
            indicators.append("Buffer Overrun")
        if "ExclusiveMode=yes" in params:
            indicators.append("Exclusive Mode")
        if "PlugInMode=yes" in params:
            indicators.append("Plug-In Mode")
        
        return indicators
    
    def create_com0com_pair(self):
        """Create a new com0com port pair"""
        accepted, cmd_args = PairCreationDialog.create_port_pair(self)
        
        if accepted and cmd_args:
            self._update_status(AppMessages.CREATING_PAIR, self.com0com_status)
            
            self.com0com_thread = Com0comProcess(cmd_args)
            self.com0com_thread.command_completed.connect(
                lambda s, o: self._handle_com0com_result(s, o, "create")
            )
            self.com0com_thread.start()
    
    def remove_com0com_pair(self):
        """Remove selected com0com port pair"""
        current_item = self.port_pairs_list.currentItem()
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
                self._update_status(AppMessages.REMOVING_PAIR, self.com0com_status)
                
                self.com0com_thread = Com0comProcess(["remove", pair_num])
                self.com0com_thread.command_completed.connect(
                    lambda s, o: self._handle_com0com_result(s, o, "remove")
                )
                self.com0com_thread.start()
    
    def _handle_com0com_result(self, success: bool, output: str, operation: str):
        """Generic handler for com0com operations"""
        if success:
            messages = {
                "create": (AppMessages.PORT_PAIR_CREATED, "Virtual port pair created successfully!"),
                "remove": (AppMessages.PORT_PAIR_REMOVED, None)
            }
            status_msg, info_msg = messages.get(operation, (None, None))
            
            if status_msg:
                self._update_status(status_msg, self.com0com_status)
            if info_msg:
                self._show_message("Success", info_msg)
            
            self.list_com0com_pairs()
            self.refresh_port_lists()
        else:
            self._update_status(f"Failed to {operation} port pair", self.com0com_status)
            self._show_message("Error", f"Failed to {operation} port pair:\n{output}", "error")
    
    def on_pair_selected(self):
        """Handle port pair selection"""
        has_selection = self.port_pairs_list.currentItem() is not None
        self.remove_pair_btn.setEnabled(has_selection)
        self.settings_btn.setEnabled(has_selection)
    
    def on_pair_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on port pair"""
        if not item or "No virtual port pairs found" in item.text():
            return
        
        dialog = self._create_pair_details_dialog(item)
        dialog.exec()
    
    def _create_pair_details_dialog(self, item: QListWidgetItem) -> QDialog:
        """Create port pair details dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Port Pair Details")
        dialog.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
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
        button_layout.addStretch()
        close_btn = ThemeManager.create_button("Close", dialog.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        return dialog
    
    def show_settings_menu(self):
        """Show dynamic settings menu for selected pair"""
        current_item = self.port_pairs_list.currentItem()
        if not current_item or "No virtual port pairs found" in current_item.text():
            return
        
        # Parse port names
        item_text = current_item.text()
        port_a, port_b = self._parse_port_names_from_item(item_text)
        
        if not port_a or not port_b:
            return
        
        # Parse current settings
        current_settings = self._parse_current_settings(current_item.toolTip())
        
        # Create menu
        menu = self._create_settings_menu(port_a, port_b, current_settings)
        menu.exec(self.settings_btn.mapToGlobal(self.settings_btn.rect().bottomLeft()))
    
    def _parse_port_names_from_item(self, item_text: str) -> tuple:
        """Parse port names from list item text"""
        if "[CNCA" in item_text and "CNCB" in item_text:
            bracket_content = item_text.split("[")[1].split("]")[0]
            parts = bracket_content.split(" ↔ ")
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return "", ""
    
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
        
        # Help option
        menu.addAction("? What do these settings do?", self.show_com0com_help)
        menu.addSeparator()
        
        # Settings options
        settings_config = [
            ("EmuBR", "Baud Rate Timing"),
            ("EmuOverrun", "Buffer Overrun Protection"),
            ("ExclusiveMode", "Exclusive Access Mode"),
            ("PlugInMode", "Plug-In Mode")
        ]
        
        for param, display_name in settings_config:
            status = "ENABLED" if current_settings.get(param) == "yes" else "DISABLED"
            menu.addAction(f"{display_name}: {status}").setEnabled(False)
            
            if current_settings.get(param) == "yes":
                menu.addAction(f"   > Turn OFF {display_name}", 
                             partial(self.quick_modify_pair, param, "no"))
            else:
                menu.addAction(f"   > Turn ON {display_name}", 
                             partial(self.quick_modify_pair, param, "yes"))
            menu.addSeparator()
        
        return menu
    
    def quick_modify_pair(self, param: str, value: str):
        """Quick modify a parameter for selected pair"""
        current_item = self.port_pairs_list.currentItem()
        if not current_item:
            return
        
        port_a, port_b = self._parse_port_names_from_item(current_item.text())
        if not port_a or not port_b:
            return
        
        self._update_status(f"Setting {param}={value} for {port_a} ↔ {port_b}...", self.com0com_status)
        
        # Modify both ports
        self.pending_modifications = 2
        self.modification_success = True
        
        for port in [port_a, port_b]:
            thread = Com0comProcess(["change", port, f"{param}={value}"])
            thread.command_completed.connect(self.on_modify_completed)
            thread.finished.connect(lambda t=thread: self._cleanup_thread(t))
            self.com0com_threads.append(thread)
            thread.start()
    
    def on_modify_completed(self, success: bool, output: str):
        """Handle modify command completion"""
        self.pending_modifications -= 1
        if not success:
            self.modification_success = False
        
        if self.pending_modifications == 0:
            if self.modification_success:
                self._update_status("Properties modified successfully", self.com0com_status)
                QTimer.singleShot(500, self.list_com0com_pairs)
            else:
                self._update_status("Failed to modify properties", self.com0com_status)
                self._show_message("Error", "Some modifications failed", "warning")
    
    def _cleanup_thread(self, thread):
        """Remove thread reference after completion"""
        if thread in self.com0com_threads:
            self.com0com_threads.remove(thread)
    
    def show_com0com_help(self):
        """Show comprehensive help dialog for COM0COM settings"""
        dialog = Com0ComHelpDialog(self)
        dialog.exec()
    
    # ========================================================================
    # ROUTE OPTIONS MANAGEMENT
    # ========================================================================
    
    def show_route_options_menu(self):
        """Show route options configuration menu"""
        menu = QMenu(self)
        
        # Header
        header_action = menu.addAction("📋 Route Mode Configuration")
        header_action.setEnabled(False)
        menu.addSeparator()
        
        # Basic modes section
        basic_header = menu.addAction("🔄 BASIC MODES")
        basic_header.setEnabled(False)
        
        # One-way mode
        one_way_action = menu.addAction("    ● One-Way Splitting" if self.route_settings['mode'] == 'one_way' else "    ○ One-Way Splitting")
        one_way_action.triggered.connect(lambda: self.set_route_mode('one_way'))
        one_way_action.setToolTip("Send data from incoming port to all outgoing ports only")
        
        # Two-way mode
        two_way_action = menu.addAction("    ● Two-Way Communication" if self.route_settings['mode'] == 'two_way' else "    ○ Two-Way Communication")
        two_way_action.triggered.connect(lambda: self.set_route_mode('two_way'))
        two_way_action.setToolTip("Allow data to flow both ways between incoming and outgoing ports")
        
        # Full network mode
        network_action = menu.addAction("    ● Full Network Mode" if self.route_settings['mode'] == 'full_network' else "    ○ Full Network Mode")
        network_action.triggered.connect(lambda: self.set_route_mode('full_network'))
        network_action.setToolTip("All ports can communicate with each other (like a network hub)")
        
        menu.addSeparator()
        
        # Advanced options section
        advanced_header = menu.addAction("⚙️ ADVANCED OPTIONS")
        advanced_header.setEnabled(False)
        
        # Echo option
        echo_status = "☑" if self.route_settings['echo_enabled'] else "☐"
        echo_action = menu.addAction(f"    {echo_status} Echo Back to Source")
        echo_action.triggered.connect(self.toggle_echo_mode)
        echo_action.setToolTip("Send incoming data back to the same port (for testing)")
        
        # Flow control option
        fc_status = "☑" if self.route_settings['flow_control_enabled'] else "☐"
        fc_action = menu.addAction(f"    {fc_status} Enable Flow Control")
        fc_action.triggered.connect(self.toggle_flow_control)
        fc_action.setToolTip("Use hardware handshaking to prevent data loss")
        
        # Disable default flow control option
        disable_fc_status = "☑" if self.route_settings['disable_default_fc'] else "☐"
        disable_fc_action = menu.addAction(f"    {disable_fc_status} Disable Default Flow Control")
        disable_fc_action.triggered.connect(self.toggle_disable_default_fc)
        disable_fc_action.setToolTip("Turn off automatic flow control (advanced users only)")
        
        menu.addSeparator()
        
        # Help option
        help_action = menu.addAction("❓ What do these settings do?")
        help_action.triggered.connect(self.show_route_help)
        
        # Show menu
        menu.exec(self.route_mode_btn.mapToGlobal(self.route_mode_btn.rect().bottomLeft()))
    
    def set_route_mode(self, mode: str):
        """Set the route mode and update UI"""
        self.route_settings['mode'] = mode
        self.update_route_mode_button()
        self.update_preview()
    
    def toggle_echo_mode(self):
        """Toggle echo mode setting"""
        self.route_settings['echo_enabled'] = not self.route_settings['echo_enabled']
        self.update_preview()
    
    def toggle_flow_control(self):
        """Toggle flow control setting"""
        self.route_settings['flow_control_enabled'] = not self.route_settings['flow_control_enabled']
        self.update_preview()
    
    def toggle_disable_default_fc(self):
        """Toggle disable default flow control setting"""
        self.route_settings['disable_default_fc'] = not self.route_settings['disable_default_fc']
        self.update_preview()
    
    def update_route_mode_button(self):
        """Update route mode button text"""
        mode_names = {
            'one_way': 'One-Way',
            'two_way': 'Two-Way', 
            'full_network': 'Full Network'
        }
        mode_name = mode_names.get(self.route_settings['mode'], 'One-Way')
        self.route_mode_btn.setText(f"Route Mode: {mode_name} ▼")
    
    def show_route_help(self):
        """Show route options help dialog"""
        help_text = """
HUB4COM Route Mode Guide

🔄 BASIC MODES:

• One-Way Splitting (Default)
  Data flows FROM incoming port TO all outgoing ports only.
  Example: GPS device → Multiple navigation apps
  
• Two-Way Communication  
  Data flows both ways between incoming and outgoing ports.
  Example: Terminal program ↔ Serial device
  
• Full Network Mode
  All ports can talk to all other ports (like a network hub).
  Example: Multiple devices all communicating with each other

⚙️ ADVANCED OPTIONS:

• Echo Back to Source
  Sends received data back to the same port it came from.
  Good for testing and debugging serial applications.
  
• Enable Flow Control
  Uses RTS/CTS handshaking to prevent data loss.
  Enable when devices support hardware flow control.
  
• Disable Default Flow Control
  Turns off automatic flow control management.
  Only for advanced users who need custom flow control.

💡 RECOMMENDATIONS:
- Start with "One-Way Splitting" for most applications
- Use "Two-Way Communication" when devices need to respond
- Enable "Flow Control" only if both devices support it
- Leave advanced options OFF unless you have specific needs
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Route Options Help")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        help_display = ThemeManager.create_textedit("console_large")
        help_display.setReadOnly(True)
        help_display.setPlainText(help_text.strip())
        layout.addWidget(help_display)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = ThemeManager.create_button("Close", dialog.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    # ========================================================================
    # APPLICATION LIFECYCLE
    # ========================================================================
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop all threads
        threads_to_stop = []
        
        if self.port_scanner_thread and self.port_scanner_thread.isRunning():
            threads_to_stop.append((self.port_scanner_thread, "port scanner"))
        
        if self.com0com_thread and self.com0com_thread.isRunning():
            threads_to_stop.append((self.com0com_thread, "COM0COM"))
        
        for thread in self.com0com_threads:
            if thread.isRunning():
                threads_to_stop.append((thread, "COM0COM operation"))
        
        # Stop threads
        for thread, name in threads_to_stop:
            thread.terminate()
            if not thread.wait(1000):
                print(f"Warning: {name} thread did not stop gracefully")
        
        # Handle hub4com process
        if self.hub4com_process and self.hub4com_process.isRunning():
            reply = QMessageBox.question(
                self,
                "Close Application",
                "hub4com is still running. Stop it before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_hub4com()
                if self.hub4com_process:
                    self.hub4com_process.wait(3000)
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()