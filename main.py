#!/usr/bin/env python3
"""
Hub4com GUI Launcher with Moxa Scanner and Baud Rate Support
A PyQt6 interface to configure and start hub4com for COM port routing
Includes comprehensive port scanning with Moxa device server detection and baud rate configuration

Main entry point for the application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu 
from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter, QBrush, QPen, QLinearGradient, QAction, QFontDatabase
from PyQt6.QtCore import Qt
from PyQt6.QtSvg import QSvgRenderer # <-- Import for SVG rendering
from ui.gui import Hub4comGUI

# --- SVG Icon Content ---
# The polished SVG icon is stored here as a multi-line string.
APP_ICON_SVG = """

<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Vibrant gradients for visibility on taskbar -->
    <linearGradient id="mainGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00a8ff;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#0078ff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0052cc;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="highlightGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </linearGradient>
    
    <linearGradient id="portGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#00d9ff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#00a8ff;stop-opacity:1" />
    </linearGradient>
    
    <!-- Subtle shadow for depth -->
    <filter id="shadow">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity="0.3"/>
    </filter>
    
    <!-- Strong glow for visibility -->
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Scaled up design to fill most of the 256x256 space -->
  <g transform="translate(128, 128)">
    
    <!-- Main connector body - much larger -->
    <g transform="translate(-100, 0)">
      <!-- Port housing -->
      <rect x="-25" y="-50" width="75" height="100" rx="12" fill="url(#mainGradient)" filter="url(#shadow)"/>
      
      <!-- Highlight for 3D effect -->
      <rect x="-25" y="-50" width="75" height="50" rx="12" fill="url(#highlightGradient)"/>
      
      <!-- Simplified pin representation -->
      <rect x="-12" y="-32" width="10" height="64" rx="3" fill="#ffffff" opacity="0.9"/>
      <rect x="2" y="-32" width="10" height="64" rx="3" fill="#ffffff" opacity="0.9"/>
      <rect x="16" y="-32" width="10" height="64" rx="3" fill="#ffffff" opacity="0.9"/>
    </g>
    
    <!-- Central hub -->
    <circle cx="0" cy="0" r="22" fill="url(#portGradient)" filter="url(#glow)"/>
    <circle cx="0" cy="0" r="11" fill="#ffffff" opacity="0.8"/>
    
    <!-- Bold connection lines -->
    <!-- Main trunk -->
    <rect x="-50" y="-10" width="50" height="20" fill="url(#mainGradient)"/>
    
    <!-- Three output paths - thicker and longer -->
    <!-- Top -->
    <path d="M 0 0 L 40 -55 L 85 -55" stroke="url(#mainGradient)" stroke-width="20" stroke-linecap="round" fill="none"/>
    <!-- Middle -->
    <rect x="0" y="-10" width="85" height="20" fill="url(#mainGradient)"/>
    <!-- Bottom -->
    <path d="M 0 0 L 40 55 L 85 55" stroke="url(#mainGradient)" stroke-width="20" stroke-linecap="round" fill="none"/>
    
    <!-- Output nodes -->
    <g>
      <!-- Top -->
      <circle cx="95" cy="-55" r="18" fill="url(#portGradient)" filter="url(#shadow)"/>
      <circle cx="95" cy="-55" r="9" fill="#ffffff" opacity="0.9"/>
      
      <!-- Middle -->
      <circle cx="95" cy="0" r="18" fill="url(#portGradient)" filter="url(#shadow)"/>
      <circle cx="95" cy="0" r="9" fill="#ffffff" opacity="0.9"/>
      
      <!-- Bottom -->
      <circle cx="95" cy="55" r="18" fill="url(#portGradient)" filter="url(#shadow)"/>
      <circle cx="95" cy="55" r="9" fill="#ffffff" opacity="0.9"/>
    </g>
    
    <!-- Active indicator dots - larger -->
    <circle cx="-40" cy="0" r="6" fill="#00ff88" opacity="0.8">
      <animate attributeName="opacity" values="0.8;0.3;0.8" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="0" cy="0" r="5" fill="#00ff88" opacity="0.8">
      <animate attributeName="opacity" values="0.3;0.8;0.3" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="40" cy="0" r="6" fill="#00ff88" opacity="0.8">
      <animate attributeName="opacity" values="0.8;0.3;0.8" dur="2s" repeatCount="indefinite" begin="1s"/>
    </circle>
  </g>
  
  <!-- Optional subtle outer glow for extra presence -->
  <circle cx="128" cy="128" r="120" fill="none" stroke="url(#mainGradient)" stroke-width="2" opacity="0.1"/>
</svg>
"""


def load_inter_font():
    """Load Poppins font files and register them with the application"""
    font_dir = Path(__file__).parent / "ui" / "fonts"
    
    if not font_dir.exists():
        print("Warning: Font directory not found, using system fonts")
        return False
    
    # Poppins font variants to load
    font_files = [
        "Poppins-Regular.ttf",
        "Poppins-Bold.ttf", 
        "Poppins-SemiBold.ttf",
        "Poppins-Medium.ttf"
    ]
    
    fonts_loaded = 0
    for font_file in font_files:
        font_path = font_dir / font_file
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                fonts_loaded += 1
                families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"Loaded font: {font_file} -> {families}")
            else:
                print(f"Failed to load font: {font_file}")
        else:
            print(f"Font file not found: {font_file}")
    
    return fonts_loaded > 0


def create_app_icon():
    """Create the application icon from the SVG data."""
    # Convert the SVG string to bytes
    svg_bytes = APP_ICON_SVG.encode('utf-8')

    # Create an SVG renderer
    renderer = QSvgRenderer(svg_bytes)
    
    # Create a pixmap to render the SVG onto. 
    # Using a larger size like 256x256 ensures high quality.
    pixmap = QPixmap(256, 256)
    pixmap.fill(Qt.GlobalColor.transparent) # Ensure background is transparent
    
    # Create a QPainter to draw the SVG onto the pixmap
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    # Return a QIcon created from our high-quality pixmap
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
    app.setQuitOnLastWindowClosed(False) # Prevent app from quitting when window is closed
    
    # Use Windows 10 system fonts (Segoe UI) - no custom font loading needed
    # load_inter_font()
    
    # Set application properties
    app.setApplicationName("Hub4com Launcher with Port Scanner & Baud Rate Support")
    app.setApplicationVersion("0.1")

    # Create system tray icon using the new SVG-based function
    # Note: Ensure you have the Qt SVG module installed: pip install PyQt6-Svg
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
