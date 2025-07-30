#!/usr/bin/env python3
"""
Serial Terminal - Standalone Application
A PyQt6 serial terminal application with split pane support and advanced formatting.

This is a standalone entry point for the terminal functionality,
while keeping the original terminal_dialog.py unchanged for cross-compatibility.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter, QFontDatabase, QFont, QDesktopServices, QCursor
from PyQt6.QtCore import Qt, QTimer, QUrl, QRect
from PyQt6.QtSvg import QSvgRenderer
from ui.dialogs.terminal_dialog import SerialMonitorWindow
from ui.theme.theme import ThemeManager, AppColors, AppFonts

# --- Clean GitHub SVG Icon ---
GITHUB_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path fill="{color}" d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.300 24 12c0-6.627-5.373-12-12-12z"/>
</svg>
"""

# --- Terminal-specific SVG Icon ---
# Modified version of the main app icon with terminal-specific styling
TERMINAL_ICON_SVG = """
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Terminal-specific gradients -->
    <linearGradient id="terminalGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00ff88;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#00cc66;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#009944;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="terminalHighlight" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </linearGradient>
    
    <!-- Terminal screen effect -->
    <filter id="screenGlow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <filter id="shadow">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-opacity="0.3"/>
    </filter>
  </defs>
  
  <!-- Terminal screen representation -->
  <g transform="translate(128, 128)">
    
    <!-- Terminal frame -->
    <rect x="-100" y="-80" width="200" height="160" rx="15" fill="#1a1a1a" filter="url(#shadow)"/>
    <rect x="-95" y="-75" width="190" height="150" rx="10" fill="#000000"/>
    
    <!-- Terminal screen -->
    <rect x="-85" y="-60" width="170" height="100" rx="5" fill="#0d1117" filter="url(#screenGlow)"/>
    
    <!-- Terminal text lines -->
    <g fill="url(#terminalGradient)" font-family="monospace" font-size="10">
      <text x="-75" y="-40">$ serial-terminal</text>
      <text x="-75" y="-25">Connected: COM3</text>
      <text x="-75" y="-10">Baud: 115200</text>
      <text x="-75" y="5">Data: 8N1</text>
      <text x="-75" y="20">Status: Ready</text>
    </g>
    
    <!-- Cursor blink -->
    <rect x="-20" y="15" width="8" height="12" fill="url(#terminalGradient)">
      <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
    </rect>
    
    <!-- Control buttons -->
    <g>
      <!-- Power button -->
      <circle cx="70" cy="-55" r="8" fill="url(#terminalGradient)" opacity="0.8"/>
      <circle cx="70" cy="-55" r="4" fill="#ffffff" opacity="0.9"/>
      
      <!-- Activity indicators -->
      <circle cx="55" cy="-55" r="4" fill="#ff4444">
        <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/>
      </circle>
      <circle cx="85" cy="-55" r="4" fill="#44ff44">
        <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
      </circle>
    </g>
    
    <!-- Bottom edge highlight -->
    <rect x="-100" y="60" width="200" height="20" rx="15" fill="url(#terminalHighlight)"/>
    
    <!-- Connection ports -->
    <g transform="translate(0, 85)">
      <rect x="-15" y="-5" width="30" height="10" rx="5" fill="url(#terminalGradient)"/>
      <rect x="-12" y="-3" width="6" height="6" rx="2" fill="#ffffff" opacity="0.9"/>
      <rect x="-2" y="-3" width="6" height="6" rx="2" fill="#ffffff" opacity="0.9"/>
      <rect x="8" y="-3" width="6" height="6" rx="2" fill="#ffffff" opacity="0.9"/>
    </g>
  </g>
</svg>
"""


def load_terminal_fonts():
    """Load fonts for terminal application (same as main app)"""
    font_dir = Path(__file__).parent / "ui" / "fonts"
    
    if not font_dir.exists():
        print("Warning: Font directory not found, using system fonts")
        return False
    
    font_files = [
        "Inter-Regular.ttf",
        "Inter-Bold.ttf", 
        "inter-SemiBold.ttf",
        "Inter-Medium.ttf"
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


def create_terminal_icon():
    """Create the terminal application icon from SVG data"""
    svg_bytes = TERMINAL_ICON_SVG.encode('utf-8')
    renderer = QSvgRenderer(svg_bytes)
    
    pixmap = QPixmap(256, 256)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    return QIcon(pixmap)


def setup_terminal_dark_mode(app):
    """Apply dark mode palette for terminal application (same as main app)"""
    palette = QPalette()
    
    # Main color roles
    palette.setColor(QPalette.ColorRole.Window, QColor(AppColors.BACKGROUND_LIGHT))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(AppColors.TEXT_DEFAULT))
    palette.setColor(QPalette.ColorRole.Base, QColor(AppColors.BACKGROUND_WHITE))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(AppColors.BACKGROUND_LIGHT))
    palette.setColor(QPalette.ColorRole.Text, QColor(AppColors.TEXT_DEFAULT))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff6b6b"))
    palette.setColor(QPalette.ColorRole.Button, QColor(AppColors.BUTTON_DEFAULT))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(AppColors.TEXT_DEFAULT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(AppColors.SELECTION_BG))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(AppColors.SELECTION_TEXT))
    
    # Tooltip colors
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(AppColors.BACKGROUND_TOOLTIP))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(AppColors.TEXT_TOOLTIP))
    
    # Link colors
    palette.setColor(QPalette.ColorRole.Link, QColor(AppColors.ACCENT_BLUE))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(AppColors.ACCENT_PURPLE))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(AppColors.TEXT_DISABLED))
    
    # 3D effect colors
    palette.setColor(QPalette.ColorRole.Light, QColor("#555555"))
    palette.setColor(QPalette.ColorRole.Midlight, QColor("#4a4a4a"))
    palette.setColor(QPalette.ColorRole.Dark, QColor("#2a2a2a"))
    palette.setColor(QPalette.ColorRole.Mid, QColor("#353535"))
    palette.setColor(QPalette.ColorRole.Shadow, QColor("#1a1a1a"))
    
    # Disabled state colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(AppColors.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(AppColors.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(AppColors.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(AppColors.BACKGROUND_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(AppColors.BACKGROUND_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(AppColors.BACKGROUND_DISABLED))
    
    # Inactive state colors
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(AppColors.BACKGROUND_LIGHT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(AppColors.TEXT_DEFAULT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(AppColors.BACKGROUND_WHITE))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(AppColors.TEXT_DEFAULT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(AppColors.BUTTON_DEFAULT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(AppColors.TEXT_DEFAULT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor("#4a4a4a"))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(AppColors.TEXT_DEFAULT))
    
    app.setPalette(palette)


class TerminalSplashScreen(QSplashScreen):
    """Professional Windows-style splash screen for Serial Terminal"""
    
    def __init__(self, pixmap):
        super().__init__(pixmap)
        
        # Window flags for clean appearance
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Status and progress tracking
        self.status_text = "Loading components..."
        self.progress = 0
        self.version_text = "Version 1.0"
        
        # Apply professional theme styling
        self.setStyleSheet(f"""
            QSplashScreen {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border: 1px solid {AppColors.BORDER_DEFAULT};
            }}
        """)
    
    def set_progress(self, value):
        """Set progress value (0-100)"""
        self.progress = max(0, min(100, value))
        self.update()
    
    def update_status(self, status):
        """Update status text"""
        self.status_text = status
        self.update()
    
    def paintEvent(self, event):
        """Professional Windows-style splash screen paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get splash screen dimensions
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        # Draw background
        painter.fillRect(rect, QColor(AppColors.BACKGROUND_LIGHT))
        
        # Application name in top-left (no icon)
        name_font = QFont(AppFonts.DEFAULT_FAMILY, 12, QFont.Weight.Medium)  # 12pt matches CAPTION_SIZE
        painter.setFont(name_font)
        painter.setPen(QColor(AppColors.TEXT_DEFAULT))
        painter.drawText(20, 32, "Serial Terminal")
        
        # Version text below name using theme font sizes
        version_font = QFont(AppFonts.DEFAULT_FAMILY, 9)  # 9pt matches DEFAULT_SIZE
        painter.setFont(version_font)
        painter.setPen(QColor(AppColors.TEXT_DISABLED))  # Use theme disabled color for muted text
        painter.drawText(20, 48, self.version_text)
        
        # Status text (loading message) using theme font sizes
        status_font = QFont(AppFonts.DEFAULT_FAMILY, 9)  # 9pt matches DEFAULT_SIZE
        painter.setFont(status_font)
        painter.setPen(QColor(AppColors.ACCENT_BLUE))
        painter.drawText(20, height - 45, self.status_text)
        
        # Progress bar
        bar_width = width - 40
        bar_height = 2
        bar_x = 20
        bar_y = height - 25
        
        # Background bar
        painter.fillRect(bar_x, bar_y, bar_width, bar_height, QColor(AppColors.BACKGROUND_WHITE))
        
        # Progress bar fill
        progress_width = int(bar_width * self.progress / 100)
        painter.fillRect(bar_x, bar_y, progress_width, bar_height, QColor(AppColors.ACCENT_BLUE))
        
        painter.end()
    
    def mousePressEvent(self, event):
        """Handle mouse clicks (minimal for professional appearance)"""
        super().mousePressEvent(event)
    
    def finish_loading(self):
        """Clean up splash screen"""
        pass


def create_splash_screen():
    """Create and return the professional splash screen"""
    # Create a smaller, professional splash screen (320x180px)
    splash_pixmap = QPixmap(320, 180)
    splash_pixmap.fill(Qt.GlobalColor.transparent)
    
    # Create splash screen
    splash = TerminalSplashScreen(splash_pixmap)
    
    return splash


def ensure_splash_visibility(splash):
    """Safely ensure splash screen appears above other windows"""
    try:
        # Standard Qt methods - always safe
        splash.show()
        splash.raise_()           # Bring to front of window stack
        splash.activateWindow()   # Give keyboard focus
        
        # Center on screen
        screen = splash.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            splash_geometry = splash.geometry()
            center_x = (screen_geometry.width() - splash_geometry.width()) // 2
            center_y = (screen_geometry.height() - splash_geometry.height()) // 2
            splash.move(center_x, center_y)
        
    except Exception as e:
        # Graceful fallback - just show the splash normally
        print(f"Warning: Could not ensure splash visibility: {e}")
        splash.show()


def main():
    """Main entry point for the standalone Serial Terminal application"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)  # Terminal closes when window closes
    
    # Create and show splash screen immediately
    splash = create_splash_screen()
    
    # Safely ensure splash appears above other windows
    ensure_splash_visibility(splash)
    
    # Process events to ensure splash is visible
    app.processEvents()
    
    # Set application properties
    app.setApplicationName("Serial Terminal")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("SerialSplit")
    app.setOrganizationDomain("serialsplit.local")
    
    # Update splash status with progress
    splash.update_status("Initializing theme...")
    splash.set_progress(20)
    app.processEvents()
    
    # Apply dark mode palette
    setup_terminal_dark_mode(app)
    
    # Apply global dark theme stylesheet
    ThemeManager.apply_global_stylesheet(app)
    
    # Use system fonts (Poppins font loading commented out above)
    # load_terminal_fonts()
    
    # Update splash status
    splash.update_status("Scanning serial ports...")
    splash.set_progress(50)
    app.processEvents()
    
    # Create terminal icon
    terminal_icon = create_terminal_icon()
    
    # Update splash status
    splash.update_status("Loading interface...")
    splash.set_progress(80)
    app.processEvents()
    
    # Create and configure terminal window
    terminal_window = SerialMonitorWindow()
    terminal_window.setWindowIcon(terminal_icon)
    terminal_window.setWindowTitle("Serial Terminal")
    
    # Final splash status
    splash.update_status("Loading...")
    splash.set_progress(100)
    app.processEvents()
    
    # Minimum splash display time (for branding)
    QTimer.singleShot(1500, lambda: (
        splash.finish_loading(),
        splash.finish(terminal_window),
        terminal_window.show()
    ))
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()