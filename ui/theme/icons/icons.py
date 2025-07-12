#!/usr/bin/env python3
"""
Windows 10 Professional System Icons for Hub4com GUI
---
Revision 2: Enhanced for a deep, rich, and eye-catching appearance
using subtle gradients and lighting effects, aligned with modern Fluent Design principles.
"""

class AppIcons:
    """
    A collection of SVG icons designed with an enhanced Windows aesthetic.
    The icons use gradients and shadows to create depth, making them suitable
    for modern applications requiring a polished, enterprise-grade look.
    """

    # Enhanced color palette with brighter tones for gradients
    _COLORS = {
        'PRIMARY_BLUE': '#0078D4',
        'PRIMARY_BLUE_LIGHT': '#00A0FF',
        'DARK_BLUE': '#005A9E',
        'SUCCESS_GREEN': '#107C10',
        'SUCCESS_GREEN_LIGHT': '#1ED760',
        'WARNING_ORANGE': '#FF8C00',
        'WARNING_ORANGE_LIGHT': '#FFA500',
        'ERROR_RED': '#D83B01',
        'ERROR_RED_LIGHT': '#F06B38',
        'GRAY_DARK': '#323130',
        'GRAY_MEDIUM': '#8A8886',
        'GRAY_LIGHT': '#E1DFDD',
        'BACKGROUND': '#F3F2F1',
        'WHITE': '#FFFFFF'
    }

    # Consistent stroke width for all icons
    _STROKE_WIDTH = "2.5"

    # Reusable SVG definitions for gradients and shadows
    _DEFS = f"""
        <defs>
            <filter id="win10-shadow" x="-25%" y="-25%" width="150%" height="150%">
                <feDropShadow dx="0" dy="2" stdDeviation="1.5" flood-color="#000000" flood-opacity="0.15"/>
            </filter>
            <filter id="win10-shadow-small" x="-25%" y="-25%" width="150%" height="150%">
                <feDropShadow dx="0" dy="0.5" stdDeviation="0.5" flood-color="#000000" flood-opacity="0.2"/>
            </filter>
            <linearGradient id="primary-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="{_COLORS['PRIMARY_BLUE_LIGHT']}" />
                <stop offset="100%" stop-color="{_COLORS['PRIMARY_BLUE']}" />
            </linearGradient>
            <linearGradient id="success-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="{_COLORS['SUCCESS_GREEN_LIGHT']}" />
                <stop offset="100%" stop-color="{_COLORS['SUCCESS_GREEN']}" />
            </linearGradient>
            <linearGradient id="error-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="{_COLORS['ERROR_RED_LIGHT']}" />
                <stop offset="100%" stop-color="{_COLORS['ERROR_RED']}" />
            </linearGradient>
            <linearGradient id="warning-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="{_COLORS['WARNING_ORANGE_LIGHT']}" />
                <stop offset="100%" stop-color="{_COLORS['WARNING_ORANGE']}" />
            </linearGradient>
            <linearGradient id="gray-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="{_COLORS['GRAY_LIGHT']}" />
                <stop offset="100%" stop-color="{_COLORS['GRAY_MEDIUM']}" />
            </linearGradient>
        </defs>
    """

    TERMINAL_SETTINGS = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <rect x="8" y="12" width="48" height="40" rx="2" fill="{_COLORS['GRAY_DARK']}"/>
            <rect x="8" y="12" width="48" height="7" rx="1" ry="1" fill="#4B4B4B"/>
            <text x="14" y="29" font-family="Consolas, 'Courier New', monospace" font-size="5" fill="#00E070">C:\&gt;_</text>
        </g>
        <g transform="translate(40 36) scale(1.2)" filter="url(#win10-shadow)">
            <circle cx="8" cy="8" r="8" fill="url(#primary-gradient)"/>
            <path d="M8 3.5v2M8 10.5v2M12.5 8h-2M5.5 8h-2M10.9 5.1l-1.4 1.4M6.5 9.5l-1.4 1.4M10.9 10.9l-1.4-1.4M6.5 6.5l-1.4-1.4" 
                  stroke="{_COLORS['WHITE']}" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
            <circle cx="8" cy="8" r="2.5" fill="{_COLORS['WHITE']}" opacity="0.9"/>
        </g>
    </svg>
    """

    LIST = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <rect x="10" y="6" width="28" height="36" rx="2" fill="{_COLORS['BACKGROUND']}"/>
            <rect x="10" y="6" width="28" height="36" rx="2" fill="{_COLORS['WHITE']}" stroke="{_COLORS['GRAY_LIGHT']}" stroke-width="0.5"/>
        </g>
        <g>
            <rect x="18" y="13" width="16" height="2.5" rx="1" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <rect x="18" y="21" width="16" height="2.5" rx="1" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <rect x="18" y="29" width="16" height="2.5" rx="1" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <rect x="18" y="37" width="10" height="2.5" rx="1" fill="{_COLORS['GRAY_MEDIUM']}"/>
        </g>
    </svg>
    """

    CREATE = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <rect x="21" y="10" width="6" height="28" rx="2" fill="url(#primary-gradient)"/>
            <rect x="10" y="21" width="28" height="6" rx="2" fill="url(#primary-gradient)"/>
        </g>
    </svg>
    """

    HELP = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <circle cx="24" cy="24" r="18" fill="url(#primary-gradient)" filter="url(#win10-shadow)"/>
        <path d="M19 18a5 5 0 0 1 5-5c2.76 0 5 2.24 5 5 0 2.76-2.24 5-5 5v1" 
              stroke="{_COLORS['WHITE']}" stroke-width="{_STROKE_WIDTH}" fill="none" stroke-linecap="round" opacity="0.9"/>
        <circle cx="24" cy="31" r="2.5" fill="{_COLORS['WHITE']}" opacity="0.9"/>
    </svg>
    """

    REFRESH = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <!-- Circular arrow with rich gradient and multiple layers -->
            <g transform="translate(24, 24)">
                <!-- Background circle for depth -->
                <circle r="16" fill="{_COLORS['BACKGROUND']}" opacity="0.3"/>
                <!-- Main refresh arrow -->
                <path d="M-12 0A12 12 0 1 1 8.5 -8.5M12 -12V-6H6" 
                      stroke="url(#primary-gradient)" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                <!-- Inner highlight path -->
                <path d="M-10 0A10 10 0 1 1 7 -7M10 -10V-7H7" 
                      stroke="{_COLORS['PRIMARY_BLUE_LIGHT']}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>
                <!-- Arrow head enhancement -->
                <g fill="url(#primary-gradient)">
                    <path d="M12 -12L6 -6L9 -9Z"/>
                </g>
                <!-- Arrow head highlight -->
                <path d="M11 -11L7 -7L9 -9Z" fill="{_COLORS['WHITE']}" opacity="0.4"/>
            </g>
            <!-- Motion indicator dots -->
            <g fill="url(#success-gradient)" opacity="0.7">
                <circle cx="38" cy="20" r="1.5"/>
                <circle cx="36" cy="14" r="1"/>
                <circle cx="32" cy="10" r="0.8"/>
            </g>
            <!-- Secondary motion trail -->
            <g transform="translate(24, 24) rotate(-30)">
                <path d="M14 0A14 14 0 0 1 10 -10" 
                      stroke="url(#success-gradient)" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.4" stroke-dasharray="3 2"/>
            </g>
        </g>
    </svg>
    """

    EXPORT = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <path d="M16 22l8-8 8 8M24 14v16" 
                  stroke="url(#primary-gradient)" stroke-width="{_STROKE_WIDTH}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <rect x="12" y="34" width="24" height="4" rx="1.5" fill="url(#gray-gradient)"/>
        </g>
    </svg>
    """

    FOLDER = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <path d="M8 12h13l4 4h15v20H8z" fill="url(#primary-gradient)"/>
            <path d="M40,17 L40,36 H8 V15 H22 l3-3 H8 a1,1 0,0,0 -1,1 V36 a1,1 0,0,0 1,1 H40 a1,1 0,0,0 1-1 V17 a1,1 0,0,0 -1,-1 z" fill="{_COLORS['DARK_BLUE']}" opacity="0.4"/>
        </g>
    </svg>
    """

    SETTINGS = f"""
   <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="a" gradientUnits="userSpaceOnUse" x1="22.27" y1="11.73" x2="9.646" y2="24.354" gradientTransform="matrix(2 0 0 -2 0 68)">
      <stop offset="0" style="stop-color:#fff;stop-opacity:1"/>
      <stop offset=".242" style="stop-color:#f2f2f2;stop-opacity:1"/>
      <stop offset="1" style="stop-color:#ccc;stop-opacity:1"/>
    </linearGradient>
    <linearGradient id="b" gradientUnits="userSpaceOnUse" x1="10.386" y1="23.614" x2="20.234" y2="13.766" gradientTransform="matrix(2 0 0 -2 0 68)">
      <stop offset=".229" style="stop-color:#0669bc;stop-opacity:1"/>
      <stop offset=".804" style="stop-color:#104e91;stop-opacity:1"/>
    </linearGradient>
    <linearGradient id="c" gradientUnits="userSpaceOnUse" x1="1.185" y1="32.737" x2="27.173" y2="6.749" gradientTransform="matrix(2 0 0 -2 0 68)">
      <stop offset=".145" style="stop-color:#8a9198;stop-opacity:1"/>
      <stop offset=".894" style="stop-color:#63707b;stop-opacity:1"/>
    </linearGradient>
  </defs>
  <path style="stroke:none;fill-rule:nonzero;fill:url(#a)" d="M50 32c0 9.941-8.059 18-18 18s-18-8.059-18-18 8.059-18 18-18 18 8.059 18 18m0 0"/>
  <path style="stroke:none;fill-rule:nonzero;fill:url(#b)" d="M44 32c0 6.629-5.371 12-12 12s-12-5.371-12-12 5.371-12 12-12 12 5.371 12 12m0 0"/>
  <path style="stroke:none;fill-rule:nonzero;fill:url(#c)" d="M63.05 24.637a11.23 11.23 0 0 1-9.573-5.5 10.86 10.86 0 0 1-.258-10.543A32.1 32.1 0 0 0 41.332 2 11.23 11.23 0 0 1 32 6.93 11.22 11.22 0 0 1 22.672 2a32.1 32.1 0 0 0-11.89 6.594 10.85 10.85 0 0 1-.259 10.543 11.23 11.23 0 0 1-9.574 5.5 30.1 30.1 0 0 0-.367 13.398 11.24 11.24 0 0 1 9.941 5.508 10.87 10.87 0 0 1-.355 11.566A32.1 32.1 0 0 0 21.914 62a11.258 11.258 0 0 1 20.172 0 32 32 0 0 0 11.742-6.89 10.86 10.86 0 0 1-.351-11.567 11.24 11.24 0 0 1 9.941-5.508 30.2 30.2 0 0 0-.367-13.398M32 48c-8.836 0-16-7.164-16-16s7.164-16 16-16 16 7.164 16 16-7.164 16-16 16m0 0"/>
</svg>
    """

    DELETE = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <path d="M15 12h18v4H15z" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <path d="M17 16h14v22a2 2 0 0 1-2 2H19a2 2 0 0 1-2-2V16z" fill="url(#error-gradient)"/>
            <path d="M21 19v15M27 19v15" stroke="{_COLORS['WHITE']}" stroke-width="2" stroke-linecap="round" opacity="0.7"/>
        </g>
    </svg>
    """

    REMOVE = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <path d="M14 14l20 20M34 14L14 34" stroke="url(#error-gradient)" stroke-width="4" stroke-linecap="round"/>
        </g>
    </svg>
    """

    PLAY = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <path d="M16 12l20 12-20 12V12z" fill="url(#success-gradient)" filter="url(#win10-shadow)"/>
    </svg>
    """

    STOP = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <rect x="14" y="14" width="20" height="20" rx="2" fill="url(#error-gradient)" filter="url(#win10-shadow)"/>
    </svg>
    """

    DROPDOWN_ARROW = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        <path d="M14 20l10 10 10-10" fill="none" stroke="{_COLORS['GRAY_DARK']}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """

    CHECKBOX_CHECK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <rect x="12" y="12" width="24" height="24" rx="3" fill="url(#primary-gradient)" filter="url(#win10-shadow)"/>
        <path d="M18 24l6 6 10-10" stroke="{_COLORS['WHITE']}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """

    MONITOR = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <rect x="6" y="10" width="36" height="24" rx="2" fill="{_COLORS['GRAY_DARK']}"/>
            <rect x="8" y="12" width="32" height="20" fill="{_COLORS['DARK_BLUE']}"/>
            <radialGradient id="glow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="{_COLORS['PRIMARY_BLUE_LIGHT']}" stop-opacity="0.7"/>
                <stop offset="100%" stop-color="{_COLORS['DARK_BLUE']}" stop-opacity="0"/>
            </radialGradient>
            <rect x="8" y="12" width="32" height="20" fill="url(#glow)"/>
            <path d="M20 34h8v4h-8z" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <path d="M16 38h16v2H16z" fill="{_COLORS['GRAY_MEDIUM']}" rx="1"/>
        </g>
    </svg>
    """

    SPINNER = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <circle cx="24" cy="24" r="16" fill="none" stroke="url(#gray-gradient)" stroke-width="3" opacity="0.3"/>
        <circle cx="24" cy="24" r="16" fill="none" stroke="url(#primary-gradient)" stroke-width="3.5" 
                stroke-dasharray="30 70" stroke-linecap="round">
            <animateTransform attributeName="transform" type="rotate" from="0 24 24" to="360 24 24" dur="1s" repeatCount="indefinite"/>
        </circle>
    </svg>
    """

    INFO = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <circle cx="24" cy="24" r="18" fill="url(#primary-gradient)" filter="url(#win10-shadow)"/>
        <g fill="{_COLORS['WHITE']}" opacity="0.9">
            <circle cx="24" cy="17" r="2.5"/>
            <rect x="21.5" y="23" width="5" height="12" rx="2.5"/>
        </g>
    </svg>
    """

    ARROW_DOWN = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <path d="M24 12v20m-8-8l8 8 8-8" stroke="url(#primary-gradient)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </g>
    </svg>
    """

    ARROW_UP = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <path d="M24 36V16m-8 8l8-8 8 8" stroke="url(#success-gradient)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </g>
    </svg>
    """

    SEARCH = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)" transform="translate(4, 4)">
            <circle cx="17" cy="17" r="10" stroke="url(#gray-gradient)" stroke-width="{_STROKE_WIDTH}" fill="none"/>
            <path d="M25 25l8 8" stroke="url(#gray-gradient)" stroke-width="3.5" stroke-linecap="round"/>
        </g>
    </svg>
    """

    CHART_BAR = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <rect x="8" y="28" width="7" height="10" rx="1.5" fill="url(#primary-gradient)"/>
            <rect x="18" y="22" width="7" height="16" rx="1.5" fill="url(#success-gradient)"/>
            <rect x="28" y="16" width="7" height="22" rx="1.5" fill="url(#warning-gradient)"/>
            <rect x="38" y="10" width="7" height="28" rx="1.5" fill="url(#error-gradient)"/>
        </g>
    </svg>
    """

    FLOW_CONTROL = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <path d="M12 18h20m-6-6l6 6-6 6" stroke="url(#primary-gradient)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <path d="M36 30H16m6 6l-6-6 6-6" stroke="url(#success-gradient)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </g>
    </svg>
    """

    SIGNAL = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)" transform="translate(0, 4)">
            <rect x="10" y="26" width="6" height="6" rx="2" fill="url(#success-gradient)"/>
            <rect x="18" y="20" width="6" height="12" rx="2" fill="url(#success-gradient)"/>
            <rect x="26" y="14" width="6" height="18" rx="2" fill="url(#success-gradient)"/>
            <rect x="34" y="8" width="6" height="24" rx="2" fill="url(#gray-gradient)" opacity="0.5"/>
        </g>
    </svg>
    """

    BUFFER = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <rect x="8" y="18" width="10" height="12" rx="2" fill="url(#primary-gradient)"/>
            <rect x="19" y="18" width="10" height="12" rx="2" fill="url(#primary-gradient)"/>
            <rect x="30" y="18" width="10" height="12" rx="2" fill="url(#gray-gradient)" opacity="0.6"/>
        </g>
    </svg>
    """

    CLOCK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <circle cx="24" cy="24" r="18" fill="{_COLORS['BACKGROUND']}" stroke="{_COLORS['GRAY_MEDIUM']}" stroke-width="1"/>
            <circle cx="24" cy="24" r="17" fill="{_COLORS['WHITE']}"/>
            <circle cx="24" cy="24" r="2" fill="{_COLORS['GRAY_DARK']}"/>
            <rect x="23" y="12" width="2" height="12" rx="1" fill="{_COLORS['GRAY_DARK']}" transform="rotate(15, 24, 24)"/>
            <rect x="23" y="18" width="2" height="8" rx="1" fill="{_COLORS['GRAY_DARK']}" transform="rotate(90, 24, 24)"/>
        </g>
    </svg>
    """

    PORT = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <rect x="12" y="18" width="24" height="12" rx="2" fill="url(#gray-gradient)"/>
            <g fill="{_COLORS['GRAY_DARK']}">
                <circle cx="17" cy="24" r="1.5"/><circle cx="21" cy="24" r="1.5"/><circle cx="25" cy="24" r="1.5"/><circle cx="29" cy="24" r="1.5"/>
            </g>
        </g>
    </svg>
    """

    CONFIGURE = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <rect x="12" y="16" width="24" height="4" rx="2" fill="{_COLORS['GRAY_LIGHT']}"/>
            <rect x="12" y="24" width="24" height="4" rx="2" fill="{_COLORS['GRAY_LIGHT']}"/>
            <rect x="12" y="32" width="24" height="4" rx="2" fill="{_COLORS['GRAY_LIGHT']}"/>
            <circle cx="28" cy="18" r="5" fill="url(#primary-gradient)"/>
            <circle cx="20" cy="26" r="5" fill="url(#success-gradient)"/>
            <circle cx="32" cy="34" r="5" fill="url(#warning-gradient)"/>
        </g>
    </svg>
    """

    # Com0com Settings Icons - Small 16x16 icons for inline display
    TIMING_CLOCK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        {_DEFS}
        <g filter="url(#win10-shadow-small)">
            <circle cx="8" cy="8" r="7" fill="{_COLORS['WHITE']}" stroke="{_COLORS['GRAY_MEDIUM']}" stroke-width="0.5"/>
            <rect x="7.5" y="4" width="1" height="4" rx="0.5" fill="{_COLORS['GRAY_DARK']}"/>
            <rect x="8" y="7.5" width="3" height="1" rx="0.5" fill="{_COLORS['GRAY_DARK']}"/>
            <circle cx="8" cy="8" r="1" fill="{_COLORS['GRAY_DARK']}"/>
        </g>
    </svg>
    """

    BUFFER_STACK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        {_DEFS}
        <g filter="url(#win10-shadow-small)">
            <rect x="2" y="10" width="12" height="4" rx="1" fill="url(#warning-gradient)"/>
            <rect x="2" y="6" width="12" height="4" rx="1" fill="url(#success-gradient)"/>
            <rect x="2" y="2" width="12" height="4" rx="1" fill="url(#success-gradient)"/>
        </g>
    </svg>
    """

    EXCLUSIVE_LOCK = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        {_DEFS}
        <g filter="url(#win10-shadow-small)">
            <path d="M4 7V5.5A4 4 0 0 1 8 1.5a4 4 0 0 1 4 4V7" 
                  stroke="url(#gray-gradient)" stroke-width="2" fill="none" stroke-linecap="round"/>
            <rect x="3" y="7" width="10" height="7" rx="1.5" fill="url(#primary-gradient)"/>
            <circle cx="8" cy="10.5" r="1" fill="{_COLORS['WHITE']}"/>
        </g>
    </svg>
    """

    PLUGIN_CONNECTOR = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        {_DEFS}
        <g filter="url(#win10-shadow-small)">
            <rect x="2" y="6" width="12" height="4" rx="1" fill="url(#gray-gradient)"/>
            <g fill="{_COLORS['GRAY_DARK']}">
                <rect x="4" y="7" width="1.5" height="2"/><rect x="7.25" y="7" width="1.5" height="2"/><rect x="10.5" y="7" width="1.5" height="2"/>
            </g>
        </g>
    </svg>
    """

    GITHUB = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" 
              fill="{_COLORS['GRAY_DARK']}"/>
    </svg>
    """

    PLUS = CREATE 

    MINUS = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <rect x="10" y="21" width="28" height="6" rx="2" fill="url(#primary-gradient)" filter="url(#win10-shadow)"/>
    </svg>
    """

    PAUSE = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)" fill="url(#warning-gradient)">
            <rect x="16" y="14" width="6" height="20" rx="2"/>
            <rect x="26" y="14" width="6" height="20" rx="2"/>
        </g>
    </svg>
    """

    CHEVRON_DOWN = DROPDOWN_ARROW # Alias for DROPDOWN_ARROW

    WRAP_TEXT = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
        {_DEFS}
        <g filter="url(#win10-shadow)">
            <rect x="8" y="12" width="32" height="3" rx="1.5" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <rect x="8" y="19" width="32" height="3" rx="1.5" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <rect x="8" y="26" width="20" height="3" rx="1.5" fill="{_COLORS['GRAY_MEDIUM']}"/>
            <path d="M36 27.5l-6 6v-4h-20" fill="none" stroke="url(#primary-gradient)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="8" y="33" width="28" height="3" rx="1.5" fill="{_COLORS['GRAY_MEDIUM']}"/>
        </g>
    </svg>
    """