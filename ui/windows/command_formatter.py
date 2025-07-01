#!/usr/bin/env python3
"""
Enhanced Command Preview Formatter for Hub4com GUI
Professional formatting with accurate ASCII diagrams and muted styling
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor, QFontDatabase
from PyQt6.QtWidgets import QTextEdit
from typing import List, Dict, Optional


class CommandFormatter:
    """Professional formatter for hub4com command preview display"""
    
    def __init__(self):
        """Initialize the command formatter with professional color scheme"""
        # Muted professional color scheme
        self.colors = {
            'default': '#2c2c2c',        # Dark gray for regular text
            'command': '#0066cc',        # Subtle blue for commands
            'port': '#2c5530',           # Dark green for ports
            'parameter': '#5a5a5a',      # Medium gray for parameters
            'value': '#2c2c2c',          # Same as default
            'enabled': '#2a7f3e',        # Muted green for enabled
            'disabled': '#994444',       # Muted red for disabled
            'muted': '#7a7a7a',          # Light gray for separators
            'highlight': '#1a1a1a',      # Darker for emphasis
            'diagram': '#5a5a5a',        # Medium gray for ASCII diagrams
        }
        
        # Character formatting objects
        self.formats = {}
        self._create_formats()
        
    def _create_formats(self):
        """Create QTextCharFormat objects for styling"""
        # Default format
        self.formats['default'] = QTextCharFormat()
        self.formats['default'].setForeground(QColor(self.colors['default']))
        self.formats['default'].setFontFamily("Consolas, 'Courier New', monospace")
        
        # Command format (subtle blue, no bold)
        self.formats['command'] = QTextCharFormat()
        self.formats['command'].setForeground(QColor(self.colors['command']))
        self.formats['command'].setFontFamily("Consolas, 'Courier New', monospace")
        
        # Port format (muted green)
        self.formats['port'] = QTextCharFormat()
        self.formats['port'].setForeground(QColor(self.colors['port']))
        self.formats['port'].setFontFamily("Consolas, 'Courier New', monospace")
        
        # Parameter format (gray)
        self.formats['parameter'] = QTextCharFormat()
        self.formats['parameter'].setForeground(QColor(self.colors['parameter']))
        self.formats['parameter'].setFontFamily("Consolas, 'Courier New', monospace")
        
        # Value format
        self.formats['value'] = QTextCharFormat()
        self.formats['value'].setForeground(QColor(self.colors['value']))
        self.formats['value'].setFontFamily("Consolas, 'Courier New', monospace")
        
        # Status formats
        self.formats['enabled'] = QTextCharFormat()
        self.formats['enabled'].setForeground(QColor(self.colors['enabled']))
        self.formats['enabled'].setFontFamily("Consolas, 'Courier New', monospace")
        
        self.formats['disabled'] = QTextCharFormat()
        self.formats['disabled'].setForeground(QColor(self.colors['disabled']))
        self.formats['disabled'].setFontFamily("Consolas, 'Courier New', monospace")
        
        # Muted format for diagrams and separators
        self.formats['muted'] = QTextCharFormat()
        self.formats['muted'].setForeground(QColor(self.colors['muted']))
        self.formats['muted'].setFontFamily("Consolas, 'Courier New', monospace")
        
        # Diagram format
        self.formats['diagram'] = QTextCharFormat()
        self.formats['diagram'].setForeground(QColor(self.colors['diagram']))
        self.formats['diagram'].setFontFamily("Consolas, 'Courier New', monospace")
    
    def format_command_preview(self, text_edit: QTextEdit, command: List[str], 
                             route_info: Dict) -> None:
        """Format the complete command preview with professional styling"""
        # Clear existing content
        text_edit.clear()
        cursor = text_edit.textCursor()
        
        # Ensure monospace font for the entire widget
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        text_edit.setFont(font)
        
        # Format the command line
        self._format_command_line(cursor, command)
        cursor.insertText("\n", self.formats['default'])
        
        # Add simple separator
        self._insert_separator(cursor)
        cursor.insertText("\n\n", self.formats['default'])
        
        # Add ASCII flow diagram
        self._format_flow_diagram(cursor, route_info)
        cursor.insertText("\n", self.formats['default'])
        
        # Add configuration details
        self._format_configuration(cursor, command, route_info)
        
        # Move cursor to beginning
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        text_edit.setTextCursor(cursor)
    
    def _format_command_line(self, cursor: QTextCursor, command: List[str]) -> None:
        """Format the command line with minimal color coding"""
        if not command:
            return
        
        # Process each command argument
        for i, arg in enumerate(command):
            if i > 0:  # Add space between arguments
                cursor.insertText(" ", self.formats['default'])
            
            # Determine argument type and format accordingly
            if arg.endswith('.exe'):
                cursor.insertText(arg, self.formats['command'])
            elif arg.startswith('--'):
                self._format_parameter(cursor, arg)
            elif '\\' in arg and ('COM' in arg.upper() or 'CNC' in arg.upper()):
                # Port with full path notation
                cursor.insertText(arg, self.formats['port'])
            else:
                cursor.insertText(arg, self.formats['default'])
    
    def _format_parameter(self, cursor: QTextCursor, param: str) -> None:
        """Format a parameter with minimal coloring"""
        if '=' in param:
            param_name, param_value = param.split('=', 1)
            cursor.insertText(param_name + "=", self.formats['parameter'])
            cursor.insertText(param_value, self.formats['value'])
        else:
            cursor.insertText(param, self.formats['parameter'])
    
    def _insert_separator(self, cursor: QTextCursor) -> None:
        """Insert a simple dashed line separator"""
        separator = "-" * 60
        cursor.insertText(separator, self.formats['muted'])
    
    def _format_flow_diagram(self, cursor: QTextCursor, route_info: Dict) -> None:
        """Create ASCII flow diagram using simple characters"""
        incoming_port = route_info.get('incoming_port', 'COM?')
        outgoing_ports = route_info.get('outgoing_ports', [])
        incoming_baud = route_info.get('incoming_baud', '?')
        mode = route_info.get('mode', 'one_way')
        
        if not outgoing_ports:
            cursor.insertText("No output ports configured\n", self.formats['muted'])
            return
        
        cursor.insertText("Data Flow:\n", self.formats['default'])
        
        # Build the diagram based on routing mode
        if mode == 'one_way':
            self._draw_one_way_diagram(cursor, incoming_port, incoming_baud, outgoing_ports)
        elif mode == 'two_way':
            self._draw_two_way_diagram(cursor, incoming_port, incoming_baud, outgoing_ports)
        elif mode == 'full_network':
            self._draw_full_network_diagram(cursor, incoming_port, incoming_baud, outgoing_ports)
    
    def _draw_one_way_diagram(self, cursor: QTextCursor, incoming_port: str, 
                             incoming_baud: str, outgoing_ports: List[Dict]) -> None:
        """Draw one-way routing diagram"""
        if len(outgoing_ports) == 1:
            # Simple one-to-one
            cursor.insertText("  ", self.formats['diagram'])
            cursor.insertText(f"{incoming_port} ({incoming_baud})", self.formats['port'])
            cursor.insertText(" --> hub4com --> ", self.formats['diagram'])
            cursor.insertText(f"{outgoing_ports[0]['port']} ({outgoing_ports[0]['baud']})", self.formats['port'])
            cursor.insertText("\n", self.formats['default'])
        else:
            # One-to-many
            cursor.insertText("  ", self.formats['diagram'])
            cursor.insertText(f"{incoming_port} ({incoming_baud})", self.formats['port'])
            cursor.insertText(" --> hub4com --+", self.formats['diagram'])
            
            for i, port_info in enumerate(outgoing_ports):
                cursor.insertText("\n", self.formats['default'])
                if i < len(outgoing_ports) - 1:
                    cursor.insertText("                      |--> ", self.formats['diagram'])
                else:
                    cursor.insertText("                      +--> ", self.formats['diagram'])
                cursor.insertText(f"{port_info['port']} ({port_info['baud']})", self.formats['port'])
    
    def _draw_two_way_diagram(self, cursor: QTextCursor, incoming_port: str, 
                             incoming_baud: str, outgoing_ports: List[Dict]) -> None:
        """Draw two-way routing diagram"""
        if len(outgoing_ports) == 1:
            # Simple bidirectional
            cursor.insertText("  ", self.formats['diagram'])
            cursor.insertText(f"{incoming_port} ({incoming_baud})", self.formats['port'])
            cursor.insertText(" <--> hub4com <--> ", self.formats['diagram'])
            cursor.insertText(f"{outgoing_ports[0]['port']} ({outgoing_ports[0]['baud']})", self.formats['port'])
            cursor.insertText("\n", self.formats['default'])
        else:
            # Bidirectional one-to-many
            cursor.insertText("  ", self.formats['diagram'])
            cursor.insertText(f"{incoming_port} ({incoming_baud})", self.formats['port'])
            cursor.insertText(" <--> hub4com <--+", self.formats['diagram'])
            
            for i, port_info in enumerate(outgoing_ports):
                cursor.insertText("\n", self.formats['default'])
                if i < len(outgoing_ports) - 1:
                    cursor.insertText("                       |<--> ", self.formats['diagram'])
                else:
                    cursor.insertText("                       +<--> ", self.formats['diagram'])
                cursor.insertText(f"{port_info['port']} ({port_info['baud']})", self.formats['port'])
    
    def _draw_full_network_diagram(self, cursor: QTextCursor, incoming_port: str, 
                                  incoming_baud: str, outgoing_ports: List[Dict]) -> None:
        """Draw full network mode diagram"""
        cursor.insertText("  All ports communicate with all other ports:\n\n", self.formats['diagram'])
        
        # List all ports
        all_ports = [(incoming_port, incoming_baud)]
        all_ports.extend([(p['port'], p['baud']) for p in outgoing_ports])
        
        # Create a simple representation
        cursor.insertText("     +", self.formats['diagram'])
        cursor.insertText("-" * (max(len(p[0]) for p in all_ports) + 20), self.formats['diagram'])
        cursor.insertText("+\n", self.formats['diagram'])
        
        for i, (port, baud) in enumerate(all_ports):
            cursor.insertText("     | ", self.formats['diagram'])
            cursor.insertText(f"{port} ({baud})", self.formats['port'])
            padding = max(len(p[0]) for p in all_ports) - len(port) + 8
            cursor.insertText(" " * padding, self.formats['diagram'])
            cursor.insertText(" |\n", self.formats['diagram'])
        
        cursor.insertText("     +", self.formats['diagram'])
        cursor.insertText("-" * (max(len(p[0]) for p in all_ports) + 20), self.formats['diagram'])
        cursor.insertText("+\n", self.formats['diagram'])
        cursor.insertText("     |       hub4com network hub       |\n", self.formats['diagram'])
        cursor.insertText("     +", self.formats['diagram'])
        cursor.insertText("-" * (max(len(p[0]) for p in all_ports) + 20), self.formats['diagram'])
        cursor.insertText("+", self.formats['diagram'])
    
    def _format_configuration(self, cursor: QTextCursor, command: List[str], 
                            route_info: Dict) -> None:
        """Format configuration details in a clean layout"""
        cursor.insertText("\n\nConfiguration:\n", self.formats['default'])
        
        # Route mode
        mode_names = {
            'one_way': 'One-way',
            'two_way': 'Two-way',
            'full_network': 'Full network'
        }
        mode_display = mode_names.get(route_info.get('mode', 'one_way'), 'One-way')
        
        # Extract route parameter from command for accuracy
        route_param = next((arg for arg in command if arg.startswith('--route=') or 
                           arg.startswith('--bi-route=')), '')
        if route_param:
            route_value = route_param.split('=')[1]
            cursor.insertText(f"  Route mode: {mode_display} ({route_value})\n", self.formats['default'])
        else:
            cursor.insertText(f"  Route mode: {mode_display}\n", self.formats['default'])
        
        # CTS handshaking
        cursor.insertText("  CTS handshaking: ", self.formats['default'])
        if route_info.get('cts_disabled', False):
            cursor.insertText("Disabled", self.formats['disabled'])
        else:
            cursor.insertText("Enabled", self.formats['enabled'])
        cursor.insertText("\n", self.formats['default'])
        
        # Source port
        incoming_port = route_info.get('incoming_port', 'COM?')
        incoming_baud = route_info.get('incoming_baud', '?')
        cursor.insertText(f"  Source port: ", self.formats['default'])
        cursor.insertText(f"{incoming_port} @ {incoming_baud} baud\n", self.formats['port'])
        
        # Target ports
        outgoing_ports = route_info.get('outgoing_ports', [])
        if outgoing_ports:
            cursor.insertText("  Target ports: ", self.formats['default'])
            port_list = [f"{p['port']} @ {p['baud']} baud" for p in outgoing_ports]
            cursor.insertText(", ".join(port_list), self.formats['port'])
            cursor.insertText("\n", self.formats['default'])
        
        # Additional options if enabled
        additional_options = []
        if route_info.get('echo_enabled', False):
            additional_options.append("Echo to source")
        if route_info.get('flow_control_enabled', False):
            additional_options.append("Flow control routing")
        if route_info.get('disable_default_fc', False):
            additional_options.append("No default flow control")
        
        if additional_options:
            cursor.insertText("  Additional options: ", self.formats['default'])
            cursor.insertText(", ".join(additional_options), self.formats['parameter'])
            cursor.insertText("\n", self.formats['default'])


def parse_command_info(command: List[str], route_info: Dict) -> Dict:
    """Parse command and route information for formatting"""
    if not command:
        return {}
    
    # Extract port information from command
    ports = []
    baud_rates = []
    
    i = 0
    while i < len(command):
        if command[i].startswith('--baud='):
            baud_rates.append(command[i].split('=')[1])
        elif ('COM' in command[i].upper() or 'CNC' in command[i].upper()) and not command[i].startswith('--'):
            # Extract just the port name from paths like \\.\COM1
            port_name = command[i]
            if port_name.startswith('\\\\.\\'):
                port_name = port_name[4:]  # Remove \\.\
            ports.append(port_name)
        i += 1
    
    # Determine incoming vs outgoing ports
    incoming_port = ports[0] if ports else 'COM?'
    incoming_baud = baud_rates[0] if baud_rates else '?'
    
    outgoing_ports = []
    for i in range(1, len(ports)):
        baud = baud_rates[i] if i < len(baud_rates) else '?'
        outgoing_ports.append({
            'port': ports[i],
            'baud': baud
        })
    
    # Check for CTS disabled
    cts_disabled = any('--octs=off' in arg for arg in command)
    
    return {
        'incoming_port': incoming_port,
        'incoming_baud': incoming_baud,
        'outgoing_ports': outgoing_ports,
        'cts_disabled': cts_disabled,
        'mode': route_info.get('mode', 'one_way')
    }


# Example outputs:
"""
ONE-WAY ROUTING (Single Output):
================================

hub4com.exe --route=0:1 --octs=off --baud=115200 \\.\COM1 --baud=115200 \\.\COM131
------------------------------------------------------------

Port Mapping & Data Flow Visualization:

     +-----------------------------+
     |           SOURCE            |
     |-----------------------------|
     | Port: COM1                  |
     | Baud: 115200                |
     | Status: [READY]             |
     +-----------------------------+

                      |
                      V
          +--------------------+
          |    [ HUB4COM ]     |
          |   Signal Splitter  |
          |   >>> One-Way >>>   |
          +--------------------+
                      |
                      V
     +-----------------------------+
     |           TARGET            |
     |-----------------------------|
     | Port: COM131                |
     | Baud: 115200                |
     | Status: [READY]             |
     +-----------------------------+

Configuration:
  Route mode: One-way (0:1)
  CTS handshaking: Disabled
  Source port: COM1 @ 115200 baud
  Target ports: COM131 @ 115200 baud


TWO-WAY ROUTING (Multiple Outputs):
===================================

hub4com.exe --bi-route=0:1,2 --baud=9600 \\.\COM1 --baud=9600 \\.\CNCB0 --baud=9600 \\.\CNCB1
------------------------------------------------------------

Port Mapping & Data Flow Visualization:

     +-----------------------------+
     |           SOURCE            |
     |-----------------------------|
     | Port: COM1                  |
     | Baud: 9600                  |
     | Status: [READY]             |
     +-----------------------------+

                      ^
                      |
                  TX  |  RX
                  >>> | <<<
                      |
                      V
          +--------------------+
          |    [ HUB4COM ]     |
          |  Bidirectional     |
          |   <-> Two-Way <->   |
          +--------------------+
                      |
          +-----------+-----------+
          |           |           |
         <->         <->         <->
          |           |           |
          V           V           V
     +---------------+
     | TARGET 1      |
     |---------------|
     | CNCB0         |
     | 9600 baud     |
     +---------------+

     +---------------+
     | TARGET 2      |
     |---------------|
     | CNCB1         |
     | 9600 baud     |
     +---------------+

Configuration:
  Route mode: Two-way (0:1,2)
  CTS handshaking: Enabled
  Source port: COM1 @ 9600 baud
  Target ports: CNCB0 @ 9600 baud, CNCB1 @ 9600 baud


FULL NETWORK MODE:
==================

hub4com.exe --route=All:All --baud=115200 \\.\COM1 --baud=115200 \\.\COM131 --baud=115200 \\.\COM141
------------------------------------------------------------

Port Mapping & Data Flow Visualization:

     +========================================+
     |           HUB4COM NETWORK              |
     |        All-to-All Communication        |
     +========================================+
     |                                        |
     |  [PORT 1] --<>-- COM1 @ 115200        |
     |                                        |
     |  [PORT 2] --<>-- COM131 @ 115200      |
     |                                        |
     |  [PORT 3] --<>-- COM141 @ 115200      |
     |                                        |
     +----------------------------------------+

     Legend: <> = Bidirectional data exchange
     Each port can send/receive to/from all others

Configuration:
  Route mode: Full network (All:All)
  CTS handshaking: Enabled
  Source port: COM1 @ 115200 baud
  Target ports: COM131 @ 115200 baud, COM141 @ 115200 baud
"""