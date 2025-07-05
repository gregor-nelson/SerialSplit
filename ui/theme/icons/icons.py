#!/usr/bin/env python3
"""
Windows 10 Professional System Icons for Hub4com GUI

This collection follows authentic Windows 10 design principles:
- Flat design with subtle depth
- Professional color palette
- Clean geometric shapes
- Enterprise-appropriate aesthetic
- Consistent with Windows system applications
"""

class AppIcons:
    """
    Windows 10 Professional system icon definitions.
    Designed for professional applications with enterprise-grade appearance.
    """

    # Windows 10 standard shadow - subtle and professional
    _WIN10_SHADOW = """
        <filter id="win10-shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="1"/>
            <feOffset dx="0" dy="1" result="offsetblur"/>
            <feFlood flood-color="#000000" flood-opacity="0.12"/>
            <feComposite in2="offsetblur" operator="in"/>
            <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    """

    # Windows 10 Professional Color Palette
    _COLORS = {
        'PRIMARY_BLUE': '#0078D4',
        'LIGHT_BLUE': '#40E0FF', 
        'DARK_BLUE': '#005A9E',
        'SUCCESS_GREEN': '#107C10',
        'WARNING_ORANGE': '#FF8C00',
        'ERROR_RED': '#E81123',
        'GRAY_DARK': '#323130',
        'GRAY_MEDIUM': '#8A8886',
        'GRAY_LIGHT': '#C8C6C4',
        'BACKGROUND': '#F3F2F1',
        'WHITE': '#FFFFFF'
    }

    LIST = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Document background -->
        <g filter="url(#win10-shadow)">
            <rect x="8" y="6" width="26" height="34" rx="2" fill="{_COLORS['WHITE']}" stroke="{_COLORS['GRAY_LIGHT']}" stroke-width="1"/>
            <!-- Folded corner -->
            <path d="M30,6 L34,10 L34,40 L30,40 Z" fill="{_COLORS['GRAY_LIGHT']}"/>
            <path d="M30,6 L34,10 L30,10 Z" fill="{_COLORS['GRAY_MEDIUM']}"/>
        </g>
        <!-- List items -->
        <rect x="12" y="14" width="2" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
        <rect x="16" y="14" width="14" height="2" fill="{_COLORS['GRAY_MEDIUM']}"/>
        <rect x="12" y="19" width="2" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
        <rect x="16" y="19" width="18" height="2" fill="{_COLORS['GRAY_MEDIUM']}"/>
        <rect x="12" y="24" width="2" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
        <rect x="16" y="24" width="16" height="2" fill="{_COLORS['GRAY_MEDIUM']}"/>
        <rect x="12" y="29" width="2" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
        <rect x="16" y="29" width="12" height="2" fill="{_COLORS['GRAY_MEDIUM']}"/>
    </svg>
    """

    CREATE = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Background circle -->
        <g filter="url(#win10-shadow)">
            <circle cx="24" cy="24" r="18" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <circle cx="24" cy="24" r="18" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        </g>
        <!-- Plus symbol -->
        <rect x="22" y="14" width="4" height="20" fill="{_COLORS['WHITE']}"/>
        <rect x="14" y="22" width="20" height="4" fill="{_COLORS['WHITE']}"/>
    </svg>
    """

    HELP = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Background circle -->
        <g filter="url(#win10-shadow)">
            <circle cx="24" cy="24" r="18" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <circle cx="24" cy="24" r="18" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        </g>
        <!-- Question mark -->
        <path d="M24,32a2,2,0,1,1-2-2A2,2,0,0,1,24,32Z" fill="{_COLORS['WHITE']}"/>
        <path d="M18,18c0-3.3,2.7-6,6-6s6,2.7,6,6c0,2-1,3-2,4l-1,1v3h-6v-4l2-2c1-1,1-1,1-2a2,2,0,0,0-4,0H18z" fill="{_COLORS['WHITE']}"/>
    </svg>
    """

    REFRESH = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Refresh arrow -->
        <g filter="url(#win10-shadow)">
            <path d="M24,8A16,16,0,1,0,35.2,19.6" fill="none" stroke="{_COLORS['PRIMARY_BLUE']}" stroke-width="3" stroke-linecap="round"/>
            <!-- Arrow head -->
            <path d="M32,12 L38,18 L32,24" fill="none" stroke="{_COLORS['PRIMARY_BLUE']}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
    </svg>
    """

    EXPORT = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Document -->
        <g filter="url(#win10-shadow)">
            <rect x="10" y="8" width="20" height="28" rx="2" fill="{_COLORS['WHITE']}" stroke="{_COLORS['GRAY_LIGHT']}" stroke-width="1"/>
            <path d="M26,8 L30,12 L30,36 L26,36 Z" fill="{_COLORS['GRAY_LIGHT']}"/>
            <path d="M26,8 L30,12 L26,12 Z" fill="{_COLORS['GRAY_MEDIUM']}"/>
        </g>
        <!-- Export arrow -->
        <path d="M32,20 L38,20 M35,17 L38,20 L35,23" stroke="{_COLORS['SUCCESS_GREEN']}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>
    """

    FOLDER = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Folder structure -->
        <g filter="url(#win10-shadow)">
            <!-- Back part -->
            <path d="M6,14V36h32V18H20l-3-4H6z" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <!-- Front part -->
            <path d="M6,18V38h32V18H6z" fill="{_COLORS['LIGHT_BLUE']}"/>
            <!-- Subtle highlight -->
            <path d="M6,18h32v2H6z" fill="rgba(255,255,255,0.2)"/>
        </g>
    </svg>
    """

    SETTINGS = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Settings gear - simplified Windows 10 style -->
        <g filter="url(#win10-shadow)">
            <path d="M24,6c-1.1,0-2,0.9-2,2v2.1c-1.3,0.2-2.5,0.6-3.6,1.2l-1.5-1.5c-0.8-0.8-2-0.8-2.8,0l-2.8,2.8c-0.8,0.8-0.8,2,0,2.8l1.5,1.5c-0.6,1.1-1,2.3-1.2,3.6H10c-1.1,0-2,0.9-2,2v4c0,1.1,0.9,2,2,2h2.1c0.2,1.3,0.6,2.5,1.2,3.6l-1.5,1.5c-0.8,0.8-0.8,2,0,2.8l2.8,2.8c0.8,0.8,2,0.8,2.8,0l1.5-1.5c1.1,0.6,2.3,1,3.6,1.2V38c0,1.1,0.9,2,2,2h4c1.1,0,2-0.9,2-2v-2.1c1.3-0.2,2.5-0.6,3.6-1.2l1.5,1.5c0.8,0.8,2,0.8,2.8,0l2.8-2.8c0.8-0.8,0.8-2,0-2.8l-1.5-1.5c0.6-1.1,1-2.3,1.2-3.6H38c1.1,0,2-0.9,2-2v-4c0-1.1-0.9-2-2-2h-2.1c-0.2-1.3-0.6-2.5-1.2-3.6l1.5-1.5c0.8-0.8,0.8-2,0-2.8l-2.8-2.8c-0.8-0.8-2-0.8-2.8,0l-1.5,1.5c-1.1-0.6-2.3-1-3.6-1.2V8c0-1.1-0.9-2-2-2H24z" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <!-- Center circle -->
            <circle cx="24" cy="24" r="6" fill="{_COLORS['BACKGROUND']}" stroke="{_COLORS['GRAY_DARK']}" stroke-width="1.5"/>
        </g>
    </svg>
    """

    DELETE = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Trash can - Windows 10 style -->
        <g filter="url(#win10-shadow)">
            <!-- Handle -->
            <rect x="20" y="8" width="8" height="4" rx="1" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <!-- Lid -->
            <rect x="14" y="12" width="20" height="3" rx="1.5" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <!-- Body -->
            <path d="M16,15 L32,15 L31,36 L17,36 Z" fill="{_COLORS['ERROR_RED']}"/>
            <!-- Delete lines -->
            <rect x="20" y="19" width="1.5" height="12" fill="{_COLORS['WHITE']}"/>
            <rect x="23.25" y="19" width="1.5" height="12" fill="{_COLORS['WHITE']}"/>
            <rect x="26.5" y="19" width="1.5" height="12" fill="{_COLORS['WHITE']}"/>
        </g>
    </svg>
    """

    REMOVE = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Remove X in circle -->
        <g filter="url(#win10-shadow)">
            <circle cx="24" cy="24" r="18" fill="{_COLORS['ERROR_RED']}"/>
            <circle cx="24" cy="24" r="18" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        </g>
        <!-- X mark -->
        <path d="M17,17 L31,31 M17,31 L31,17" stroke="{_COLORS['WHITE']}" stroke-width="3" stroke-linecap="round"/>
    </svg>
    """

    PLAY = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Play button -->
        <g filter="url(#win10-shadow)">
            <circle cx="24" cy="24" r="18" fill="{_COLORS['SUCCESS_GREEN']}"/>
            <circle cx="24" cy="24" r="18" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        </g>
        <!-- Play triangle -->
        <path d="M19,16 L33,24 L19,32 Z" fill="{_COLORS['WHITE']}"/>
    </svg>
    """

    STOP = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Stop button -->
        <g filter="url(#win10-shadow)">
            <circle cx="24" cy="24" r="18" fill="{_COLORS['ERROR_RED']}"/>
            <circle cx="24" cy="24" r="18" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        </g>
        <!-- Stop square -->
        <rect x="16" y="16" width="16" height="16" rx="2" fill="{_COLORS['WHITE']}"/>
    </svg>
    """

    DROPDOWN_ARROW = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <path d="M16,20 L24,28 L32,20" fill="none" stroke="{_COLORS['GRAY_DARK']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """

    CHECKBOX_CHECK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Checkbox -->
        <g filter="url(#win10-shadow)">
            <rect x="10" y="10" width="28" height="28" rx="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="10" y="10" width="28" height="28" rx="2" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        </g>
        <!-- Checkmark -->
        <path d="M16,24 L22,30 L34,18" stroke="{_COLORS['WHITE']}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """

    ERROR_CROSS = REMOVE  # Reuse for consistency

    MONITOR = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Monitor -->
        <g filter="url(#win10-shadow)">
            <!-- Stand -->
            <rect x="20" y="38" width="8" height="4" rx="1" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <rect x="18" y="35" width="12" height="3" rx="1" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <!-- Screen bezel -->
            <rect x="6" y="8" width="36" height="27" rx="2" fill="{_COLORS['GRAY_DARK']}"/>
            <!-- Screen -->
            <rect x="9" y="11" width="30" height="21" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <!-- Screen content -->
            <rect x="12" y="14" width="24" height="2" fill="{_COLORS['WHITE']}" opacity="0.7"/>
            <rect x="12" y="18" width="18" height="2" fill="{_COLORS['WHITE']}" opacity="0.5"/>
            <rect x="12" y="22" width="20" height="2" fill="{_COLORS['WHITE']}" opacity="0.6"/>
        </g>
    </svg>
    """

    SPINNER = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <!-- Loading spinner -->
        <circle cx="24" cy="24" r="16" fill="none" stroke="{_COLORS['GRAY_LIGHT']}" stroke-width="3"/>
        <circle cx="24" cy="24" r="16" fill="none" stroke="{_COLORS['PRIMARY_BLUE']}" stroke-width="3" stroke-linecap="round" stroke-dasharray="25 75">
            <animateTransform attributeName="transform" type="rotate" from="0 24 24" to="360 24 24" dur="1s" repeatCount="indefinite"/>
        </circle>
    </svg>
    """

    INFO = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Info circle -->
        <g filter="url(#win10-shadow)">
            <circle cx="24" cy="24" r="18" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <circle cx="24" cy="24" r="18" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        </g>
        <!-- Info symbol -->
        <rect x="22" y="20" width="4" height="14" fill="{_COLORS['WHITE']}"/>
        <circle cx="24" cy="15" r="2.5" fill="{_COLORS['WHITE']}"/>
    </svg>
    """

    ARROW_DOWN = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Down arrow -->
        <g filter="url(#win10-shadow)">
            <path d="M24,8 L24,34 M16,26 L24,34 L32,26" stroke="{_COLORS['PRIMARY_BLUE']}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </g>
    </svg>
    """

    ARROW_UP = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Up arrow -->
        <g filter="url(#win10-shadow)">
            <path d="M24,40 L24,14 M16,22 L24,14 L32,22" stroke="{_COLORS['SUCCESS_GREEN']}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </g>
    </svg>
    """

    SEARCH = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Search icon -->
        <g filter="url(#win10-shadow)">
            <circle cx="20" cy="20" r="10" fill="none" stroke="{_COLORS['GRAY_DARK']}" stroke-width="3"/>
            <path d="M28,28 L38,38" stroke="{_COLORS['GRAY_DARK']}" stroke-width="3" stroke-linecap="round"/>
        </g>
    </svg>
    """

    CHART_BAR = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Bar chart -->
        <g filter="url(#win10-shadow)">
            <rect x="8" y="24" width="6" height="16" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="18" y="16" width="6" height="24" fill="{_COLORS['SUCCESS_GREEN']}"/>
            <rect x="28" y="20" width="6" height="20" fill="{_COLORS['WARNING_ORANGE']}"/>
            <rect x="38" y="12" width="6" height="28" fill="{_COLORS['ERROR_RED']}"/>
        </g>
    </svg>
    """

    FLOW_CONTROL = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Flow arrows -->
        <g filter="url(#win10-shadow)">
            <path d="M8,16 L34,16 M28,10 L34,16 L28,22" stroke="{_COLORS['PRIMARY_BLUE']}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <path d="M40,32 L14,32 M20,26 L14,32 L20,38" stroke="{_COLORS['SUCCESS_GREEN']}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </g>
    </svg>
    """

    SIGNAL = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <!-- Signal strength -->
        <rect x="8" y="32" width="4" height="8" fill="{_COLORS['SUCCESS_GREEN']}"/>
        <rect x="16" y="24" width="4" height="16" fill="{_COLORS['SUCCESS_GREEN']}"/>
        <rect x="24" y="16" width="4" height="24" fill="{_COLORS['SUCCESS_GREEN']}"/>
        <rect x="32" y="8" width="4" height="32" fill="{_COLORS['GRAY_LIGHT']}"/>
    </svg>
    """

    BUFFER = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Buffer blocks -->
        <g filter="url(#win10-shadow)">
            <rect x="8" y="16" width="8" height="16" rx="1" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="20" y="16" width="8" height="16" rx="1" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="32" y="16" width="8" height="16" rx="1" fill="{_COLORS['GRAY_LIGHT']}"/>
        </g>
    </svg>
    """

    CLOCK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Clock -->
        <g filter="url(#win10-shadow)">
            <circle cx="24" cy="24" r="18" fill="{_COLORS['WHITE']}" stroke="{_COLORS['GRAY_MEDIUM']}" stroke-width="2"/>
            <!-- Clock hands -->
            <circle cx="24" cy="24" r="1.5" fill="{_COLORS['GRAY_DARK']}"/>
            <path d="M24,24 L24,12" stroke="{_COLORS['GRAY_DARK']}" stroke-width="2" stroke-linecap="round"/>
            <path d="M24,24 L32,24" stroke="{_COLORS['GRAY_DARK']}" stroke-width="2" stroke-linecap="round"/>
        </g>
    </svg>
    """

    PORT = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Serial port connector -->
        <g filter="url(#win10-shadow)">
            <!-- Connector body -->
            <rect x="12" y="16" width="24" height="16" rx="2" fill="{_COLORS['GRAY_MEDIUM']}" stroke="{_COLORS['GRAY_DARK']}" stroke-width="1"/>
            <!-- Connector pins -->
            <rect x="16" y="20" width="3" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="22" y="20" width="3" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="28" y="20" width="3" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="16" y="26" width="3" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="22" y="26" width="3" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="28" y="26" width="3" height="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <!-- Cable -->
            <rect x="8" y="22" width="4" height="4" rx="2" fill="{_COLORS['GRAY_DARK']}"/>
            <rect x="36" y="22" width="4" height="4" rx="2" fill="{_COLORS['GRAY_DARK']}"/>
        </g>
    </svg>
    """

    CONFIGURE = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <defs>
            {_WIN10_SHADOW}
        </defs>
        <!-- Configuration panel -->
        <g filter="url(#win10-shadow)">
            <!-- Panel background -->
            <rect x="8" y="12" width="32" height="24" rx="2" fill="{_COLORS['WHITE']}" stroke="{_COLORS['GRAY_MEDIUM']}" stroke-width="1"/>
            <!-- Sliders -->
            <rect x="12" y="18" width="24" height="2" fill="{_COLORS['GRAY_LIGHT']}"/>
            <rect x="24" y="16" width="4" height="6" rx="2" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="12" y="24" width="24" height="2" fill="{_COLORS['GRAY_LIGHT']}"/>
            <rect x="18" y="22" width="4" height="6" rx="2" fill="{_COLORS['SUCCESS_GREEN']}"/>
            <rect x="12" y="30" width="24" height="2" fill="{_COLORS['GRAY_LIGHT']}"/>
            <rect x="30" y="28" width="4" height="6" rx="2" fill="{_COLORS['WARNING_ORANGE']}"/>
        </g>
    </svg>
    """

    # Com0com Settings Icons - Small 16x16 icons for inline display
    TIMING_CLOCK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <defs>
            <filter id="timing-shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="0.5"/>
                <feOffset dx="0" dy="0.5" result="offsetblur"/>
                <feFlood flood-color="#000000" flood-opacity="0.1"/>
                <feComposite in2="offsetblur" operator="in"/>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        <!-- Clock face -->
        <g filter="url(#timing-shadow)">
            <circle cx="8" cy="8" r="6" fill="{_COLORS['WHITE']}" stroke="{_COLORS['PRIMARY_BLUE']}" stroke-width="1.5"/>
            <!-- Clock hands -->
            <circle cx="8" cy="8" r="0.8" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <path d="M8,8 L8,4" stroke="{_COLORS['PRIMARY_BLUE']}" stroke-width="1.2" stroke-linecap="round"/>
            <path d="M8,8 L11,8" stroke="{_COLORS['PRIMARY_BLUE']}" stroke-width="1" stroke-linecap="round"/>
        </g>
    </svg>
    """

    BUFFER_STACK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <defs>
            <filter id="buffer-shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="0.5"/>
                <feOffset dx="0" dy="0.5" result="offsetblur"/>
                <feFlood flood-color="#000000" flood-opacity="0.1"/>
                <feComposite in2="offsetblur" operator="in"/>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        <!-- Buffer blocks -->
        <g filter="url(#buffer-shadow)">
            <rect x="2" y="10" width="4" height="4" rx="0.5" fill="{_COLORS['SUCCESS_GREEN']}"/>
            <rect x="6" y="8" width="4" height="6" rx="0.5" fill="{_COLORS['SUCCESS_GREEN']}"/>
            <rect x="10" y="6" width="4" height="8" rx="0.5" fill="{_COLORS['WARNING_ORANGE']}"/>
        </g>
    </svg>
    """

    EXCLUSIVE_LOCK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <defs>
            <filter id="lock-shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="0.5"/>
                <feOffset dx="0" dy="0.5" result="offsetblur"/>
                <feFlood flood-color="#000000" flood-opacity="0.1"/>
                <feComposite in2="offsetblur" operator="in"/>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        <!-- Lock -->
        <g filter="url(#lock-shadow)">
            <!-- Lock shackle -->
            <path d="M5,6 L5,4 A3,3 0 0,1 11,4 L11,6" fill="none" stroke="{_COLORS['PRIMARY_BLUE']}" stroke-width="1.5" stroke-linecap="round"/>
            <!-- Lock body -->
            <rect x="4" y="6" width="8" height="7" rx="1" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <!-- Keyhole -->
            <circle cx="8" cy="9" r="1" fill="{_COLORS['WHITE']}"/>
            <rect x="7.5" y="9" width="1" height="2" fill="{_COLORS['WHITE']}"/>
        </g>
    </svg>
    """

    PLUGIN_CONNECTOR = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <defs>
            <filter id="plugin-shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="0.5"/>
                <feOffset dx="0" dy="0.5" result="offsetblur"/>
                <feFlood flood-color="#000000" flood-opacity="0.1"/>
                <feComposite in2="offsetblur" operator="in"/>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        <!-- Connector -->
        <g filter="url(#plugin-shadow)">
            <!-- Connector body -->
            <rect x="3" y="6" width="10" height="4" rx="1" fill="{_COLORS['GRAY_MEDIUM']}" stroke="{_COLORS['GRAY_DARK']}" stroke-width="0.5"/>
            <!-- Connector pins -->
            <rect x="5" y="7" width="1" height="0.8" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="7" y="7" width="1" height="0.8" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="9" y="7" width="1" height="0.8" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="5" y="8.2" width="1" height="0.8" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="7" y="8.2" width="1" height="0.8" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <rect x="9" y="8.2" width="1" height="0.8" fill="{_COLORS['PRIMARY_BLUE']}"/>
            <!-- Cable -->
            <rect x="1" y="7" width="2" height="2" rx="1" fill="{_COLORS['GRAY_DARK']}"/>
            <rect x="13" y="7" width="2" height="2" rx="1" fill="{_COLORS['GRAY_DARK']}"/>
        </g>
    </svg>
    """