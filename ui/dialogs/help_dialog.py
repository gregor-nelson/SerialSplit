#!/usr/bin/env python3
"""
Unified Help Manager for Serial Port Splitter
Consolidated help system with centralized content management
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QTabWidget, QWidget, QLineEdit, QSplitter)
from PyQt6.QtCore import Qt
from enum import Enum
import os

from ui.theme.theme import ThemeManager, AppStyles, AppFonts, AppDimensions, AppColors


class HelpTopic(Enum):
    """Enumeration of all available help topics"""
    COM0COM_SETTINGS = "com0com_settings"
    HUB4COM_ROUTES = "hub4com_routes"
    HUB4COM_REFERENCE = "hub4com_reference"
    COM0COM_REFERENCE = "com0com_reference"
    PORT_TYPES = "port_types"
    CONFIGURATION = "configuration"
    QUICK_TIPS = "quick_tips"


class HelpContentRegistry:
    """Centralized registry for all help content"""
    
    @staticmethod
    def get_content(topic: HelpTopic) -> dict:
        """Get help content for specified topic"""
        content_map = {
            HelpTopic.COM0COM_SETTINGS: {
                "title": "COM0COM Virtual Port Settings",
                "content": HelpContentRegistry._get_com0com_settings_content(),
                "category": "Virtual Ports"
            },
            HelpTopic.HUB4COM_ROUTES: {
                "title": "HUB4COM Route Options",
                "content": HelpContentRegistry._get_hub4com_routes_content(),
                "category": "Routing"
            },
            HelpTopic.HUB4COM_REFERENCE: {
                "title": "HUB4COM Command Reference",
                "content": HelpContentRegistry._get_hub4com_reference_content(),
                "category": "Reference"
            },
            HelpTopic.COM0COM_REFERENCE: {
                "title": "COM0COM Command Reference",
                "content": HelpContentRegistry._get_com0com_reference_content(),
                "category": "Reference"
            },
            HelpTopic.PORT_TYPES: {
                "title": "Port Types & Identification",
                "content": HelpContentRegistry._get_port_types_content(),
                "category": "Configuration"
            },
            HelpTopic.CONFIGURATION: {
                "title": "System Configuration Guide",
                "content": HelpContentRegistry._get_configuration_content(),
                "category": "Configuration"
            },
            HelpTopic.QUICK_TIPS: {
                "title": "Quick Tips & Troubleshooting",
                "content": HelpContentRegistry._get_quick_tips_content(),
                "category": "Tips"
            }
        }
        return content_map.get(topic, {"title": "Help", "content": "Content not found", "category": "General"})
    
    @staticmethod
    def get_all_topics() -> list:
        """Get all available help topics grouped by category"""
        topics_by_category = {}
        for topic in HelpTopic:
            content = HelpContentRegistry.get_content(topic)
            category = content["category"]
            if category not in topics_by_category:
                topics_by_category[category] = []
            topics_by_category[category].append((topic, content["title"]))
        return topics_by_category
    
    @staticmethod
    def _get_com0com_settings_content() -> str:
        """Get COM0COM settings help content"""
        return """
<h2>COM0COM Virtual Serial Port Settings Guide</h2>
<h3>Overview</h3>
<p>The COM0COM driver facilitates the creation of virtual serial port pairs. These pairs are interconnected by a virtual null-modem cable, meaning any data written to one port in a pair is instantaneously received by the other. This guide details the configuration settings available for these port pairs.</p>

<h3>Port Display Format</h3>
<p>Port pairs are displayed using the following convention:</p>
<p style="margin-left: 20px;"><b>COM3 ⇄ COM4 [CNCA0 ⇄ CNCB0] [Features: Baud Rate Emulation]</b></p>
<ul>
    <li><b>COM3 ⇄ COM4</b>: These are the system-level port names that will be visible to and used by your applications.</li>
    <li><b>[CNCA0 ⇄ CNCB0]</b>: These are the internal driver names for the virtual port pair.</li>
    <li><b>[Features: ...]</b>: This section indicates which special emulation features are currently enabled for the port pair.</li>
</ul>

<h3>Configuration Settings</h3>
<p>The following settings control the behavior of the virtual serial ports to simulate physical hardware characteristics.</p>

<h4>Baud Rate Emulation (EmuBR)</h4>
<p><b>Functionality:</b> This setting emulates the transmission timing of a physical serial port.
<br><b>Default State (Disabled):</b> Data transfer occurs instantaneously, limited only by system performance.
<br><b>Enabled State:</b> Data transfer is throttled to match the baud rate specified by the connecting application (e.g., 9600 bps, 115200 bps).
<br><b>Recommended Use:</b> Enable this feature when developing or testing applications that are sensitive to serial port timing and require realistic transfer speeds.</p>

<h4>Buffer Overrun Emulation (EmuOverrun)</h4>
<p><b>Functionality:</b> This setting simulates the finite buffer capacity of a physical serial port.
<br><b>Default State (Disabled):</b> The driver uses extensive buffering to prevent data loss.
<br><b>Enabled State:</b> The port will drop data if the receiving application does not read it from the buffer quickly enough, simulating a hardware buffer overrun.
<br><b>Recommended Use:</b> Enable this feature specifically for testing an application's ability to handle data loss and error conditions.</p>

<h4>Exclusive Access Mode (ExclusiveMode)</h4>
<p><b>Functionality:</b> This setting controls the system-level visibility of the ports.
<br><b>Default State (Disabled):</b> Both ports in a pair are persistently visible in Device Manager and are available to all applications.
<br><b>Enabled State:</b> A port remains hidden from the system until its corresponding paired port is opened by an application.
<br><b>Recommended Use:</b> Enable this mode to prevent applications from accessing or listing a port until its counterpart is actively in use.</p>

<h4>Plug-In Mode (PlugInMode)</h4>
<p><b>Functionality:</b> This setting enables the dynamic enumeration and removal of a port from the system.
<br><b>Default State (Disabled):</b> The port is permanently registered in Device Manager.
<br><b>Enabled State:</b> The port is created and appears in Device Manager only when its paired port is opened, and it is removed when the paired port is closed.
<br><b>Recommended Use:</b> Enable this for advanced scenarios requiring dynamic port management based on application activity.</p>

<h3>Setup Recommendations</h3>

<h4>Standard Configuration (General Data Transfer)</h4>
<ul>
    <li>For maximum performance and reliability in standard application-to-application communication, it is recommended to leave all emulation settings disabled.</li>
</ul>

<h4>Development and Testing Configuration</h4>
<ul>
    <li>Enable <b>Baud Rate Emulation</b> to validate application behavior with realistic serial communication speeds.</li>
    <li>Enable <b>Buffer Overrun Emulation</b> to test an application's error and data loss handling logic.</li>
</ul>

<h3>Important Considerations</h3>
<ul>
    <li>Configuration changes are applied to the driver immediately and do not require a system restart.</li>
    <li>Settings are applied symmetrically to both ports within a virtual pair.</li>
    <li>To ensure new settings are recognized, applications may need to close and reopen the serial port connection.</li>
    <li>The default configuration (all features disabled) is the most stable and suitable for the majority of use cases.</li>
</ul>

<p><i>Note: For more detailed technical information, you may double-click any port pair in the list.</i></p>
"""
    
    @staticmethod
    def _get_hub4com_routes_content() -> str:
        """Get HUB4COM route options help content"""
        return """
<h2>HUB4COM Route Mode Guide</h2>

<h3>Basic Modes:</h3>

<h4>• One-Way Splitting (Default)</h4>
<p>Data flows FROM incoming port TO all outgoing ports only.<br>
<b>Example:</b> GPS device → Multiple navigation apps</p>

<h4>• Two-Way Communication</h4>
<p>Data flows both ways between incoming and outgoing ports.<br>
<b>Example:</b> Terminal program ↔ Serial device</p>

<h4>• Full Network Mode</h4>
<p>All ports can talk to all other ports (like a network hub).<br>
<b>Example:</b> Multiple devices all communicating with each other</p>

<h3>Advanced Options:</h3>

<h4>• Echo Back to Source</h4>
<p>Sends received data back to the same port it came from.<br>
<b>Good for:</b> Testing and debugging serial applications.</p>

<h4>• Enable Flow Control</h4>
<p>Uses RTS/CTS handshaking to prevent data loss.<br>
<b>Enable when:</b> Devices support hardware flow control.</p>

<h4>• Disable Default Flow Control</h4>
<p>Turns off automatic flow control management.<br>
<b>Only for:</b> Advanced users who need custom flow control.</p>

<h3>Recommendations:</h3>
<ul>
    <li>Start with "One-Way Splitting" for most applications</li>
    <li>Use "Two-Way Communication" when devices need to respond</li>
    <li>Enable "Flow Control" only if both devices support it</li>
    <li>Leave advanced options OFF unless you have specific needs</li>
</ul>
"""
    
    @staticmethod
    def _get_hub4com_reference_content() -> str:
        """Get HUB4COM command reference content"""
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            help_file = os.path.join(script_dir, "hub4comhelp.txt")
            with open(help_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"<pre>{content}</pre>"
        except:
            return "<p>HUB4COM reference file not found. Please ensure hub4comhelp.txt is in the application directory.</p>"
    
    @staticmethod
    def _get_com0com_reference_content() -> str:
        """Get COM0COM command reference content"""
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            help_file = os.path.join(script_dir, "com0com_help_command.txt")
            with open(help_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"<pre>{content}</pre>"
        except:
            return "<p>COM0COM reference file not found. Please ensure com0com_help_command.txt is in the application directory.</p>"
    
    @staticmethod
    def _get_port_types_content() -> str:
        """Get port types and identification help content"""
        return """
<h2>Port Types & Identification Guide</h2>

<h3>Port Type Indicators</h3>

<h4>🌐 MOXA Network Device</h4>
<p><b>Description:</b> Network-attached serial device server<br>
<b>Important:</b> Make sure baud rate matches your source device<br>
<b>Common Use:</b> Remote serial device access over Ethernet</p>

<h4>🔌 Physical Port</h4>
<p><b>Description:</b> Hardware COM port (built-in or USB adapter)<br>
<b>Important:</b> Connected to real hardware, verify device baud rate<br>
<b>Common Use:</b> Direct connection to serial devices</p>

<h4>💻 Virtual Port</h4>
<p><b>Description:</b> Software-created port for inter-application communication<br>
<b>Important:</b> No physical hardware involved<br>
<b>Common Use:</b> Application-to-application data transfer</p>

<h3>Baud Rate Guidelines</h3>
<ul>
    <li><b>Physical/MOXA Ports:</b> Must match the connected device's baud rate exactly</li>
    <li><b>Virtual Ports:</b> Baud rate setting is usually ignored (instant transfer)</li>
    <li><b>Mixed Routing:</b> Each port can have its own baud rate when routing between different types</li>
</ul>

<h3>Connection Tips</h3>
<ul>
    <li>Always verify physical connections before troubleshooting software</li>
    <li>MOXA devices require network connectivity to function</li>
    <li>Virtual ports appear only when COM0COM pairs are created</li>
    <li>USB serial adapters may change port numbers when reconnected</li>
</ul>
"""
    
    @staticmethod
    def _get_configuration_content() -> str:
        """Get system configuration guide content"""
        return """
<h2>System Configuration Guide</h2>

<h3>Data Flow Architecture</h3>
<p>The Serial Port Splitter uses a hub-and-spoke model:</p>
<ol>
    <li><b>Incoming Port:</b> Receives data from your source device</li>
    <li><b>HUB4COM Router:</b> Central routing engine that distributes data</li>
    <li><b>Outgoing Ports:</b> Send data to multiple destination applications</li>
</ol>

<h3>Virtual Port Management</h3>
<p>COM0COM creates virtual port pairs that appear as real COM ports to applications:</p>
<ul>
    <li>Each pair consists of two linked ports (e.g., COM3 ↔ COM4)</li>
    <li>Data written to one port instantly appears on the paired port</li>
    <li>Applications see these as standard Windows COM ports</li>
</ul>

<h3>Application Setup Process</h3>
<ol>
    <li><b>Create Virtual Pairs:</b> Generate COM port pairs for your applications</li>
    <li><b>Configure Routing:</b> Set up data flow from source to destinations</li>
    <li><b>Set Baud Rates:</b> Match rates to your source device and applications</li>
    <li><b>Start Routing:</b> Begin the HUB4COM routing service</li>
    <li><b>Connect Applications:</b> Point your apps to the assigned COM ports</li>
</ol>

<h3>External Application Configuration</h3>
<p>When configuring your applications:</p>
<ul>
    <li>Use the COM port numbers shown in the application</li>
    <li>Set baud rates to match your source device</li>
    <li>Most applications will auto-detect the virtual ports</li>
    <li>Flow control settings are usually handled automatically</li>
</ul>

<h3>Troubleshooting Tips</h3>
<ul>
    <li>If ports don't appear, restart the application</li>
    <li>Check Windows Device Manager for port conflicts</li>
    <li>Ensure COM0COM driver is properly installed</li>
    <li>Verify source device is sending data before troubleshooting routing</li>
</ul>
"""
    
    @staticmethod
    def _get_quick_tips_content() -> str:
        """Get quick tips and troubleshooting content"""
        return """
<h2>Quick Tips & Troubleshooting</h2>

<h3>🚀 Quick Start</h3>
<ol>
    <li>Create virtual port pairs for your applications</li>
    <li>Select your incoming data source port</li>
    <li>Add outgoing ports for each application</li>
    <li>Set appropriate baud rates</li>
    <li>Start routing and connect your applications</li>
</ol>

<h3>🔧 Common Issues</h3>

<h4>"Port not found" or "Access denied"</h4>
<ul>
    <li>Close all applications using the ports</li>
    <li>Restart the Serial Port Splitter</li>
    <li>Check Windows Device Manager for conflicts</li>
</ul>

<h4>"No data received"</h4>
<ul>
    <li>Verify source device is connected and powered</li>
    <li>Check baud rate matches source device</li>
    <li>Test source port with a terminal program first</li>
</ul>

<h4>"Routing stopped unexpectedly"</h4>
<ul>
    <li>Check if any port was disconnected</li>
    <li>Restart routing from the application</li>
    <li>Ensure sufficient system resources</li>
</ul>

<h3>💡 Pro Tips</h3>
<ul>
    <li><b>Test First:</b> Use a simple terminal program to verify data flow before adding complexity</li>
    <li><b>Baud Rate Sync:</b> Use the "Set All" button to quickly match all outgoing rates</li>
    <li><b>Flow Control:</b> Enable CTS handshaking only if your source device supports it</li>
    <li><b>Port Numbers:</b> Note assigned port numbers before connecting applications</li>
    <li><b>System Tray:</b> The application continues running when minimized to system tray</li>
</ul>

<h3>📋 Best Practices</h3>
<ul>
    <li>Create descriptive names for virtual pairs</li>
    <li>Document your port assignments</li>
    <li>Test configuration before deploying</li>
    <li>Keep backups of working configurations</li>
    <li>Monitor system resources during heavy data flow</li>
</ul>
"""


class HelpManager:
    """Unified help system manager"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def show_help(topic: HelpTopic, parent=None):
        """Show help dialog for specified topic"""
        dialog = UnifiedHelpDialog(parent, topic)
        dialog.exec()
    
    @staticmethod
    def get_tooltip(tooltip_type: str, **kwargs) -> str:
        """Get formatted tooltip text"""
        tooltips = {
            "pair_tooltip": "Port A ({port_a}): {params_a}\nPort B ({port_b}): {params_b}\n\nRight-click or use 'Configure Features' to modify settings\nClick 'Help' button for detailed explanations of all features",
            "port_type_moxa": "🌐 MOXA Network Device - Make sure baud rate matches your source device",
            "port_type_physical": "🔌 PHYSICAL PORT - Connected to real hardware, verify device baud rate",
            "port_type_virtual": "💻 VIRTUAL PORT - Software-created port for inter-application communication"
        }
        template = tooltips.get(tooltip_type, "")
        return template.format(**kwargs)


class UnifiedHelpDialog(QDialog):
    """Modern unified help dialog with search and navigation"""
    
    def __init__(self, parent=None, initial_topic: HelpTopic = HelpTopic.COM0COM_SETTINGS):
        super().__init__(parent)
        self.initial_topic = initial_topic
        self.init_ui()
        self.load_topic(initial_topic)
    
    def init_ui(self):
        """Initialize the unified help interface"""
        self.setWindowTitle("Serial Port Splitter - Help & Documentation")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        layout = QVBoxLayout(self)
        
        # Create splitter for navigation and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Topic navigation
        nav_widget = self.create_navigation_panel()
        splitter.addWidget(nav_widget)
        
        # Right panel - Content display
        content_widget = self.create_content_panel()
        splitter.addWidget(content_widget)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 0)  # Navigation panel fixed width
        splitter.setStretchFactor(1, 1)  # Content panel gets remaining space
        splitter.setSizes([250, 750])
        
        layout.addWidget(splitter)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet(AppStyles.button())
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
    
    def create_navigation_panel(self) -> QWidget:
        """Create topic navigation panel"""
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        
        # Search box
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search help topics...")
        search_box.textChanged.connect(self.filter_topics)
        nav_layout.addWidget(search_box)
        
        # Topic tabs organized by category
        self.topic_tabs = QTabWidget()
        self.topic_tabs.setTabPosition(QTabWidget.TabPosition.West)
        
        topics_by_category = HelpContentRegistry.get_all_topics()
        
        for category, topics in topics_by_category.items():
            category_widget = QWidget()
            category_layout = QVBoxLayout(category_widget)
            
            for topic, title in topics:
                topic_button = QPushButton(title)
                topic_button.clicked.connect(lambda checked, t=topic: self.load_topic(t))
                topic_button.setStyleSheet(AppStyles.button("flat"))
                category_layout.addWidget(topic_button)
            
            category_layout.addStretch()
            self.topic_tabs.addTab(category_widget, category)
        
        nav_layout.addWidget(self.topic_tabs)
        return nav_widget
    
    def create_content_panel(self) -> QWidget:
        """Create content display panel"""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Content display area
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {AppColors.BORDER_DEFAULT};
                padding: 15px;
                background-color: {AppColors.BACKGROUND_WHITE};
                color: {AppColors.TEXT_DEFAULT};
                line-height: 1.5;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 11pt;
            }}
        """)
        
        content_layout.addWidget(self.content_display)
        return content_widget
    
    def load_topic(self, topic: HelpTopic):
        """Load and display help content for specified topic"""
        content_info = HelpContentRegistry.get_content(topic)
        self.content_display.setHtml(content_info["content"])
        self.setWindowTitle(f"Help - {content_info['title']}")
    
    def filter_topics(self, search_text: str):
        """Filter visible topics based on search text"""
        # Implementation for search filtering would go here
        # For now, this is a placeholder for the search functionality
        pass
