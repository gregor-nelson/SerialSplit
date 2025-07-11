#!/usr/bin/env python3
"""
Hub4com GUI Icons using Newaita-reborn-dark Icon Pack
---
Direct implementation of Newaita-reborn-dark icons without modifications.
Icons maintain their original dark theme styling and color schemes.
"""

class AppIcons:
    """
    A collection of SVG icons from the Newaita-reborn-dark icon pack.
    Icons are used exactly as provided in the original pack without any modifications.
    """

    # Color constants for icon theming
    _COLORS = {
        'PRIMARY_BLUE': '#eeeeee',
        'SUCCESS_GREEN': '#00e070',
        'WARNING_ORANGE': '#ff8c00',
        'ERROR_RED': '#ff5555',
        'GRAY_DARK': '#424242',
        'GRAY_MEDIUM': '#8a8886',
        'GRAY_LIGHT': '#eeeeee',
        'WHITE': '#ffffff'
    }

    TERMINAL_SETTINGS = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text"  d="M 4 4 L 4 18 L 18 18 L 18 4 Z M 6 6 L 16 6 L 16 16 L 6 16 Z M 9 8 L 9 9 L 7 9 L 7 12 L 11 12 L 11 13 L 7 13 L 7 14 L 9 14 L 9 15 L 10 15 L 10 14 L 12 14 L 12 11 L 8 11 L 8 10 L 12 10 L 12 9 L 10 9 L 10 8 Z M 9 8 "/>
    </g>
    </svg>
    """

    LIST = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 12 4 L 12 10 L 18 10 L 18 4 Z M 4 6 L 4 18 L 6 18 L 6 16 L 10 16 L 10 14 L 6 14 L 6 8 L 10 8 L 10 6 Z M 12 12 L 12 18 L 18 18 L 18 12 Z M 12 12 "/>
    </g>
    </svg>
    """

    CREATE = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 5 4 L 5 18 L 10 18 L 10 16 L 7 16 L 7 6 L 12 6 L 15 9 L 15 10 L 17 10 L 17 8 L 13 4 Z M 14 12 L 14 14 L 12 14 L 12 16 L 14 16 L 14 18 L 16 18 L 16 16 L 18 16 L 18 14 L 16 14 L 16 12 Z M 14 12 "/>
    </g>
    </svg>
    """

    HELP = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 11 4 C 7.121094 4 4 7.121094 4 11 C 4 14.878906 7.121094 18 11 18 C 14.878906 18 18 14.878906 18 11 C 18 7.121094 14.878906 4 11 4 Z M 11 6 C 13.769531 6 16 8.230469 16 11 C 16 13.769531 13.769531 16 11 16 C 8.230469 16 6 13.769531 6 11 C 6 8.230469 8.230469 6 11 6 Z M 9 8 L 9 10 L 13 10 L 13 8 Z M 9 12 L 9 14 L 13 14 L 13 12 Z M 9 12 "/>
    </g>
    </svg>
    """

    REFRESH = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 11 4 C 7.460938 4 4.5625 6.601562 4.078125 10 L 6.101562 10 C 6.5625 7.710938 8.574219 6 11 6 C 13.769531 6 16 8.230469 16 11 C 16 13.769531 13.769531 16 11 16 L 10 16 L 10 18 L 11 18 C 14.878906 18 18 14.878906 18 11 C 18 7.121094 14.878906 4 11 4 Z M 10 7 L 10 12 L 14 12 L 14 10 L 12 10 L 12 7 Z M 4 12 L 4 18 L 9 15 Z M 4 12 "/>
    </g>
    </svg>
    """

    EXPORT = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M16 22l8-8 8 8M24 14v16"/>
    </g>
    </svg>
    """

    FOLDER = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="48" height="48" viewBox="0 0 48 48" version="1.1">
    <defs>
    <linearGradient id="linear0" gradientUnits="userSpaceOnUse" x1="31.999998" y1="60" x2="31.999998" y2="3.999999" gradientTransform="matrix(0.75,0,0,0.75,0,0.000000000000085265)">
    <stop offset="0" style="stop-color:rgb(0%,0%,0%);stop-opacity:0.2;"/>
    <stop offset="1" style="stop-color:rgb(100%,100%,100%);stop-opacity:0;"/>
    </linearGradient>
    </defs>
    <g id="surface1">
    <path style=" stroke:none;fill-rule:nonzero;fill:rgb(12.941177%,58.823532%,95.294118%);fill-opacity:1;" d="M 28.5 6 C 27.386719 6 26.417969 6.601562 25.898438 7.5 L 7.5 7.5 C 5.839844 7.5 4.5 8.839844 4.5 10.5 L 4.5 15 C 4.5 16.660156 5.839844 18 7.5 18 L 40.5 18 C 42.160156 18 43.5 16.660156 43.5 15 L 43.5 9 C 43.5 7.339844 42.160156 6 40.5 6 Z M 28.5 6 "/>
    <path style=" stroke:none;fill-rule:nonzero;fill:rgb(100%,100%,100%);fill-opacity:0.4;" d="M 28.5 6 C 27.386719 6 26.417969 6.601562 25.898438 7.5 L 7.5 7.5 C 5.839844 7.5 4.5 8.839844 4.5 10.5 L 4.5 10.554688 C 4.660156 9.042969 5.929688 7.875 7.484375 7.875 L 25.882812 7.875 C 26.398438 6.976562 27.367188 6.375 28.480469 6.375 L 40.480469 6.375 C 42.144531 6.375 43.480469 7.714844 43.480469 9.375 L 43.480469 15.316406 C 43.492188 15.214844 43.5 15.109375 43.5 15 L 43.5 9 C 43.5 7.339844 42.160156 6 40.5 6 Z M 28.5 6 "/>
    <path style=" stroke:none;fill-rule:nonzero;fill:rgb(25.882354%,64.705884%,96.078432%);fill-opacity:1;" d="M 6 9 C 4.339844 9 3 10.339844 3 12 L 3 39 C 3 40.660156 4.339844 42 6 42 L 42 42 C 43.660156 42 45 40.660156 45 39 L 45 15 C 45 13.339844 43.660156 12 42 12 L 28.539062 12 C 28.527344 12 28.511719 12 28.5 12 C 27.667969 12 27 11.332031 27 10.5 C 27 9.667969 26.332031 9 25.5 9 Z M 6 9 "/>
    <path style=" stroke:none;fill-rule:nonzero;fill:rgb(100%,100%,100%);fill-opacity:0.4;" d="M 6 9 C 4.339844 9 3 10.339844 3 12 L 3 12.75 C 3 11.089844 4.339844 9.75 6 9.75 L 25.5 9.75 C 26.332031 9.75 27 10.417969 27 11.25 C 27 12.082031 27.667969 12.75 28.5 12.75 C 28.511719 12.75 28.527344 12.75 28.539062 12.75 L 42 12.75 C 43.660156 12.75 45 14.089844 45 15.75 L 45 15 C 45 13.339844 43.660156 12 42 12 L 28.539062 12 C 28.527344 12 28.511719 12 28.5 12 C 27.667969 12 27 11.332031 27 10.5 C 27 9.667969 26.332031 9 25.5 9 Z M 6 9 "/>
    <path style=" stroke:none;fill-rule:nonzero;fill:rgb(0%,0%,0%);fill-opacity:0.4;" d="M 3 38.25 L 3 39 C 3 40.660156 4.339844 42 6 42 L 42 42 C 43.660156 42 45 40.660156 45 39 L 45 38.25 C 45 39.910156 43.660156 41.25 42 41.25 L 6 41.25 C 4.339844 41.25 3 39.910156 3 38.25 Z M 3 38.25 "/>
    <path style=" stroke:none;fill-rule:nonzero;fill:rgb(0%,0%,0%);fill-opacity:0.2;" d="M 3 39 L 3 40.125 C 3 41.785156 4.339844 43.125 6 43.125 L 42 43.125 C 43.660156 43.125 45 41.785156 45 40.125 L 45 39 C 45 40.660156 43.660156 42 42 42 L 6 42 C 4.339844 42 3 40.660156 3 39 Z M 3 39 "/>
    <path style=" stroke:none;fill-rule:nonzero;fill:url(#linear0);" d="M 28.5 6 C 27.386719 6 26.417969 6.601562 25.898438 7.5 L 7.5 7.5 C 6.28125 7.5 5.234375 8.222656 4.765625 9.261719 C 3.722656 9.734375 3 10.78125 3 12 L 3 39 C 3 40.660156 4.339844 42 6 42 L 42 42 C 43.660156 42 45 40.660156 45 39 L 45 15 C 45 13.886719 44.398438 12.917969 43.5 12.402344 L 43.5 9 C 43.5 7.339844 42.160156 6 40.5 6 Z M 28.5 6 "/>
    </g>
    </svg>
    """

    SETTINGS = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 9 4 L 8.25 6.242188 L 5.9375 5.769531 L 3.9375 9.234375 L 5.503906 11 L 3.9375 12.769531 L 5.9375 16.234375 L 8.25 15.757812 L 9 18 L 13 18 L 13.75 15.757812 L 16.0625 16.234375 L 18.0625 12.769531 L 16.496094 11 L 18.0625 9.234375 L 16.0625 5.769531 L 13.75 6.242188 L 13 4 Z M 10 6 L 12 6 L 12.691406 8.074219 L 14.828125 7.636719 L 15.828125 9.367188 L 14.378906 11 L 15.828125 12.636719 L 14.828125 14.367188 L 12.691406 13.929688 L 12 16 L 10 16 L 9.308594 13.929688 L 7.167969 14.367188 L 6.167969 12.636719 L 7.617188 11 L 6.167969 9.367188 L 7.167969 7.636719 L 9.308594 8.074219 Z M 11 9 C 9.890625 9 9 9.890625 9 11 C 9 12.109375 9.890625 13 11 13 C 12.109375 13 13 12.109375 13 11 C 13 9.890625 12.109375 9 11 9 Z M 11 9 "/>
    </g>
    </svg>
    """

    DELETE = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 10 4 L 10 5 L 5 5 L 5 7 L 6 7 L 6 18 L 16 18 L 16 7 L 17 7 L 17 5 L 12 5 L 12 4 Z M 8 7 L 10 7 L 10 16 L 8 16 Z M 12 7 L 14 7 L 14 16 L 12 16 Z M 12 7 "/>
    </g>
    </svg>
    """

    REMOVE = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M14 14l20 20M34 14L14 34"/>
    </g>
    </svg>
    """

    PLAY = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 11 4 C 7.460938 4 4.5625 6.601562 4.078125 10 L 6.101562 10 C 6.5625 7.710938 8.574219 6 11 6 C 13.769531 6 16 8.230469 16 11 C 16 13.769531 13.769531 16 11 16 L 10 16 L 10 18 L 11 18 C 14.878906 18 18 14.878906 18 11 C 18 7.121094 14.878906 4 11 4 Z M 10 7 L 10 12 L 14 12 L 14 10 L 12 10 L 12 7 Z M 4 12 L 4 18 L 9 15 Z M 4 12 "/>
    </g>
    </svg>
    """

    STOP = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 6 6 L 16 6 L 16 16 L 6 16 Z M 6 6 "/>
    </g>
    </svg>
    """

    DROPDOWN_ARROW = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 6 12 L 9 12 L 9 4 L 13 4 L 13 12 L 16 12 L 11 18 Z M 6 12 "/>
    </g>
    </svg>
    """

    CHECKBOX_CHECK = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M18 24l6 6 10-10"/>
    </g>
    </svg>
    """

    MONITOR = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 4 4 L 4 16 L 18 16 L 18 4 Z M 6 6 L 16 6 L 16 14 L 6 14 Z M 10 18 L 10 19 L 12 19 L 12 18 Z M 8 20 L 8 21 L 14 21 L 14 20 Z"/>
    </g>
    </svg>
    """

    SPINNER = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <circle cx="11" cy="11" r="8" fill="none" stroke="currentColor" stroke-width="2" opacity="0.3"/>
    <circle cx="11" cy="11" r="8" fill="none" stroke="currentColor" stroke-width="2" 
            stroke-dasharray="15 35" stroke-linecap="round">
        <animateTransform attributeName="transform" type="rotate" from="0 11 11" to="360 11 11" dur="1s" repeatCount="indefinite"/>
    </circle>
    </g>
    </svg>
    """

    INFO = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 11 4 C 7.121094 4 4 7.121094 4 11 C 4 14.878906 7.121094 18 11 18 C 14.878906 18 18 14.878906 18 11 C 18 7.121094 14.878906 4 11 4 Z M 11 6 C 13.769531 6 16 8.230469 16 11 C 16 13.769531 13.769531 16 11 16 C 8.230469 16 6 13.769531 6 11 C 6 8.230469 8.230469 6 11 6 Z M 10 8 L 10 10 L 12 10 L 12 8 Z M 10 12 L 10 14 L 12 14 L 12 12 Z"/>
    </g>
    </svg>
    """

    ARROW_DOWN = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 6 12 L 9 12 L 9 4 L 13 4 L 13 12 L 16 12 L 11 18 Z M 6 12 "/>
    </g>
    </svg>
    """

    ARROW_UP = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 16 10 L 13 10 L 13 18 L 9 18 L 9 10 L 6 10 L 11 4 Z M 16 10 "/>
    </g>
    </svg>
    """

    SEARCH = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 9 4 C 6.25 4 4 6.25 4 9 C 4 11.75 6.25 14 9 14 C 10.207031 14 11.308594 13.554688 12.15625 12.84375 L 17.65625 18.34375 L 18.34375 17.65625 L 12.84375 12.15625 C 13.554688 11.308594 14 10.207031 14 9 C 14 6.25 11.75 4 9 4 Z M 9 6 C 10.652344 6 12 7.347656 12 9 C 12 10.652344 10.652344 12 9 12 C 7.347656 12 6 10.652344 6 9 C 6 7.347656 7.347656 6 9 6 Z"/>
    </g>
    </svg>
    """

    CHART_BAR = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 5 4 L 5 15 L 4 15 L 4 17 L 5 17 L 5 18 L 7 18 L 7 17 L 18 17 L 18 15 L 17 15 L 17 8 L 14 8 L 14 15 L 12 15 L 12 5 L 9 5 L 9 15 L 7 15 L 7 4 Z M 5 4 "/>
    </g>
    </svg>
    """

    FLOW_CONTROL = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 4 8 L 4 10 L 14 10 L 12 8 L 18 11 L 12 14 L 14 12 L 4 12 L 4 14 L 18 14 L 18 16 L 8 16 L 10 18 L 4 15 L 10 12 L 8 14 L 18 14"/>
    </g>
    </svg>
    """

    SIGNAL = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 4 16 L 4 18 L 6 18 L 6 16 Z M 8 12 L 8 18 L 10 18 L 10 12 Z M 12 8 L 12 18 L 14 18 L 14 8 Z M 16 4 L 16 18 L 18 18 L 18 4 Z"/>
    </g>
    </svg>
    """

    BUFFER = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 4 6 L 4 16 L 8 16 L 8 6 Z M 10 6 L 10 16 L 14 16 L 14 6 Z M 16 6 L 16 16 L 18 16 L 18 6 Z"/>
    </g>
    </svg>
    """

    CLOCK = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 11 4 C 7.121094 4 4 7.121094 4 11 C 4 14.878906 7.121094 18 11 18 C 14.878906 18 18 14.878906 18 11 C 18 7.121094 14.878906 4 11 4 Z M 11 6 C 13.769531 6 16 8.230469 16 11 C 16 13.769531 13.769531 16 11 16 C 8.230469 16 6 13.769531 6 11 C 6 8.230469 8.230469 6 11 6 Z M 11 8 L 11 11 L 14 11 L 14 9 L 13 9 L 13 8 Z"/>
    </g>
    </svg>
    """

    PORT = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 4 9 L 4 13 L 18 13 L 18 9 Z M 6 10 L 7 10 L 7 12 L 6 12 Z M 8 10 L 9 10 L 9 12 L 8 12 Z M 10 10 L 11 10 L 11 12 L 10 12 Z M 12 10 L 13 10 L 13 12 L 12 12 Z M 14 10 L 15 10 L 15 12 L 14 12 Z M 16 10 L 17 10 L 17 12 L 16 12 Z"/>
    </g>
    </svg>
    """

    CONFIGURE = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 9 4 L 8.25 6.242188 L 5.9375 5.769531 L 3.9375 9.234375 L 5.503906 11 L 3.9375 12.769531 L 5.9375 16.234375 L 8.25 15.757812 L 9 18 L 13 18 L 13.75 15.757812 L 16.0625 16.234375 L 18.0625 12.769531 L 16.496094 11 L 18.0625 9.234375 L 16.0625 5.769531 L 13.75 6.242188 L 13 4 Z M 10 6 L 12 6 L 12.691406 8.074219 L 14.828125 7.636719 L 15.828125 9.367188 L 14.378906 11 L 15.828125 12.636719 L 14.828125 14.367188 L 12.691406 13.929688 L 12 16 L 10 16 L 9.308594 13.929688 L 7.167969 14.367188 L 6.167969 12.636719 L 7.617188 11 L 6.167969 9.367188 L 7.167969 7.636719 L 9.308594 8.074219 Z M 11 9 C 9.890625 9 9 9.890625 9 11 C 9 12.109375 9.890625 13 11 13 C 12.109375 13 13 12.109375 13 11 C 13 9.890625 12.109375 9 11 9 Z M 11 9 "/>
    </g>
    </svg>
    """

    # Com0com Settings Icons - Small 16x16 icons for inline display
    TIMING_CLOCK = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="16px" height="16px" viewBox="0 0 16 16" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 8 2 C 5.25 2 3 4.25 3 7 C 3 9.75 5.25 12 8 12 C 10.75 12 13 9.75 13 7 C 13 4.25 10.75 2 8 2 Z M 8 4 C 9.652344 4 11 5.347656 11 7 C 11 8.652344 9.652344 10 8 10 C 6.347656 10 5 8.652344 5 7 C 5 5.347656 6.347656 4 8 4 Z M 8 5 L 8 7 L 10 7 L 10 6 L 9 6 L 9 5 Z"/>
    </g>
    </svg>
    """

    BUFFER_STACK = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="16px" height="16px" viewBox="0 0 16 16" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 2 3 L 2 6 L 14 6 L 14 3 Z M 2 7 L 2 10 L 14 10 L 14 7 Z M 2 11 L 2 14 L 14 14 L 14 11 Z"/>
    </g>
    </svg>
    """

    EXCLUSIVE_LOCK = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="16px" height="16px" viewBox="0 0 16 16" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 8 2 C 5.789062 2 4 3.789062 4 6 L 4 7 L 3 7 L 3 14 L 13 14 L 13 7 L 12 7 L 12 6 C 12 3.789062 10.210938 2 8 2 Z M 8 4 C 9.105469 4 10 4.894531 10 6 L 10 7 L 6 7 L 6 6 C 6 4.894531 6.894531 4 8 4 Z M 8 9 C 8.554688 9 9 9.445312 9 10 C 9 10.554688 8.554688 11 8 11 C 7.445312 11 7 10.554688 7 10 C 7 9.445312 7.445312 9 8 9 Z"/>
    </g>
    </svg>
    """

    PLUGIN_CONNECTOR = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="16px" height="16px" viewBox="0 0 16 16" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 2 6 L 2 10 L 14 10 L 14 6 Z M 4 7 L 5 7 L 5 9 L 4 9 Z M 6 7 L 7 7 L 7 9 L 6 9 Z M 8 7 L 9 7 L 9 9 L 8 9 Z M 10 7 L 11 7 L 11 9 L 10 9 Z M 12 7 L 13 7 L 13 9 L 12 9 Z"/>
    </g>
    </svg>
    """

    GITHUB = """
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" 
              fill="#323130"/>
    </svg>
    """

    PLUS = CREATE  # Alias for CREATE

    MINUS = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 5 10 L 5 12 L 17 12 L 17 10 Z M 5 10 "/>
    </g>
    </svg>
    """

    PAUSE = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 7 5 L 7 17 L 9 17 L 9 5 Z M 13 5 L 13 17 L 15 17 L 15 5 Z"/>
    </g>
    </svg>
    """

    CHEVRON_DOWN = DROPDOWN_ARROW  # Alias for DROPDOWN_ARROW

    WRAP_TEXT = """
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="22px" height="22px" viewBox="0 0 22 22" version="1.1">
    <g id="surface1">
    <defs>
      <style id="current-color-scheme" type="text/css">
       .ColorScheme-Text { color:#eeeeee; } .ColorScheme-Highlight { color:#424242; }
      </style>
     </defs>
    <path style="fill:currentColor" class="ColorScheme-Text" d="M 9 4 C 6.785156 4 5 5.785156 5 8 L 5 18 L 7 18 L 7 14 L 13 14 L 15 12 L 15 8 C 15 5.785156 13.214844 4 11 4 Z M 9 6 L 11 6 C 12.109375 6 13 6.890625 13 8 L 13 12 L 7 12 L 7 8 C 7 6.890625 7.890625 6 9 6 Z M 16 11 L 16 15 L 15 15 L 15 14 L 12 16 L 15 18 L 15 17 L 18 17 L 18 11 Z M 16 11 "/>
    </g>
    </svg>
    """