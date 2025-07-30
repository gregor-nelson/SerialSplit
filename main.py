#!/usr/bin/env python3
"""
Hub4com GUI Launcher with Moxa Scanner and Baud Rate Support
A PyQt6 interface to configure and start hub4com for COM port routing
Includes comprehensive port scanning with Moxa device server detection and baud rate configuration

Main entry point for the application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QSplashScreen
from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter, QBrush, QPen, QLinearGradient, QAction, QFontDatabase, QDesktopServices, QCursor, QFont
from PyQt6.QtCore import Qt, QTimer, QUrl, QRect
from PyQt6.QtSvg import QSvgRenderer # <-- Import for SVG rendering
from ui.gui import Hub4comGUI
from ui.theme.theme import ThemeManager, AppColors  # Import for dark mode global styling

# --- GitHub SVG Icon ---
GITHUB_ICON_SVG = """
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path fill="{color}" d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.300 24 12c0-6.627-5.373-12-12-12z"/>
</svg>
"""

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


def load_splash_icon():
    """Load the splash screen icon from icon.svg file"""
    icon_path = Path(__file__).parent / "assets/icon.svg"
    
    if not icon_path.exists():
        print("Warning: icon.svg not found, using embedded icon")
        return APP_ICON_SVG
    
    try:
        with open(icon_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading icon.svg: {e}, using embedded icon")
        return APP_ICON_SVG


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

def setup_dark_mode_palette(app):
    """Apply a comprehensive dark mode QPalette for all native window elements."""
    palette = QPalette()
    
    # === MAIN COLOR ROLES ===
    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(AppColors.BACKGROUND_LIGHT))  # #2d2d2d
    palette.setColor(QPalette.ColorRole.WindowText, QColor(AppColors.TEXT_DEFAULT))  # #ffffff
    
    # Base colors for input fields
    palette.setColor(QPalette.ColorRole.Base, QColor(AppColors.BACKGROUND_WHITE))  # #1e1e1e
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(AppColors.BACKGROUND_LIGHT))  # #2d2d2d
    
    # Text colors
    palette.setColor(QPalette.ColorRole.Text, QColor(AppColors.TEXT_DEFAULT))  # #ffffff
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff6b6b"))  # Bright red for warnings
    
    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(AppColors.BUTTON_DEFAULT))  # #404040
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(AppColors.TEXT_DEFAULT))  # #ffffff
    
    # Selection colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(AppColors.SELECTION_BG))  # #1e90ff
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(AppColors.SELECTION_TEXT))  # #ffffff
    
    # === MISSING COLOR ROLES (Critical for complete dark mode) ===
    # Tooltip colors
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(AppColors.BACKGROUND_TOOLTIP))  # #404040
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(AppColors.TEXT_TOOLTIP))  # #ffffff
    
    # Link colors
    palette.setColor(QPalette.ColorRole.Link, QColor(AppColors.ACCENT_BLUE))  # #1e90ff
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(AppColors.ACCENT_PURPLE))  # #5c2d91
    
    # Placeholder text (Qt 5.12+)
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(AppColors.TEXT_DISABLED))  # #808080
    
    # === 3D EFFECT COLORS (Essential for borders and shadows) ===
    palette.setColor(QPalette.ColorRole.Light, QColor("#555555"))      # Lighter than button
    palette.setColor(QPalette.ColorRole.Midlight, QColor("#4a4a4a"))   # Between button and light
    palette.setColor(QPalette.ColorRole.Dark, QColor("#2a2a2a"))       # Darker than button
    palette.setColor(QPalette.ColorRole.Mid, QColor("#353535"))        # Between button and dark
    palette.setColor(QPalette.ColorRole.Shadow, QColor("#1a1a1a"))     # Very dark shadow
    
    # === COLOR GROUP STATES (Essential for dialogs and popups) ===
    
    # DISABLED state colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(AppColors.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(AppColors.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(AppColors.TEXT_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(AppColors.BACKGROUND_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(AppColors.BACKGROUND_DISABLED))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(AppColors.BACKGROUND_DISABLED))
    
    # INACTIVE state colors (for unfocused windows and dialogs)
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(AppColors.BACKGROUND_LIGHT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(AppColors.TEXT_DEFAULT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(AppColors.BACKGROUND_WHITE))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(AppColors.TEXT_DEFAULT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(AppColors.BUTTON_DEFAULT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(AppColors.TEXT_DEFAULT))
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor("#4a4a4a"))  # Dimmed selection
    palette.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(AppColors.TEXT_DEFAULT))
    
    # Set the palette to the application
    app.setPalette(palette)


class SplashScreen(QSplashScreen):
    """Custom splash screen for Serial Port Splitter application"""
    
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
        self.version_text = "Version 0.1"
        
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
        
        # Draw main application icon (centered, scaled)
        icon_size = 120
        icon_x = (width - icon_size) // 2
        icon_y = 40
        
        # Render main application icon
        splash_icon_svg = load_splash_icon()
        svg_bytes = splash_icon_svg.encode('utf-8')
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
        
        title_rect = painter.fontMetrics().boundingRect("Serial Port Splitter")
        title_x = (width - title_rect.width()) // 2
        title_y = icon_y + icon_size + 30
        
        painter.drawText(title_x, title_y, "Serial Port Splitter")
        
        # Draw version
        version_font = QFont("Segoe UI", 11)
        painter.setFont(version_font)
        painter.setPen(QColor(AppColors.TEXT_DEFAULT))
        
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
    splash = SplashScreen(splash_pixmap)
    
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
    """Main entry point for the Hub4com Launcher application"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Prevent app from quitting when window is closed
    
    # Create and show splash screen immediately
    splash = create_splash_screen()
    
    # Safely ensure splash appears above other windows
    ensure_splash_visibility(splash)
    
    # Process events to ensure splash is visible
    app.processEvents()
    
    # Set application properties
    app.setApplicationName("Serial Port Splitter")
    app.setApplicationVersion("0.1")
    app.setOrganizationName("SerialSplit")
    app.setOrganizationDomain("serialsplit.local")
    
    # Update splash status
    splash.update_status("Initializing theme")
    app.processEvents()
    
    # Apply dark mode palette as a fallback for native components
    setup_dark_mode_palette(app)
    
    # Apply dark mode global stylesheet to entire application
    # This ensures context menus, system tray menus, and all global UI elements use dark theme
    ThemeManager.apply_global_stylesheet(app)
    
    # Use Windows 10 system fonts (Segoe UI) - no custom font loading needed
    # load_inter_font()
    
    # Update splash status
    splash.update_status("Loading system components")
    app.processEvents()

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
    
    # Update splash status
    splash.update_status("Initializing interface")
    app.processEvents()
    
    # Create and show main window
    window = Hub4comGUIWithTray(tray_icon)
    window.setWindowIcon(app_icon)
    
    # Connect tray actions
    show_action.triggered.connect(window.show_window)
    quit_action.triggered.connect(app.quit)
    tray_icon.activated.connect(lambda reason: window.show_window() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.setToolTip("Serial Port Splitter")
    tray_icon.show()
    
    # Final splash status
    splash.update_status("Loading")
    app.processEvents()
    
    # Minimum splash display time (for branding)
    QTimer.singleShot(1500, lambda: (
        splash.finish_loading(),
        splash.finish(window),
        window.show()
    ))
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
