#!/usr/bin/env python3
"""
Hub4com GUI Launcher with Moxa Scanner and Baud Rate Support
A PyQt6 interface to configure and start hub4com for COM port routing
Includes comprehensive port scanning with Moxa device server detection and baud rate configuration

Main entry point for the application
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.gui import Hub4comGUI


def main():
    """Main entry point for the Hub4com Launcher application"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Hub4com Launcher with Port Scanner & Baud Rate Support")
    app.setApplicationVersion("0.1")
    
    # Create and show main window
    window = Hub4comGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()