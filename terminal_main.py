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
from ui.theme.theme import ThemeManager, AppColors

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
    """Custom splash screen for Serial Terminal application"""
    
    def __init__(self, pixmap):
        super().__init__(pixmap)
        
        # Safe window flags for maximum visibility without breaking anything
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint  # Always stays above other windows
        )
        
        # Status and animation state
        self.status_text = "Loading..."
        self.loading_dots = 0
        self.version_text = "Version 1.0"
        
        # GitHub profile URL (replace with your GitHub username)
        self.github_url = "https://github.com/gregor-nelson"  # Replace with your GitHub profile
        self.github_icon_rect = QRect()  # Will be set in paintEvent
        self.github_hovered = False
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(500)  # Update every 500ms
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Apply dark theme styling
        self.setStyleSheet(f"""
            QSplashScreen {{
                background-color: {AppColors.BACKGROUND_LIGHT};
                border: 2px solid {AppColors.ACCENT_BLUE};
            }}
        """)
    
    def update_animation(self):
        """Update loading animation dots"""
        self.loading_dots = (self.loading_dots + 1) % 4
        self.update()
    
    def update_status(self, status):
        """Update status text"""
        self.status_text = status
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event to draw splash screen content"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get splash screen dimensions
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        # Draw background
        painter.fillRect(rect, QColor(AppColors.BACKGROUND_LIGHT))
        
        # Draw terminal icon (centered, scaled)
        icon_size = 120
        icon_x = (width - icon_size) // 2
        icon_y = 40
        
        # Render terminal icon
        svg_bytes = TERMINAL_ICON_SVG.encode('utf-8')
        renderer = QSvgRenderer(svg_bytes)
        icon_pixmap = QPixmap(icon_size, icon_size)
        icon_pixmap.fill(Qt.GlobalColor.transparent)
        icon_painter = QPainter(icon_pixmap)
        renderer.render(icon_painter)
        icon_painter.end()
        
        painter.drawPixmap(icon_x, icon_y, icon_pixmap)
        
        # Draw title (reduced size)
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)  # Reduced from 24 to 20
        painter.setFont(title_font)
        painter.setPen(QColor(AppColors.TEXT_DEFAULT))
        
        title_rect = painter.fontMetrics().boundingRect("Serial Terminal")
        title_x = (width - title_rect.width()) // 2
        title_y = icon_y + icon_size + 30
        
        painter.drawText(title_x, title_y, "Serial Terminal")
        
        # Draw version
        version_font = QFont("Segoe UI", 11)
        painter.setFont(version_font)
        painter.setPen(QColor(AppColors.TEXT_DEFAULT  ))
        
        version_rect = painter.fontMetrics().boundingRect(self.version_text)
        version_x = (width - version_rect.width()) // 2
        version_y = title_y + 35
        
        painter.drawText(version_x, version_y, self.version_text)
        
        # Draw GitHub icon (clickable)
        github_icon_size = 20
        github_x = (width - github_icon_size) // 2
        github_y = version_y + 25
        
        # Set the clickable area for the GitHub icon
        self.github_icon_rect = QRect(github_x, github_y, github_icon_size, github_icon_size)
        
        # Choose icon color based on hover state
        github_color = AppColors.ACCENT_BLUE if self.github_hovered else AppColors.TEXT_PRIMARY
        
        # Render GitHub icon
        github_svg = GITHUB_ICON_SVG.format(color=github_color)
        github_svg_bytes = github_svg.encode('utf-8')
        github_renderer = QSvgRenderer(github_svg_bytes)
        github_pixmap = QPixmap(github_icon_size, github_icon_size)
        github_pixmap.fill(Qt.GlobalColor.transparent)
        github_painter = QPainter(github_pixmap)
        github_renderer.render(github_painter)
        github_painter.end()
        
        painter.drawPixmap(github_x, github_y, github_pixmap)
        
        # Draw loading animation (positioned with more space from GitHub icon)
        loading_font = QFont("Segoe UI", 12)
        painter.setFont(loading_font)
        painter.setPen(QColor(AppColors.ACCENT_BLUE))
        
        # Create animated loading text
        dots = "." * self.loading_dots
        loading_text = f"{self.status_text}{dots}"
        
        loading_rect = painter.fontMetrics().boundingRect(loading_text)
        loading_x = (width - loading_rect.width()) // 2
        loading_y = github_y + 60  # Increased gap from GitHub icon
        
        painter.drawText(loading_x, loading_y, loading_text)
        
        # Draw loading indicator bar
        bar_width = 200
        bar_height = 4
        bar_x = (width - bar_width) // 2
        bar_y = loading_y + 25
        
        # Background bar
        painter.fillRect(bar_x, bar_y, bar_width, bar_height, QColor(AppColors.BACKGROUND_WHITE))
        
        # Animated progress bar
        progress_width = int(bar_width * (self.loading_dots + 1) / 4)
        painter.fillRect(bar_x, bar_y, progress_width, bar_height, QColor(AppColors.ACCENT_BLUE))
        
        # Note: Footer is drawn after version text above
        
        painter.end()
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on the splash screen"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.github_icon_rect.contains(event.pos()):
                # Open GitHub profile
                QDesktopServices.openUrl(QUrl(self.github_url))
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover effects"""
        old_hovered = self.github_hovered
        self.github_hovered = self.github_icon_rect.contains(event.pos())
        
        # Update cursor and repaint if hover state changed
        if self.github_hovered != old_hovered:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor) if self.github_hovered else QCursor(Qt.CursorShape.ArrowCursor))
            self.update()
        
        super().mouseMoveEvent(event)
    
    def finish_loading(self):
        """Clean up splash screen"""
        self.animation_timer.stop()


def create_splash_screen():
    """Create and return the splash screen"""
    # Create a pixmap for the splash screen background (adjusted for GitHub icon)
    splash_pixmap = QPixmap(400, 400)
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
    
    # Update splash status
    splash.update_status("Initializing theme")
    app.processEvents()
    
    # Apply dark mode palette
    setup_terminal_dark_mode(app)
    
    # Apply global dark theme stylesheet
    ThemeManager.apply_global_stylesheet(app)
    
    # Use system fonts (Poppins font loading commented out above)
    # load_terminal_fonts()
    
    # Update splash status
    splash.update_status("Scanning serial ports")
    app.processEvents()
    
    # Create terminal icon
    terminal_icon = create_terminal_icon()
    
    # Update splash status
    splash.update_status("Loading terminal interface")
    app.processEvents()
    
    # Create and configure terminal window
    terminal_window = SerialMonitorWindow()
    terminal_window.setWindowIcon(terminal_icon)
    terminal_window.setWindowTitle("Serial Terminal")
    
    # Final splash status
    splash.update_status("Loading")
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