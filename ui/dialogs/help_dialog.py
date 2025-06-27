#!/usr/bin/env python3
"""
Help Dialog for Hub4com GUI
Displays comprehensive help information for COM0COM settings
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import Qt

from ui.theme.theme import ThemeManager, AppStyles, AppFonts, AppDimensions, AppColors


class HelpDialog(QDialog):
    """Dialog for displaying COM0COM help information"""
    
    def __init__(self, parent=None, title="Help", content="Help information goes here."):
        super().__init__(parent)
        self.help_title = title
        self.help_content = content
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(self.help_title)
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Create scrollable text area for help content
        help_text = QTextEdit()
        help_text.setFont(AppFonts.CONSOLE_LARGE)
        help_text.setReadOnly(True)
        help_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {AppColors.BORDER_DEFAULT};
                padding: 10px;
                background-color: {AppColors.BACKGROUND_WHITE};
                color: {AppColors.TEXT_DEFAULT};
                line-height: 1.4;
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: 10pt;
            }}
        """)
        
        help_text.setHtml(self.help_content)
        layout.addWidget(help_text)
        
class Com0ComHelpDialog(HelpDialog):
    """Specialized help dialog for COM0COM settings"""
    
    def __init__(self, parent=None):
        help_content = """
<h2>COM0COM Virtual Serial Port Settings Guide</h2>
        <h3>Overview</h3>
        <p>The COM0COM driver facilitates the creation of virtual serial port pairs. These pairs are interconnected by a virtual null-modem cable, meaning any data written to one port in a pair is instantaneously received by the other. This guide details the configuration settings available for these port pairs.</p>

        <h3>Port Display Format</h3>
        <p>Port pairs are displayed using the following convention:</p>
        <p style="margin-left: 20px;"><b>COM3 &harr; COM4 [CNCA0 &harr; CNCB0] [Features: Baud Rate Emulation]</b></p>
        <ul>
            <li><b>COM3 &harr; COM4</b>: These are the system-level port names that will be visible to and used by your applications.</li>
            <li><b>[CNCA0 &harr; CNCB0]</b>: These are the internal driver names for the virtual port pair.</li>
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
        
        super().__init__(
            parent=parent,
            title="COM0COM Virtual Port Settings - Help Guide",
            content=help_content
        )