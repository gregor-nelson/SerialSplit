#!/usr/bin/env python3
"""
Enhanced Windows 10 Style Help Manager for Serial Port Splitter
Implements Windows Settings-style navigation with search and modern UI
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                              QWidget,
                             QListWidget, QListWidgetItem, QLabel, QFrame,
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QTextDocument, QTextCursor, QColor
from enum import Enum
import os
from typing import Dict, List, Optional, Tuple
from ui.theme.theme import (AppDimensions, ThemeManager,AppFonts, 
                           AppColors, HTMLTheme, AppStyles)

class HelpTopic(Enum):
    """Enumeration of all available help topics"""
    # Getting Started
    QUICK_START = "quick_start"
    FIRST_SETUP = "first_setup"
    
    # Virtual Ports
    COM0COM_SETTINGS = "com0com_settings"
    PORT_PAIRS = "port_pairs"
    PORT_TYPES = "port_types"
    
    # Routing
    HUB4COM_ROUTES = "hub4com_routes"
    ROUTING_MODES = "routing_modes"
    FLOW_CONTROL = "flow_control"
    
    # Configuration
    CONFIGURATION = "configuration"
    BAUD_RATES = "baud_rates"
    ADVANCED_SETTINGS = "advanced_settings"
    
    # Reference
    HUB4COM_REFERENCE = "hub4com_reference"
    COM0COM_REFERENCE = "com0com_reference"
    COMMAND_LINE = "command_line"
    
    # Troubleshooting
    QUICK_TIPS = "quick_tips"
    COMMON_ISSUES = "common_issues"
    ERROR_MESSAGES = "error_messages"


class HelpCategory:
    """Help categories with icons"""
    GETTING_STARTED = ("Getting Started", "")
    VIRTUAL_PORTS = ("Virtual Ports", "")
    ROUTING = ("Routing", "")
    CONFIGURATION = ("Configuration", "")
    REFERENCE = ("Reference", "")
    TROUBLESHOOTING = ("Troubleshooting", "")


class NavigationItem(QListWidgetItem):
    """Custom list item for navigation with category support"""
    def __init__(self, text: str, topic: Optional[HelpTopic] = None, 
                 is_category: bool = False, icon: str = ""):
        super().__init__()
        if is_category:
            self.setText(f"{icon}  {text.title()}")
            self.setFlags(Qt.ItemFlag.NoItemFlags)  # Make category non-selectable
        else:
            self.setText(f"    {text}")  # Indent topics under categories
        
        self.topic = topic
        self.is_category = is_category


class SearchHighlighter:
    """Utility class for highlighting search terms in content"""
    
    @staticmethod
    def highlight_text(text_edit: QTextEdit, search_term: str):
        """Highlight all occurrences of search term"""
        if not search_term:
            return
            
        # Clear existing highlights
        cursor = text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(cursor.charFormat())
        cursor.clearSelection()
        
        # Highlight new search term
        document = text_edit.document()
        cursor = QTextCursor(document)
        
        # Setup highlight format
        format = cursor.charFormat()
        format.setBackground(QColor(AppColors.ACCENT_YELLOW))
        format.setForeground(QColor(AppColors.TEXT_DEFAULT))
        
        # Find and highlight all occurrences
        while not cursor.isNull() and not cursor.atEnd():
            cursor = document.find(search_term, cursor, 
                                 QTextDocument.FindFlag.FindCaseSensitively)
            if not cursor.isNull():
                cursor.mergeCharFormat(format)


class HelpContentRegistry:
    """Enhanced content registry with metadata"""
    
    @staticmethod
    def get_content(topic: HelpTopic) -> dict:
        """Get help content for specified topic with enhanced metadata"""
        content_map = {
            # Getting Started
            HelpTopic.QUICK_START: {
                "title": "Quick Start Guide",
                "content": HelpContentRegistry._get_quick_start_content(),
                "category": HelpCategory.GETTING_STARTED,
                "keywords": ["start", "begin", "setup", "first", "guide"],
                "related": [HelpTopic.FIRST_SETUP, HelpTopic.PORT_PAIRS]
            },
            HelpTopic.FIRST_SETUP: {
                "title": "First Time Setup",
                "content": HelpContentRegistry._get_first_setup_content(),
                "category": HelpCategory.GETTING_STARTED,
                "keywords": ["install", "setup", "configure", "initial"],
                "related": [HelpTopic.QUICK_START, HelpTopic.COM0COM_SETTINGS]
            },
            
            # Virtual Ports
            HelpTopic.COM0COM_SETTINGS: {
                "title": "COM0COM Virtual Port Settings",
                "content": HelpContentRegistry._get_com0com_settings_content(),
                "category": HelpCategory.VIRTUAL_PORTS,
                "keywords": ["com0com", "virtual", "port", "settings", "emulation"],
                "related": [HelpTopic.PORT_PAIRS, HelpTopic.PORT_TYPES]
            },
            HelpTopic.PORT_PAIRS: {
                "title": "Managing Port Pairs",
                "content": HelpContentRegistry._get_port_pairs_content(),
                "category": HelpCategory.VIRTUAL_PORTS,
                "keywords": ["pair", "create", "remove", "manage", "virtual"],
                "related": [HelpTopic.COM0COM_SETTINGS, HelpTopic.PORT_TYPES]
            },
            HelpTopic.PORT_TYPES: {
                "title": "Port Types & Identification",
                "content": HelpContentRegistry._get_port_types_content(),
                "category": HelpCategory.VIRTUAL_PORTS,
                "keywords": ["type", "physical", "virtual", "moxa", "identify"],
                "related": [HelpTopic.PORT_PAIRS, HelpTopic.CONFIGURATION]
            },
            
            # Routing
            HelpTopic.HUB4COM_ROUTES: {
                "title": "HUB4COM Route Options",
                "content": HelpContentRegistry._get_hub4com_routes_content(),
                "category": HelpCategory.ROUTING,
                "keywords": ["route", "hub4com", "split", "data", "flow"],
                "related": [HelpTopic.ROUTING_MODES, HelpTopic.FLOW_CONTROL]
            },
            HelpTopic.ROUTING_MODES: {
                "title": "Understanding Routing Modes",
                "content": HelpContentRegistry._get_routing_modes_content(),
                "category": HelpCategory.ROUTING,
                "keywords": ["mode", "one-way", "two-way", "network", "communication"],
                "related": [HelpTopic.HUB4COM_ROUTES, HelpTopic.FLOW_CONTROL]
            },
            HelpTopic.FLOW_CONTROL: {
                "title": "Flow Control Settings",
                "content": HelpContentRegistry._get_flow_control_content(),
                "category": HelpCategory.ROUTING,
                "keywords": ["flow", "control", "rts", "cts", "handshaking"],
                "related": [HelpTopic.ROUTING_MODES, HelpTopic.ADVANCED_SETTINGS]
            },
            
            # Configuration
            HelpTopic.CONFIGURATION: {
                "title": "System Configuration Guide",
                "content": HelpContentRegistry._get_configuration_content(),
                "category": HelpCategory.CONFIGURATION,
                "keywords": ["config", "setup", "system", "architecture"],
                "related": [HelpTopic.BAUD_RATES, HelpTopic.ADVANCED_SETTINGS]
            },
            HelpTopic.BAUD_RATES: {
                "title": "Baud Rate Configuration",
                "content": HelpContentRegistry._get_baud_rates_content(),
                "category": HelpCategory.CONFIGURATION,
                "keywords": ["baud", "rate", "speed", "communication"],
                "related": [HelpTopic.CONFIGURATION, HelpTopic.PORT_TYPES]
            },
            HelpTopic.ADVANCED_SETTINGS: {
                "title": "Advanced Settings",
                "content": HelpContentRegistry._get_advanced_settings_content(),
                "category": HelpCategory.CONFIGURATION,
                "keywords": ["advanced", "expert", "settings", "options"],
                "related": [HelpTopic.FLOW_CONTROL, HelpTopic.COM0COM_SETTINGS]
            },
            
            # Reference
            HelpTopic.HUB4COM_REFERENCE: {
                "title": "HUB4COM Command Reference",
                "content": HelpContentRegistry._get_hub4com_reference_content(),
                "category": HelpCategory.REFERENCE,
                "keywords": ["hub4com", "command", "reference", "manual"],
                "related": [HelpTopic.COM0COM_REFERENCE, HelpTopic.COMMAND_LINE]
            },
            HelpTopic.COM0COM_REFERENCE: {
                "title": "COM0COM Command Reference",
                "content": HelpContentRegistry._get_com0com_reference_content(),
                "category": HelpCategory.REFERENCE,
                "keywords": ["com0com", "command", "reference", "manual"],
                "related": [HelpTopic.HUB4COM_REFERENCE, HelpTopic.COMMAND_LINE]
            },
            HelpTopic.COMMAND_LINE: {
                "title": "Command Line Usage",
                "content": HelpContentRegistry._get_command_line_content(),
                "category": HelpCategory.REFERENCE,
                "keywords": ["command", "line", "cli", "terminal"],
                "related": [HelpTopic.HUB4COM_REFERENCE, HelpTopic.COM0COM_REFERENCE]
            },
            
            # Troubleshooting
            HelpTopic.QUICK_TIPS: {
                "title": "Quick Tips & Troubleshooting",
                "content": HelpContentRegistry._get_quick_tips_content(),
                "category": HelpCategory.TROUBLESHOOTING,
                "keywords": ["tips", "troubleshoot", "help", "problem"],
                "related": [HelpTopic.COMMON_ISSUES, HelpTopic.ERROR_MESSAGES]
            },
            HelpTopic.COMMON_ISSUES: {
                "title": "Common Issues & Solutions",
                "content": HelpContentRegistry._get_common_issues_content(),
                "category": HelpCategory.TROUBLESHOOTING,
                "keywords": ["issue", "problem", "error", "fix", "solution"],
                "related": [HelpTopic.QUICK_TIPS, HelpTopic.ERROR_MESSAGES]
            },
            HelpTopic.ERROR_MESSAGES: {
                "title": "Error Messages Guide",
                "content": HelpContentRegistry._get_error_messages_content(),
                "category": HelpCategory.TROUBLESHOOTING,
                "keywords": ["error", "message", "warning", "alert"],
                "related": [HelpTopic.COMMON_ISSUES, HelpTopic.QUICK_TIPS]
            }
        }
        
        return content_map.get(topic, {
            "title": "Help", 
            "content": "Content not found", 
            "category": HelpCategory.GETTING_STARTED,
            "keywords": [],
            "related": []
        })
    
    @staticmethod
    def search_topics(search_term: str) -> List[Tuple[HelpTopic, int]]:
        """Search topics and return matches with relevance scores"""
        if not search_term:
            return []
            
        search_lower = search_term.lower()
        results = []
        
        for topic in HelpTopic:
            content_data = HelpContentRegistry.get_content(topic)
            score = 0
            
            # Check title
            if search_lower in content_data["title"].lower():
                score += 10
            
            # Check keywords
            for keyword in content_data["keywords"]:
                if search_lower in keyword.lower():
                    score += 5
            
            # Check content (basic check)
            if search_lower in content_data["content"].lower():
                score += 1
                
            if score > 0:
                results.append((topic, score))
        
        # Sort by relevance score
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    @staticmethod
    def get_categories_with_topics() -> Dict[HelpCategory, List[Tuple[HelpTopic, str]]]:
        """Get all categories with their topics"""
        categories = {}
        
        for topic in HelpTopic:
            content = HelpContentRegistry.get_content(topic)
            category = content["category"]
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append((topic, content["title"]))
        
        return categories
    
    # Content generation methods (enhanced versions)
    @staticmethod
    def _get_quick_start_content() -> str:
            """Enhanced quick start content"""
            return f"""
        {HTMLTheme.get_styles()}
        <h2>Quick Start Guide</h2>

        <div class="info-box">
        <h3>Welcome to Serial Port Splitter!</h3>
        <p>This guide will enable operation in just a few minutes. Follow these straightforward steps to begin splitting serial data.</p>
        </div>

        <h3>Step 1: Create Virtual Port Pairs</h3>
        <p>Virtual port pairs are the foundation of serial port splitting. Here's how to create them:</p>
        <ol>
            <li>Click the <b>"Create New Pair"</b> button in the Virtual Ports section</li>
            <li>The system will automatically assign port numbers (e.g., COM3 ↔ COM4)</li>
            <li>Note these port numbers - these will be required for applications</li>
            <li><b>Important:</b> Applications should connect to the "other side" of the pair from the data source (if this utility uses COM3 as the source, applications connect to COM4)</li>
        </ol>

        <h3>Step 2: Select Data Source</h3>
        <p>Select the serial data source:</p>
        <ul>
            <li><b>Physical Port:</b> A real COM port connected to hardware</li>
            <li><b>MOXA Device:</b> Network-attached serial device</li>
            <li><b>Virtual Port:</b> One side of a virtual port pair</li>
        </ul>

        <h3>Step 3: Add Output Destinations</h3>
        <p>Add ports to which data should be sent:</p>
        <ol>
            <li>Click <b>"Add Output Port"</b> for each destination</li>
            <li>Select the appropriate COM port from the dropdown</li>
            <li>Set the baud rate to match application requirements</li>
        </ol>

        <h3>Step 4: Configure and Start</h3>
        <ol>
            <li>Choose your routing mode (usually "One-Way" for basic splitting)</li>
            <li>Verify all baud rates are correct</li>
            <li>Click <b>"Start Routing"</b> to begin data flow</li>
        </ol>

        <div class="footer-box">
        <p><b>Tip:</b> Use the "Set All" button to quickly apply the same baud rate to all output ports!</p>
        </div>
        """
    
    @staticmethod
    def _get_first_setup_content() -> str:
        """First time setup content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>First Time Setup</h2>

    <div class="info-box">
    <h3>Initial Configuration</h3>
    <p>Ensure everything is properly configured for initial use.</p>
    </div>

    <h3>Prerequisites Check</h3>
    <ul>
        <li>Windows 10 or later</li>
        <li>Administrator privileges (for driver installation)</li>
        <li>COM0COM driver installed</li>
        <li>Serial device connected</li>
    </ul>

    <div class="warning-box">
    <h3>⚠️ Administrator Privileges Required</h3>
    <p><b>CRITICAL:</b> COM0COM driver installation requires Windows Administrator privileges and UAC elevation. Installation is NOT automatic.</p>
    </div>

    <h3>Required Installation Steps</h3>
    <ol>
        <li><b>Close all applications</b> that may use serial ports</li>
        <li><b>Right-click the application</b> and select "Run as Administrator"</li>
        <li><b>Accept UAC prompt</b> when Windows requests elevation</li>
        <li><b>Allow driver installation</b> if Windows Defender or antivirus shows warnings</li>
        <li><b>Restart the system</b> if prompted to complete driver registration</li>
    </ol>

    <h3>Verify Installation</h3>
    <p>To confirm everything is working:</p>
    <ol>
        <li>Click "Refresh Ports" - available COM ports should be visible</li>
        <li>Create a test virtual pair</li>
        <li>The new ports should appear in the port lists</li>
    </ol>

    <div class="warning-box">
    <h3>⚠️ Enterprise Security Considerations</h3>
    <p><b>Corporate/Offshore Networks:</b> Group Policy or security software may prevent COM0COM installation:</p>
    <ul>
        <li><b>Digital signature warnings:</b> COM0COM uses test-signed drivers</li>
        <li><b>Driver installation restrictions:</b> IT policies may block unsigned drivers</li>
        <li><b>Antivirus interference:</b> Security software may quarantine driver files</li>
    </ul>
    <p><b>Resolution:</b> Contact IT security team for driver approval before deployment.</p>
    </div>
    """

    @staticmethod
    def _get_port_pairs_content() -> str:
        """Port pairs management content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>Managing Virtual Port Pairs</h2>

    <h3>Understanding Port Pairs</h3>
    <p>Virtual port pairs are two COM ports connected by a virtual null-modem cable. Data written to one port instantly appears on the other.</p>

    <div class="info-box">
    <p><b>Example:</b> COM3 ⇄ COM4 means anything sent to COM3 appears on COM4, and vice versa.</p>
    </div>

    <h3>Creating Port Pairs</h3>
    <ol>
        <li>Click <b>"Create New Pair"</b> in the Virtual Ports section</li>
        <li>The system automatically assigns the next available port numbers</li>
        <li>Port names follow the pattern: CNCA0/CNCB0, CNCA1/CNCB1, etc.</li>
    </ol>

    <h3>Managing Existing Pairs</h3>
    <ul>
        <li><b>View Details:</b> Double-click any pair to see advanced settings</li>
        <li><b>Configure Features:</b> Right-click to access emulation options</li>
        <li><b>Remove Pairs:</b> Select and click "Remove Selected Pair"</li>
    </ul>

    <h3>Best Practices</h3>
    <ul>
        <li>Create only the pairs needed - each uses system resources</li>
        <li>Document which applications use which ports</li>
        <li>Remove unused pairs to keep the list manageable</li>
        <li>Restart applications after creating new pairs</li>
    </ul>

    <div class="warning-box">
    <h3>⚠️ CRITICAL: Port Number Stability</h3>
    <p><b>Port numbers CAN change after:</b></p>
    <ul>
        <li>System restarts</li>
        <li>Hardware configuration changes</li>
        <li>Windows updates</li>
        <li>Driver reinstallation</li>
    </ul>
    <p><b>IMPACT:</b> Automated systems and applications must be reconfigured when port numbers change. Always verify port assignments before critical operations.</p>
    </div>
    """

    @staticmethod
    def _get_routing_modes_content() -> str:
        """Routing modes detailed content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>Understanding Routing Modes</h2>

    <h3>Available Routing Modes</h3>

    <div class="info-box">
    <h3>One-Way Splitting (Default)</h3>
    <p><b>Data Flow:</b> Incoming Port → All Output Ports<br>
    <b>Use Case:</b> Broadcasting data from one source to multiple receivers<br>
    <b>Example:</b> GPS device sending location to multiple navigation applications</p>
    </div>

    <div class="info-box">
    <h3>Two-Way Communication</h3>
    <p><b>Data Flow:</b> Bidirectional between incoming and output ports<br>
    <b>Use Case:</b> When applications need to send commands back to the device<br>
    <b>Example:</b> Terminal program communicating with a modem</p>
    </div>

    <div class="info-box">
    <h3>Full Network Mode</h3>
    <p><b>Data Flow:</b> All ports can communicate with all other ports<br>
    <b>Use Case:</b> Creating a virtual serial network<br>
    <b>Example:</b> Multiple devices/applications all intercommunicating</p>
    </div>

    <h3>Choosing the Right Mode</h3>
    <table style="width: 100%; border-collapse: collapse;">
    <tr style="background-color: {AppColors.BACKGROUND_LIGHT};">
        <th style="padding: 8px; text-align: left;">Scenario</th>
        <th style="padding: 8px; text-align: left;">Recommended Mode</th>
    </tr>
    <tr>
        <td style="padding: 8px;">Simple data logging/monitoring</td>
        <td style="padding: 8px;">One-Way</td>
    </tr>
    <tr>
        <td style="padding: 8px;">Device control with feedback</td>
        <td style="padding: 8px;">Two-Way</td>
    </tr>
    <tr>
        <td style="padding: 8px;">Multi-device simulation</td>
        <td style="padding: 8px;">Full Network</td>
    </tr>
    </table>

    <div class="warning-box">
    <h3>Performance Note</h3>
    <p>Full Network mode uses more CPU resources. Use only when necessary.</p>
    </div>
    """

    @staticmethod
    def _get_flow_control_content() -> str:
        """Flow control detailed content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>Flow Control Settings</h2>

    <h3>What is Flow Control?</h3>
    <p>Flow control prevents data loss by coordinating when devices can send data. It functions like traffic lights for serial communication.</p>

    <h3>Hardware Flow Control (RTS/CTS)</h3>
    <div class="info-box">
    <p><b>RTS (Request To Send):</b> Sender signals it wants to transmit<br>
    <b>CTS (Clear To Send):</b> Receiver signals it's ready to receive</p>
    </div>

    <h3>When to Enable Flow Control</h3>
    <ul>
        <li>High-speed data transfers (>38400 baud)</li>
        <li>Large data volumes</li>
        <li>When devices explicitly support it</li>
        <li>Experiencing data loss or corruption</li>
    </ul>

    <h3>When NOT to Use Flow Control</h3>
    <ul>
        <li>Simple, low-speed connections</li>
        <li>Devices that don't support it</li>
        <li>When using 3-wire connections (TX, RX, GND only)</li>
    </ul>

    <h3>Configuration Options</h3>
    <ol>
        <li><b>Enable CTS Handshaking:</b> Standard flow control</li>
        <li><b>Disable Default Flow Control:</b> For custom implementations</li>
        <li><b>Echo Mode:</b> Special testing mode (not for normal use)</li>
    </ol>

    <div class="warning-box">
    <h3>Important</h3>
    <p>Both devices must support and be configured for the same flow control method!</p>
    </div>
    """

    @staticmethod
    def _get_baud_rates_content() -> str:
        """Baud rate configuration content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>Baud Rate Configuration</h2>

    <h3>Understanding Baud Rates</h3>
    <p>Baud rate is the speed of serial communication, measured in bits per second (bps).</p>

    <h3>Common Baud Rates</h3>
    <table style="width: 100%; border-collapse: collapse;">
    <tr style="background-color: {AppColors.BACKGROUND_LIGHT};">
        <th style="padding: 8px;">Baud Rate</th>
        <th style="padding: 8px;">Typical Use</th>
        <th style="padding: 8px;">Notes</th>
    </tr>
    <tr>
        <td style="padding: 8px;">9600</td>
        <td style="padding: 8px;">GPS, Arduino</td>
        <td style="padding: 8px;">Most compatible, slower</td>
    </tr>
    <tr>
        <td style="padding: 8px;">19200</td>
        <td style="padding: 8px;">Industrial devices</td>
        <td style="padding: 8px;">Good balance</td>
    </tr>
    <tr>
        <td style="padding: 8px;">38400</td>
        <td style="padding: 8px;">Modems</td>
        <td style="padding: 8px;">Medium speed</td>
    </tr>
    <tr>
        <td style="padding: 8px;">57600</td>
        <td style="padding: 8px;">Embedded systems</td>
        <td style="padding: 8px;">Higher speed</td>
    </tr>
    <tr>
        <td style="padding: 8px;">115200</td>
        <td style="padding: 8px;">Modern devices</td>
        <td style="padding: 8px;">Fast, common default</td>
    </tr>
    </table>

    <h3>Important Rules</h3>
    <div class="warning-box">
    <p><b>The baud rate MUST match the source device!</b><br>
    Mismatched baud rates result in garbage characters or no communication.</p>
    </div>

    <h3>Quick Tips</h3>
    <ul>
        <li>Check device manual for the correct baud rate</li>
        <li>Start with 9600 if uncertain - it's the most compatible</li>
        <li>Use "Set All" to quickly match all output ports</li>
        <li>Higher rates need better cable quality</li>
    </ul>
    """

    @staticmethod
    def _get_advanced_settings_content() -> str:
        """Advanced settings content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>Advanced Settings</h2>

    <div class="warning-box">
    <h3>Expert Users Only</h3>
    <p>These settings can affect system stability. Change only when the implications are understood.</p>
    </div>

    <h3>COM0COM Emulation Features</h3>

    <h4>Baud Rate Emulation (EmuBR)</h4>
    <ul>
        <li>Simulates physical port timing</li>
        <li>Useful for testing timing-sensitive applications</li>
        <li>Reduces performance - disable for maximum speed</li>
    </ul>

    <h4>Buffer Overrun Emulation</h4>
    <ul>
        <li>Simulates hardware buffer limitations</li>
        <li>Tests application error handling</li>
        <li>Can cause data loss - use only for testing</li>
    </ul>

    <h4>Exclusive Mode</h4>
    <ul>
        <li>Hides port until paired port is opened</li>
        <li>Prevents accidental connections</li>
        <li>May confuse some applications</li>
    </ul>

    <h4>Plug-In Mode</h4>
    <ul>
        <li>Dynamic port creation/removal</li>
        <li>Advanced scenario only</li>
        <li>Not compatible with all applications</li>
    </ul>

    <h3>HUB4COM Advanced Options</h3>
    <ul>
        <li><b>Custom Routes:</b> Use command line for complex routing</li>
        <li><b>Filters:</b> Apply data transformations</li>
        <li><b>Logging:</b> Enable for debugging</li>
    </ul>

    <div class="footer-box">
    <p>See the Command Reference section for detailed command-line options.</p>
    </div>
    """

    @staticmethod
    def _get_command_line_content() -> str:
        """Command line usage content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>Command Line Usage</h2>

    <h3>Running from Command Line</h3>
    <p>The Serial Port Splitter can be controlled via command line for automation.</p>

    <h3>Basic Commands</h3>
    <div style="background-color: {AppColors.GRAY_100}; padding: 10px; font-family: monospace;">
    # List all ports<br>
    hub4com.exe --list<br><br>

    # Simple one-way split<br>
    hub4com.exe COM1 COM3 COM4<br><br>

    # Two-way communication<br>
    hub4com.exe --bi-route=0:1 COM1 COM3
    </div>

    <h3>COM0COM Commands</h3>
    <div style="background-color: {AppColors.GRAY_100}; padding: 10px; font-family: monospace;">
    # List virtual pairs<br>
    setupc.exe list<br><br>

    # Create new pair<br>
    setupc.exe install PortName=COM10 PortName=COM11<br><br>

    # Remove pair<br>
    setupc.exe remove CNCA0
    </div>

    <h3>Automation Examples</h3>
    <h4>Batch File for Startup</h4>
    <div style="background-color: {AppColors.GRAY_100}; padding: 10px; font-family: monospace;">
    @echo off<br>
    echo Starting Serial Port Splitter...<br>
    start hub4com.exe --load=config.txt<br>
    echo Routing started!
    </div>

    <h4>PowerShell Script</h4>
    <div style="background-color: {AppColors.GRAY_100}; padding: 10px; font-family: monospace;">
    # Check if port exists<br>
    $ports = [System.IO.Ports.SerialPort]::getportnames()<br>
    if ($ports -contains "COM3") <br>
    &nbsp;&nbsp;Start-Process "hub4com.exe" -ArgumentList "COM3 COM10 COM11"<br>
    </div>
    """

    @staticmethod
    def _get_common_issues_content() -> str:
        """Common issues and solutions content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>Common Issues & Solutions</h2>

    <h3>"Access Denied" Error</h3>
    <div class="info-box">
    <b>Cause:</b> Port is already in use<br>
    <b>Solution:</b>
    <ol>
        <li>Close all applications using the port</li>
        <li>Check Task Manager for hidden processes</li>
        <li>Restart the application</li>
    </ol>
    </div>

    <h3>"Port Not Found"</h3>
    <div class="info-box">
    <b>Cause:</b> Port doesn't exist or driver issue<br>
    <b>Solution:</b>
    <ol>
        <li>Click "Refresh Ports"</li>
        <li>Check Device Manager for the port</li>
        <li>Reinstall COM0COM driver if virtual ports missing</li>
    </ol>
    </div>

    <h3>No Data Received</h3>
    <div class="info-box">
    <b>Cause:</b> Multiple possible causes<br>
    <b>Solution:</b>
    <ol>
        <li>Verify source device is sending data</li>
        <li>Check baud rate matches exactly</li>
        <li>Test with a terminal program first</li>
        <li>Verify cable connections (for physical ports)</li>
    </ol>
    </div>

    <h3>Garbage Characters</h3>
    <div class="info-box">
    <b>Cause:</b> Baud rate mismatch<br>
    <b>Solution:</b>
    <ol>
        <li>Double-check source device baud rate</li>
        <li>Try common rates: 9600, 19200, 115200</li>
        <li>Check data bits, parity, stop bits settings</li>
    </ol>
    </div>

    <h3>Application Can't Open Port</h3>
    <div class="info-box">
    <b>Cause:</b> Port permissions or visibility<br>
    <b>Solution:</b>
    <ol>
        <li>Run application as Administrator</li>
        <li>Disable Exclusive Mode in port settings</li>
        <li>Restart the application after creating ports</li>
    </ol>
    </div>
    """

    @staticmethod
    def _get_error_messages_content() -> str:
        """Error messages guide content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>Error Messages Guide</h2>

    <h3>Understanding Error Messages</h3>
    <p>This guide explains common error messages and their solutions.</p>

    <h3>Critical Errors</h3>

    <div class="warning-box">
    <h4>"Failed to start hub4com.exe"</h4>
    <p><b>Meaning:</b> The routing engine couldn't start<br>
    <b>Action:</b> Ensure hub4com.exe is in the application folder</p>
    </div>

    <div class="warning-box">
    <h4>"COM0COM driver not installed"</h4>
    <p><b>Meaning:</b> Virtual port driver is missing<br>
    <b>Action:</b> Restart app as Administrator for auto-installation</p>
    </div>

    <h3>Warning Messages</h3>

    <div class="info-box">
    <h4>"Port already in use"</h4>
    <p><b>Meaning:</b> Another application is using this port<br>
    <b>Action:</b> Choose a different port or close the other app</p>
    </div>

    <div class="info-box">
    <h4>"Baud rate mismatch detected"</h4>
    <p><b>Meaning:</b> Output ports have different baud rates<br>
    <b>Action:</b> Use "Set All" to synchronise rates</p>
    </div>

    <h3>Informational Messages</h3>
    <ul>
        <li><b>"Routing started successfully"</b> - Normal operation</li>
        <li><b>"Port scan complete"</b> - Refresh finished</li>
        <li><b>"Virtual pair created"</b> - New ports available</li>
    </ul>

    <h3>Critical Process Failures</h3>

    <div class="warning-box">
    <h4>"HUB4COM process terminated unexpectedly"</h4>
    <p><b>Immediate Action Required:</b></p>
    <ol>
        <li><b>Stop all data collection</b> - routing has failed</li>
        <li><b>Check Windows Event Viewer</b> for crash details</li>
        <li><b>Verify all output ports are accessible</b></li>
        <li><b>Restart routing service</b> from main application</li>
        <li><b>Monitor for repeated failures</b> - may indicate hardware issues</li>
    </ol>
    </div>

    <h3>Getting Help</h3>
    <p>If an error not listed here is encountered:</p>
    <ol>
        <li>Note the exact error message</li>
        <li>Check the application log file</li>
        <li>Try the troubleshooting steps in Quick Tips</li>
    </ol>
    """

    @staticmethod
    def _get_com0com_settings_content() -> str:
        """Get COM0COM settings help content"""
        return f"""
    {HTMLTheme.get_styles()}
    <h2>COM0COM Virtual Serial Port Settings Guide</h2>
    <h3>Overview</h3>
    <p>The COM0COM driver facilitates the creation of virtual serial port pairs. These pairs are interconnected by a virtual null-modem cable, meaning any data written to one port in a pair is instantaneously received by the other. This guide details the configuration settings available for these port pairs.</p>

    <h3>Port Display Format</h3>
    <p>Port pairs are displayed using the following convention:</p>
    <p style="margin-left: 20px;"><b>COM131 ⇄ COM132 [CNCA31 ⇄ CNCB31] [Features: Baud Rate Emulation]</b></p>
    <ul>
        <li><b>COM131 ⇄ COM132</b>: These are the system-level port names that will be visible to and used by applications.</li>
        <li><b>[CNCA31 ⇄ CNCB31]</b>: These are the internal driver names for the virtual port pair.</li>
        <li><b>[Features: ...]</b>: This section indicates which special emulation features are currently enabled for the port pair.</li>
    </ul>
    <p><b>Default Configuration:</b> This application creates port pairs using the CNCA31/CNCB31 and CNCA41/CNCB41 naming convention, which typically map to COM131/132 and COM141/142 respectively.</p>

    <h3>Configuration Settings</h3>
    <p>The following settings control the behaviour of the virtual serial ports to simulate physical hardware characteristics.</p>

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
        <li>Enable <b>Baud Rate Emulation</b> to validate application behaviour with realistic serial communication speeds.</li>
        <li>Enable <b>Buffer Overrun Emulation</b> to test an application's error and data loss handling logic.</li>
    </ul>

    <h3>Important Considerations</h3>
    <ul>
        <li>Configuration changes are applied to the driver immediately and do not require a system restart.</li>
        <li>Settings are applied symmetrically to both ports within a virtual pair.</li>
        <li>To ensure new settings are recognised, applications may need to close and reopen the serial port connection.</li>
        <li>The default configuration (all features disabled) is the most stable and suitable for the majority of use cases.</li>
    </ul>

    <p><i>Note: For more detailed technical information, double-click any port pair in the list.</i></p>
    """

    @staticmethod
    def _get_hub4com_routes_content() -> str:
        """Get HUB4COM route options help content"""
        return f"""
    {HTMLTheme.get_styles()}
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
        <li>Leave advanced options OFF unless there are specific needs</li>
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
            return f"{HTMLTheme.get_styles()}<pre>{content}</pre>"
        except:
            return f"{HTMLTheme.get_styles()}<p>HUB4COM reference file not found. Please ensure hub4comhelp.txt is in the application directory.</p>"
    
    @staticmethod
    def _get_com0com_reference_content() -> str:
        """Get COM0COM command reference content"""
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            help_file = os.path.join(script_dir, "com0com_help_command.txt")
            with open(help_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"{HTMLTheme.get_styles()}<pre>{content}</pre>"
        except:
            return f"{HTMLTheme.get_styles()}<p>COM0COM reference file not found. Please ensure com0com_help_command.txt is in the application directory.</p>"
    
    @staticmethod
    def _get_port_types_content() -> str:
        """Get port types and identification help content"""
        return f"""
{HTMLTheme.get_styles()}
<h2>Port Types & Identification Guide</h2>

<h3>Port Type Indicators</h3>

<h4>MOXA Network Device</h4>
<p><b>Description:</b> Network-attached serial device server<br>
<b>Important:</b> Make sure baud rate matches your source device<br>
<b>Common Use:</b> Remote serial device access over Ethernet</p>

<h4>Physical Port</h4>
<p><b>Description:</b> Hardware COM port (built-in or USB adapter)<br>
<b>Important:</b> Connected to real hardware, verify device baud rate<br>
<b>Common Use:</b> Direct connection to serial devices</p>

<h4>Virtual Port</h4>
<p><b>Description:</b> Software-created port for inter-application communication<br>
<b>Important:</b> No physical hardware involved<br>
<b>Common Use:</b> Application-to-application data transfer</p>

<h3>Baud Rate Guidelines</h3>
<ul>
    <li><b>Physical/MOXA Ports:</b> Must match the connected device's baud rate exactly</li>
    <li><b>Virtual Ports (EmuBR Disabled):</b> Data transfers instantly, baud rate setting ignored</li>
    <li><b>Virtual Ports (EmuBR Enabled):</b> Data transfer speed matches configured baud rate exactly - <b>CRITICAL</b> for timing-sensitive offshore equipment</li>
    <li><b>Default Configuration:</b> This application enables EmuBR by default for realistic timing behavior</li>
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
        return f"""
{HTMLTheme.get_styles()}
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
        return f"""
{HTMLTheme.get_styles()}
<h2>Quick Tips & Troubleshooting</h2>

<h3>Quick Start</h3>
<ol>
    <li>Create virtual port pairs for your applications</li>
    <li>Select your incoming data source port</li>
    <li>Add outgoing ports for each application</li>
    <li>Set appropriate baud rates</li>
    <li>Start routing and connect your applications</li>
</ol>

<h3>Common Issues</h3>

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

<h3>Pro Tips</h3>
<ul>
    <li><b>Test First:</b> Use a simple terminal program to verify data flow before adding complexity</li>
    <li><b>Baud Rate Sync:</b> Use the "Set All" button to quickly match all outgoing rates</li>
    <li><b>Flow Control:</b> Enable CTS handshaking only if your source device supports it</li>
    <li><b>Port Numbers:</b> Note assigned port numbers before connecting applications</li>
    <li><b>System Tray:</b> The application continues running when minimized to system tray</li>
</ul>

<h3>Best Practices</h3>
<ul>
    <li>Create descriptive names for virtual pairs</li>
    <li>Document your port assignments</li>
    <li>Test configuration before deploying</li>
    <li>Keep backups of working configurations</li>
    <li>Monitor system resources during heavy data flow</li>
</ul>
"""


class BreadcrumbWidget(QWidget):
    """Windows 10 style breadcrumb navigation"""
    
    breadcrumbClicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize breadcrumb UI"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Home button
        self.home_btn = ThemeManager.create_button("Home", style_type="compact")
        self.home_btn.clicked.connect(lambda: self.breadcrumbClicked.emit("home"))
        self.layout.addWidget(self.home_btn)
        
        # Separator
        self.add_separator()
        
        # Category label
        self.category_label = QLabel("")
        self.category_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                padding: 0 8px;
                font-family: {AppFonts.DEFAULT_FAMILY};
            }}
        """)
        self.layout.addWidget(self.category_label)
        
        # Topic separator
        self.topic_separator = QLabel(" › ")
        self.topic_separator.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                padding: 0 4px;
            }}
        """)
        self.topic_separator.setVisible(False)
        self.layout.addWidget(self.topic_separator)
        
        # Topic label
        self.topic_label = QLabel("")
        self.topic_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.ACCENT_BLUE};
                padding: 0 8px;
                font-weight: bold;
            }}
        """)
        self.layout.addWidget(self.topic_label)
        
        self.layout.addStretch()
        
    def add_separator(self):
        """Add a separator between breadcrumb items"""
        sep = QLabel(" › ")
        sep.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                padding: 0 4px;
            }}
        """)
        self.layout.addWidget(sep)
        
    def update_breadcrumb(self, category: str, topic: str):
        """Update breadcrumb display"""
        self.category_label.setText(category)
        self.topic_label.setText(topic)
        self.topic_separator.setVisible(bool(topic))


class SearchResultsWidget(QListWidget):
    """Search results dropdown widget"""
    
    resultSelected = pyqtSignal(HelpTopic)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setMaximumHeight(240)
        self.itemClicked.connect(self._on_item_clicked)
        
        # Apply styling
        self.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BACKGROUND_WHITE};
                outline: none;
            }}
            QListWidget::item {{
                padding: {AppDimensions.PADDING_MEDIUM};
                border-bottom: 1px solid {AppColors.BORDER_LIGHT};
            }}
            QListWidget::item:hover {{
                background-color: {AppColors.BUTTON_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: {AppColors.SELECTION_BG};
                color: {AppColors.SELECTION_TEXT};
            }}
        """)
        
    def _on_item_clicked(self, item):
        """Handle item click"""
        if hasattr(item, 'topic'):
            self.resultSelected.emit(item.topic)
            self.hide()


class UnifiedHelpDialog(QDialog):
    """Enhanced Windows 10 style help dialog"""
    
    def __init__(self, parent=None, initial_topic: HelpTopic = HelpTopic.QUICK_START):
        super().__init__(parent)
        self.current_topic = initial_topic
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.init_ui()
        self.load_topic(initial_topic)
        
    def init_ui(self):
        """Initialize the enhanced help interface"""
        self.setWindowTitle("Help - Serial Port Splitter")
        self.setMaximumSize(1280, 768)
        self.resize(1000, 500)
        
        # Apply dialog styling
        ThemeManager.style_dialog(self)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        header_widget = self.create_header_section()
        main_layout.addWidget(header_widget)
        
        # Add separator
        main_layout.addWidget(ThemeManager.create_separator("horizontal"))
        
        # Content section with splitter
        content_widget = self.create_content_section()
        main_layout.addWidget(content_widget)

    def create_header_section(self) -> QWidget:
        """Create header with breadcrumb and search"""
        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)
        
        # Back button
        self.back_btn = ThemeManager.create_icon_button("arrow_left", "Go back", "medium")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)  # Disable initially
        layout.addWidget(self.back_btn)
        
        # Breadcrumb navigation
        self.breadcrumb = BreadcrumbWidget()
        self.breadcrumb.breadcrumbClicked.connect(self.handle_breadcrumb_click)
        layout.addWidget(self.breadcrumb)
        
        layout.addStretch()
        
        # Search box
        self.search_box = ThemeManager.create_lineedit()
        self.search_box.setPlaceholderText("Search help topics...")
        self.search_box.setMaximumWidth(200)
        self.search_box.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_box)
        
        # Search results dropdown
        self.search_results = SearchResultsWidget(self.search_box)
        self.search_results.resultSelected.connect(self.load_topic)
        self.search_results.hide()
        
        return header
        
    def create_content_section(self) -> QWidget:
        """Create main content area with navigation and display"""
        content_widget = QWidget()
        layout = QHBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter
        splitter = ThemeManager.create_splitter(Qt.Orientation.Horizontal)
        
        # Left panel - Navigation
        nav_widget = self.create_navigation_panel()
        splitter.addWidget(nav_widget)
        
        # Right panel - Content display
        display_widget = self.create_display_panel()
        splitter.addWidget(display_widget)
        
        # Configure splitter
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([180, 720])
        
        layout.addWidget(splitter)
        return content_widget
        
    def create_navigation_panel(self) -> QWidget:
        """Create Windows Settings style navigation panel"""
        nav_widget = QWidget()
        nav_widget.setMinimumWidth(240)
        nav_widget.setMaximumWidth(320)
        nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border-right: 1px solid {AppColors.BORDER_LIGHT};
            }}
        """)
        
        layout = QVBoxLayout(nav_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Topics list
        self.topics_list = QListWidget()
        self.topics_list.setFrameShape(QFrame.Shape.NoFrame)
        self.topics_list.itemClicked.connect(self.on_topic_clicked)
        
        # Custom styling for navigation list
        self.topics_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border: none;
                outline: none;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
            }}
            QListWidget::item {{
                padding: {AppDimensions.PADDING_LARGE} {AppDimensions.PADDING_LARGE};
                border: none;
                color: {AppColors.TEXT_DEFAULT};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {AppColors.BUTTON_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: {AppColors.BACKGROUND_WHITE};
                color: {AppColors.ACCENT_BLUE};
                font-weight: bold;
                border-left: 3px solid {AppColors.ACCENT_BLUE};
            }}
            QListWidget::item:disabled {{
                color: {AppColors.TEXT_DISABLED};
                font-weight: bold;
                padding: {AppDimensions.PADDING_LARGE} {AppDimensions.PADDING_LARGE} {AppDimensions.PADDING_MEDIUM} {AppDimensions.PADDING_LARGE};
                background-color: transparent;
            }}
        """)
        
        # Populate navigation
        self.populate_navigation()
        
        layout.addWidget(self.topics_list)
        return nav_widget
        
    def create_display_panel(self) -> QWidget:
        """Create content display panel"""
        display_widget = QWidget()
        display_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_WHITE};
            }}
        """)
        
        layout = QVBoxLayout(display_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Content display
        self.content_display = ThemeManager.create_html_content_widget(max_height=1200)
        self.content_display.setMinimumHeight(480)
        self.content_display.setStyleSheet(self.content_display.styleSheet() + AppStyles.scroll_area())
        
        # Related topics section
        self.related_widget = self.create_related_topics_section()
        self.related_widget.setVisible(False)
        
        layout.addWidget(self.content_display)
        layout.addWidget(self.related_widget)
        layout.addStretch()
        
        return display_widget
        
    def create_related_topics_section(self) -> QWidget:
        """Create related topics section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header_label = QLabel("Related Topics")
        header_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12pt;
                font-weight: bold;
                color: {AppColors.TEXT_DEFAULT};
                margin-top: 20px;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(header_label)
        
        # Related topics container
        self.related_container = QHBoxLayout()
        self.related_container.setSpacing(10)
        layout.addLayout(self.related_container)
        
        return widget
          
    def populate_navigation(self):
        """Populate navigation list with categories and topics"""
        self.topics_list.clear()
        
        categories = HelpContentRegistry.get_categories_with_topics()
        
        # Fixed category order
        category_order = [
            HelpCategory.GETTING_STARTED,
            HelpCategory.VIRTUAL_PORTS,
            HelpCategory.ROUTING,
            HelpCategory.CONFIGURATION,
            HelpCategory.REFERENCE,
            HelpCategory.TROUBLESHOOTING
        ]
        
        for category in category_order:
            if category in categories:
                # Add category header
                category_name, icon = category
                category_item = NavigationItem(category_name, None, True, icon)
                self.topics_list.addItem(category_item)
                
                # Add topics under category
                for topic, title in categories[category]:
                    topic_item = NavigationItem(title, topic, False)
                    self.topics_list.addItem(topic_item)
        
    def load_topic(self, topic: HelpTopic):
        """Load and display help content for specified topic"""
        self.current_topic = topic
        content_info = HelpContentRegistry.get_content(topic)
        
        # Update display
        self.content_display.setHtml(content_info["content"])
        self.setWindowTitle(f"Help - {content_info['title']}")
        
        # Update breadcrumb
        category_name, _ = content_info["category"]
        self.breadcrumb.update_breadcrumb(category_name, content_info["title"])
        
        # Update selection in navigation
        for i in range(self.topics_list.count()):
            item = self.topics_list.item(i)
            if hasattr(item, 'topic') and item.topic == topic:
                self.topics_list.setCurrentItem(item)
                break
        
        # Update related topics
        self.update_related_topics(content_info.get("related", []))
        
        # Highlight search term if exists
        if self.search_box.text():
            SearchHighlighter.highlight_text(self.content_display, self.search_box.text())
        
    def update_related_topics(self, related_topics: List[HelpTopic]):
        """Update related topics display"""
        # Clear existing
        while self.related_container.count():
            item = self.related_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not related_topics:
            self.related_widget.setVisible(False)
            return
            
        self.related_widget.setVisible(True)
        
        # Add related topic buttons
        for topic in related_topics[:3]:  # Show max 3 related topics
            content = HelpContentRegistry.get_content(topic)
            btn = ThemeManager.create_button(
                content["title"], 
                lambda checked, t=topic: self.load_topic(t),
                "compact"
            )
            self.related_container.addWidget(btn)
            
        self.related_container.addStretch()
        
    def on_topic_clicked(self, item):
        """Handle topic selection from navigation"""
        if hasattr(item, 'topic') and item.topic and not item.is_category:
            self.load_topic(item.topic)
            
    def on_search_text_changed(self, text):
        """Handle search text changes with debouncing"""
        self.search_timer.stop()
        if text:
            self.search_timer.start(300)  # 300ms delay
        else:
            self.search_results.hide()
            self.search_results.clear()
            
    def perform_search(self):
        """Perform search and show results"""
        search_term = self.search_box.text()
        if not search_term:
            return
            
        results = HelpContentRegistry.search_topics(search_term)
        
        self.search_results.clear()
        
        if results:
            # Position dropdown
            pos = self.search_box.mapToGlobal(self.search_box.rect().bottomLeft())
            self.search_results.move(pos)
            self.search_results.resize(self.search_box.width(), min(200, len(results) * 40))
            
            # Add results
            for topic, score in results[:5]:  # Show top 5 results
                content = HelpContentRegistry.get_content(topic)
                item = QListWidgetItem(f"{content['title']}")
                item.topic = topic
                self.search_results.addItem(item)
                
            self.search_results.show()
            
    def handle_breadcrumb_click(self, target):
        """Handle breadcrumb navigation"""
        if target == "home":
            self.load_topic(HelpTopic.QUICK_START)
            
    def go_back(self):
        """Navigate back (placeholder for history)"""
        # Could implement navigation history here
        pass
        
    def feedback_yes(self):
        """Handle positive feedback"""
        # Show brief thank you message
        QApplication.beep()
        
    def feedback_no(self):
        """Handle negative feedback"""
        # Could open feedback form
        QApplication.beep()
        
    def print_topic(self):
        """Print current topic"""
        # Implement print functionality
        QApplication.beep()
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Escape:
            if self.search_results.isVisible():
                self.search_results.hide()
            else:
                self.close()
        elif event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.search_box.setFocus()
            self.search_box.selectAll()
        else:
            super().keyPressEvent(event)


class HelpManager:
    """Enhanced help system manager"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def show_help(topic: HelpTopic = HelpTopic.QUICK_START, parent=None):
        """Show help dialog for specified topic"""
        dialog = UnifiedHelpDialog(parent, topic)
        dialog.exec()
    
    @staticmethod
    def get_tooltip(tooltip_type: str, **kwargs) -> str:
        """Get formatted tooltip text"""
        tooltips = {
            "pair_tooltip": "Port A ({port_a}): {params_a}\nPort B ({port_b}): {params_b}\n\nRight-click or use 'Configure Features' to modify settings\nClick 'Help' button for detailed explanations of all features",
            "port_type_moxa": "Moxa Network Device",
            "port_type_physical": "Physical Device",
            "port_type_virtual": "Virtual Device"
        }
        template = tooltips.get(tooltip_type, "")
        return template.format(**kwargs)