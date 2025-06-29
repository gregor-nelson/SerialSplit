#!/usr/bin/env python3
"""
Hub4com GUI Launcher with Moxa Scanner and Baud Rate Support
A PyQt6 interface to configure and start hub4com for COM port routing
Includes comprehensive port scanning with Moxa device server detection and baud rate configuration

Main entry point for the application
"""

import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu 
from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter, QBrush, QPen, QLinearGradient, QAction
from PyQt6.QtCore import Qt
from ui.gui import Hub4comGUI


def create_app_icon():
    """Create a programmatic application icon for the system tray"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    
    # Gradient background
    gradient = QLinearGradient(0, 0, 64, 64)
    gradient.setColorAt(0, QColor("#282c34"))  # Match One Dark theme
    gradient.setColorAt(1, QColor("#1c2526"))
    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(Qt.PenStyle.NoPen))
    painter.drawRoundedRect(4, 4, 56, 56, 12, 12)
    
    # Draw simple icon (e.g., a stylized 'H' for Hub4com)
    painter.setPen(QPen(QColor("#abb2bf"), 2))
    painter.setBrush(QBrush(Qt.GlobalColor.white))
    painter.drawRoundedRect(18, 12, 28, 36, 3, 3)
    
    # Draw 'H' symbol
    painter.setPen(QPen(QColor("#abb2bf"), 3))
    painter.drawLine(24, 18, 24, 42)  # Left vertical
    painter.drawLine(40, 18, 40, 42)  # Right vertical
    painter.drawLine(24, 30, 40, 30)  # Horizontal bar
    
    painter.end()
    return QIcon(pixmap)


class Hub4comGUIWithTray(Hub4comGUI):
    """Subclass of Hub4comGUI to add system tray functionality"""
    def __init__(self, tray_icon):
        super().__init__()
        self.tray_icon = tray_icon

    def show_window(self):
        """Show and raise the main window"""
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        """Handle close event - minimize to tray instead of closing"""
        if self.tray_icon and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Serial Port Splitter",
                "Application minimized to tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

def main():
    """Main entry point for the Hub4com Launcher application"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Prevent app from quitting when window is closed
    
    # Set application properties
    app.setApplicationName("Hub4com Launcher with Port Scanner & Baud Rate Support")
    app.setApplicationVersion("0.1")

    # Create system tray icon
    app_icon = create_app_icon()
    tray_icon = QSystemTrayIcon(app_icon)
    
    # Create tray menu
    tray_menu = QMenu()
    show_action = QAction("Show", tray_icon)
    quit_action = QAction("Quit", tray_icon)
    tray_menu.addAction(show_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)
    
    # Create and show main window
    window = Hub4comGUIWithTray(tray_icon)
    window.setWindowIcon(app_icon)
    
    # Connect tray actions
    show_action.triggered.connect(window.show_window)
    quit_action.triggered.connect(app.quit)
    tray_icon.activated.connect(lambda reason: window.show_window() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.setToolTip("Virtual Port Splitter")
    tray_icon.show()
    
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()