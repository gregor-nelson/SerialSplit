#!/usr/bin/env python3
"""
Enhanced Port Information Widget - Compact single-line design
Windows 10 Task Manager inspired layout for maximum information density
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QSizePolicy, QVBoxLayout)
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QBrush, QPolygonF
import time

from core.core import SerialPortInfo, SerialPortMonitor
from ui.theme.theme import ThemeManager, AppStyles, AppDimensions, AppColors, AppFonts
from ui.theme.icons.icons import AppIcons


class CombinedDataChart(QWidget):
    """Combined RX/TX data chart with professional styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(150, 30)  # Reduced minimum size for better slider utilization
        self.setMaximumHeight(16777215)  # Remove height restrictions
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.rx_data = []
        self.tx_data = []
        self.timestamps = []
        self.max_points = 120  # Higher resolution for smoother curves and better granularity
        self.max_value = 1
        
    def add_values(self, rx_value: float, tx_value: float):
        """Add new RX and TX values with timestamp"""
        current_time = time.time()
        
        # Add new data points
        self.rx_data.append(rx_value)
        self.tx_data.append(tx_value)
        self.timestamps.append(current_time)
        
        # Keep only the last max_points
        if len(self.rx_data) > self.max_points:
            self.rx_data.pop(0)
            self.tx_data.pop(0)
            self.timestamps.pop(0)
        
        # Update max value for scaling
        all_values = self.rx_data + self.tx_data
        self.max_value = max(max(all_values) if all_values else 0, 1)
        
        self.update()
    
    def clear_data(self):
        """Clear all data points"""
        self.rx_data.clear()
        self.tx_data.clear()
        self.timestamps.clear()
        self.max_value = 1
        self.update()
    
    def paintEvent(self, event):
        """Paint the combined chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(AppColors.BACKGROUND_LIGHT))
        
        # Define margins for chart area
        margin_top = 8
        margin_bottom = 8
        margin_left = 4
        margin_right = 4
        
        # Calculate chart area with margins
        chart_width = self.width() - margin_left - margin_right
        chart_height = self.height() - margin_top - margin_bottom
        
        # Draw subtle grid lines within chart area
        painter.setPen(QPen(QColor(AppColors.BORDER_DEFAULT), 0.5))
        width = chart_width
        height = chart_height
        
        # Only draw grid if there's enough space
        if height > 40:
            # Horizontal grid lines within chart area
            grid_lines = min(4, height // 20)  # Adaptive grid based on height
            for i in range(1, grid_lines):
                y = margin_top + height * i / grid_lines
                painter.drawLine(margin_left, int(y), margin_left + width, int(y))
        
        if width > 100:
            # Vertical grid lines within chart area
            grid_lines = min(6, width // 40)  # Adaptive grid based on width
            for i in range(1, grid_lines):
                x = margin_left + width * i / grid_lines
                painter.drawLine(int(x), margin_top, int(x), margin_top + height)
        
        # Draw data if available within chart area
        if len(self.rx_data) > 1 and self.max_value > 0:
            self._draw_data_line(painter, self.rx_data, QColor("#28a745"), margin_left, margin_top, chart_width, chart_height)  # Green for RX
            self._draw_data_line(painter, self.tx_data, QColor("#007bff"), margin_left, margin_top, chart_width, chart_height)  # Blue for TX
    
    def _draw_data_line(self, painter, data, color, margin_left, margin_top, chart_width, chart_height):
        """Draw a data line with fill area within chart bounds"""
        if len(data) < 2:
            return
        
        x_step = chart_width / (len(data) - 1)
        
        # Create path for line within chart area
        points = []
        for i, value in enumerate(data):
            x = margin_left + i * x_step
            y = margin_top + chart_height - (value / self.max_value * chart_height)
            points.append((x, y))
        
        # Draw fill area
        fill_color = QColor(color)
        fill_color.setAlpha(40)  # Semi-transparent
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(fill_color, 0))
        
        # Create fill polygon from points to bottom of chart area
        fill_polygon = QPolygonF()
        for x, y in points:
            fill_polygon.append(QPointF(x, y))
        fill_polygon.append(QPointF(margin_left + chart_width, margin_top + chart_height))
        fill_polygon.append(QPointF(margin_left, margin_top + chart_height))
        
        painter.drawPolygon(fill_polygon)
        
        # Draw line with improved styling
        painter.setBrush(QBrush())
        painter.setPen(QPen(color, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        
        for i in range(1, len(points)):
            x1, y1 = points[i-1]
            x2, y2 = points[i]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))


class EnhancedPortInfoWidget(QWidget):
    """Compact port information widget with inline monitoring display"""
    
    # Signals for thread-safe UI updates
    tx_success_signal = pyqtSignal()
    tx_error_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.port_monitor = None
        self.current_port = None
        self.last_stats = None  # Store last received stats
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_chart)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Connect signals for thread-safe UI updates
        self.tx_success_signal.connect(self._show_tx_feedback)
        self.tx_error_signal.connect(self._show_tx_error)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the responsive UI layout"""
        # Main container with flexible constraints for responsive scaling
        self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Main vertical layout for header + chart
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Remove top alignment to allow chart to expand fully
        
        # Info panel (header row) - flexible width container
        self.info_panel = QWidget()
        self.info_panel.setVisible(False)
        self.info_panel.setFixedHeight(28)  # Fixed height for header
        self.info_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.info_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {AppColors.BACKGROUND_LIGHT};
            }}
        """)
        
        panel_layout = QHBoxLayout(self.info_panel)
        panel_layout.setContentsMargins(
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_SMALL,
            AppDimensions.SPACING_MEDIUM,
            AppDimensions.SPACING_SMALL
        )
        panel_layout.setSpacing(AppDimensions.SPACING_LARGE)
        
        # Port info section (left)
        port_section = QHBoxLayout()
        port_section.setSpacing(AppDimensions.SPACING_SMALL)
        port_section.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Port status indicator (small colored bar)
        self.status_indicator = QFrame()
        # Will set size after port_label is created to match its font height
        self.status_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.TEXT_DISABLED};
                border: none;
            }}
        """)
        port_section.addWidget(self.status_indicator, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Port name and type
        self.port_label = QLabel("")
        self.port_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.DEFAULT_SIZE};
                background: transparent;
                border: none;
            }}
        """)
        self.port_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        port_section.addWidget(self.port_label)
        
        # Set status indicator height to match port label font height
        label_font_metrics = self.port_label.fontMetrics()
        label_height = label_font_metrics.height()
        self.status_indicator.setFixedSize(3, label_height)
        
        panel_layout.addLayout(port_section)
        
        # Monitoring data section (center) - professional header style
        monitor_section = QHBoxLayout()
        monitor_section.setSpacing(AppDimensions.SPACING_MEDIUM)
        
        # RX indicator with colored bullet
        self.rx_indicator = QLabel("●")
        self.rx_indicator.setStyleSheet(f"""
            QLabel {{
                color: #28a745;
                font-size: 12pt;
                background: transparent;
            }}
        """)
        monitor_section.addWidget(self.rx_indicator)
        
        self.rx_label = QLabel("RX")
        self.rx_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.SMALL_SIZE};
                background: transparent;
            }}
        """)
        monitor_section.addWidget(self.rx_label)
        
        self.rx_value = QLabel("0 B/s")
        self.rx_value.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.CONSOLE.family()};
                font-size: {AppFonts.SMALL_SIZE};
                background: transparent;
                min-width: 60px;
            }}
        """)
        monitor_section.addWidget(self.rx_value)
        
        # TX indicator with colored bullet
        self.tx_indicator = QLabel("●")
        self.tx_indicator.setStyleSheet(f"""
            QLabel {{
                color: #007bff;
                font-size: 12pt;
                background: transparent;
            }}
        """)
        monitor_section.addWidget(self.tx_indicator)
        
        self.tx_label = QLabel("TX")
        self.tx_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.DEFAULT_FAMILY};
                font-size: {AppFonts.SMALL_SIZE};
                background: transparent;
            }}
        """)
        monitor_section.addWidget(self.tx_label)
        
        self.tx_value = QLabel("0 B/s")
        self.tx_value.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.CONSOLE.family()};
                font-size: {AppFonts.SMALL_SIZE};
                background: transparent;
                min-width: 60px;
            }}
        """)
        monitor_section.addWidget(self.tx_value)
        
        # Hide monitoring section initially
        self.monitor_container = QWidget()
        monitor_layout = QHBoxLayout(self.monitor_container)
        monitor_layout.setContentsMargins(0, 0, 0, 0)
        monitor_layout.addLayout(monitor_section)
        self.monitor_container.setVisible(False)
        
        panel_layout.addWidget(self.monitor_container)
        panel_layout.addStretch()
        
        # Control section (right)
        control_section = QHBoxLayout()
        control_section.setSpacing(AppDimensions.SPACING_SMALL)
        
        # Time indicator
        self.time_label = QLabel("")
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DISABLED};
                font-family: {AppFonts.CONSOLE.family()};
                font-size: {AppFonts.SMALL_SIZE};
                background: transparent;
            }}
        """)
        self.time_label.setVisible(False)
        control_section.addWidget(self.time_label)
        
        # TX Test button
        self.tx_test_btn = QPushButton()
        self.tx_test_btn.setFixedSize(24, 24)
        self.tx_test_btn.setToolTip("Send TX test")
        self.tx_test_btn.clicked.connect(self.send_test_tx)
        self.tx_test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_HOVER};
                border: 1px solid {AppColors.BORDER_DEFAULT};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_PRESSED};
            }}
        """)
        self._update_tx_test_button_icon()
        self.tx_test_btn.setVisible(False)  # Hidden initially
        control_section.addWidget(self.tx_test_btn)
        
        # Monitor button
        self.monitor_btn = QPushButton()
        self.monitor_btn.setFixedSize(24, 24)
        self.monitor_btn.setToolTip("Start port monitoring")
        self.monitor_btn.clicked.connect(self.toggle_monitoring)
        self.monitor_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {AppColors.BUTTON_HOVER};
                border: 1px solid {AppColors.BORDER_DEFAULT};
            }}
            QPushButton:pressed {{
                background-color: {AppColors.BUTTON_PRESSED};
            }}
        """)
        self._update_monitor_button_icon(False)
        control_section.addWidget(self.monitor_btn)
        
        panel_layout.addLayout(control_section)
        
        # Add header to main layout
        layout.addWidget(self.info_panel)
        
        # Separator line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator.setStyleSheet(f"""
            QFrame {{
                color: {AppColors.BORDER_DEFAULT};
                background-color: {AppColors.BORDER_DEFAULT};
                border: none;
                max-height: 1px;
            }}
        """)
        self.separator.setVisible(False)
        layout.addWidget(self.separator)
        
        # Combined chart section - pre-allocated space that fills vertically
        self.chart_container = QWidget()
        self.chart_container.setVisible(False)
        self.chart_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chart_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        chart_layout = QVBoxLayout(self.chart_container)
        chart_layout.setContentsMargins(AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL, AppDimensions.SPACING_MEDIUM, AppDimensions.SPACING_SMALL)
        chart_layout.setSpacing(0)
        
        self.data_chart = CombinedDataChart()
        chart_layout.addWidget(self.data_chart)
        
        layout.addWidget(self.chart_container)
        
        # Invisible spacer to maintain consistent width when chart is hidden
        self.chart_spacer = QWidget()
        self.chart_spacer.setVisible(True)  # Always visible to maintain width
        # Remove minimum width constraint for flexible scaling
        self.chart_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.chart_spacer)
    
    def _apply_status_style(self, style_type: str):
        """Apply the status indicator color"""
        status_colors = {
            "available": AppColors.SUCCESS_PRIMARY,
            "in_use": AppColors.WARNING_PRIMARY,
            "unavailable": AppColors.ERROR_PRIMARY,
            "virtual": AppColors.ACCENT_BLUE,
            "moxa": AppColors.ACCENT_ORANGE,
            "info": AppColors.TEXT_DISABLED
        }
        
        color = status_colors.get(style_type, AppColors.TEXT_DISABLED)
        
        self.status_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
            }}
        """)
    
    def _update_monitor_button_icon(self, is_monitoring: bool):
        """Update monitor button icon"""
        from ui.theme.theme import IconManager
        
        if is_monitoring:
            icon = IconManager.create_svg_icon(
                AppIcons.STOP,
                AppColors.TEXT_DEFAULT,
                IconManager.get_scaled_size(14)
            )
            self.monitor_btn.setToolTip("Stop monitoring")
        else:
            icon = IconManager.create_svg_icon(
                AppIcons.PLAY,
                AppColors.TEXT_DEFAULT,
                IconManager.get_scaled_size(14)
            )
            self.monitor_btn.setToolTip("Start monitoring")
        
        self.monitor_btn.setIcon(icon)
        self.monitor_btn.setIconSize(IconManager.get_scaled_size(14))
    
    def _update_tx_test_button_icon(self):
        """Update TX test button icon"""
        from ui.theme.theme import IconManager
        
        icon = IconManager.create_svg_icon(
            AppIcons.ARROW_UP,
            AppColors.TEXT_DEFAULT,
            IconManager.get_scaled_size(14)
        )
        self.tx_test_btn.setIcon(icon)
        self.tx_test_btn.setIconSize(IconManager.get_scaled_size(14))
    
    def _update_chart(self):
        """Update chart visualization"""
        if self.port_monitor and self.port_monitor.monitoring and self.last_stats:
            # Use the last received stats
            rx_rate = self.last_stats.get("rx_rate", 0)
            tx_rate = self.last_stats.get("tx_rate", 0)
            self.data_chart.add_values(rx_rate, tx_rate)
    
    def update_port_info(self, port_info: SerialPortInfo, enhanced_display: str):
        """Update port information display"""
        self.current_port = port_info
        
        # Update status indicator
        if port_info.is_moxa:
            style_type = "moxa"
        elif port_info.port_type == "Physical":
            style_type = "available"
        else:
            style_type = "virtual"
        
        self._apply_status_style(style_type)
        
        # Update port label with compact info
        port_text = f"{port_info.port_name}"
        if port_info.description and port_info.description != "N/A":
            # Truncate description to fit
            desc = port_info.description[:30] + "..." if len(port_info.description) > 30 else port_info.description
            port_text += f" - {desc}"
        
        self.port_label.setText(port_text)
        self.info_panel.setVisible(True)
        
        # Show/hide monitor controls based on port type
        can_monitor = (port_info.port_type == "Physical" or 
                      port_info.port_type.startswith("Virtual"))
        
        self.monitor_btn.setVisible(can_monitor)
        self.tx_test_btn.setVisible(can_monitor)  # Show TX test when monitoring is available
        
        if not can_monitor:
            self.stop_monitoring()
    
    def toggle_monitoring(self):
        """Toggle port monitoring on/off"""
        if not self.current_port:
            return
            
        if self.port_monitor and self.port_monitor.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring the current port"""
        if not self.current_port:
            return
            
        # Stop existing monitor
        self.stop_monitoring()
        
        # Create new monitor
        self.port_monitor = SerialPortMonitor(self.current_port.port_name, 9600)
        self.port_monitor.stats_updated.connect(self.update_monitoring_stats)
        self.port_monitor.error_occurred.connect(self.handle_monitoring_error)
        
        if self.port_monitor.start_monitoring():
            self._update_monitor_button_icon(True)
            self.monitor_container.setVisible(True)
            self.chart_container.setVisible(True)
            self.separator.setVisible(True)
            self.time_label.setVisible(True)
            self.chart_spacer.setVisible(False)  # Hide spacer when chart is active
        
        # Allow chart to expand to fill available space without height limits
        self.chart_container.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
        self.data_chart.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
        self.update_timer.start(10)  # Update chart 4x per second
    
    def stop_monitoring(self):
        """Stop port monitoring"""
        if self.port_monitor:
            self.port_monitor.stop_monitoring()
            self.port_monitor = None
            
        self.update_timer.stop()
        self._update_monitor_button_icon(False)
        self.monitor_container.setVisible(False)
        self.chart_container.setVisible(False)
        self.separator.setVisible(False)
        self.time_label.setVisible(False)
        self.chart_spacer.setVisible(True)  # Show spacer to maintain width
        
        # Reset chart size constraints
        self.chart_container.setMaximumHeight(0)
        self.data_chart.setMaximumHeight(0)
        
        # Reset displays
        self.rx_value.setText("0 B/s")
        self.tx_value.setText("0 B/s")
        self.data_chart.clear_data()
    
    def update_monitoring_stats(self, stats):
        """Update monitoring statistics display"""
        # Store the latest stats
        self.last_stats = stats
        
        # Format compact rate display
        rx_rate = stats.get("rx_rate", 0)
        tx_rate = stats.get("tx_rate", 0)
        
        # Professional formatting with units
        if rx_rate < 1024:
            rx_text = f"{rx_rate:.0f} B/s"
        elif rx_rate < 1024 * 1024:
            rx_text = f"{rx_rate/1024:.1f} K/s"
        else:
            rx_text = f"{rx_rate/(1024*1024):.1f} M/s"
            
        if tx_rate < 1024:
            tx_text = f"{tx_rate:.0f} B/s"
        elif tx_rate < 1024 * 1024:
            tx_text = f"{tx_rate/1024:.1f} K/s"
        else:
            tx_text = f"{tx_rate/(1024*1024):.1f} M/s"
        
        self.rx_value.setText(rx_text)
        self.tx_value.setText(tx_text)
        
        # Update time
        running_time = int(stats.get("running_time", 0))
        if running_time < 60:
            time_str = f"{running_time}s"
        else:
            time_str = f"{running_time//60}:{running_time%60:02d}"
        self.time_label.setText(time_str)
        
        # Dynamic text weight based on activity
        rx_weight = AppFonts.BOLD_WEIGHT if rx_rate > 0 else AppFonts.NORMAL_WEIGHT
        tx_weight = AppFonts.BOLD_WEIGHT if tx_rate > 0 else AppFonts.NORMAL_WEIGHT
        
        self.rx_value.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.CONSOLE.family()};
                font-size: {AppFonts.SMALL_SIZE};
                font-weight: {rx_weight};
                background: transparent;
                min-width: 60px;
            }}
        """)
        
        self.tx_value.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.TEXT_DEFAULT};
                font-family: {AppFonts.CONSOLE.family()};
                font-size: {AppFonts.SMALL_SIZE};
                font-weight: {tx_weight};
                background: transparent;
                min-width: 60px;
            }}
        """)
    
    def handle_monitoring_error(self, error_msg):
        """Handle monitoring errors"""
        self.stop_monitoring()
        
        # Update port label to show error
        if "network" in error_msg.lower():
            error_text = " [Network unreachable]"
        elif "busy" in error_msg.lower():
            error_text = " [Port busy]"
        elif "disconnected" in error_msg.lower():
            error_text = " [Disconnected]"
        else:
            error_text = " [Error]"
            
        current_text = self.port_label.text()
        if not current_text.endswith("]"):
            self.port_label.setText(current_text + error_text)
    
    def set_port_type(self, port_type: str):
        """Set the port type and apply appropriate styling"""
        if hasattr(self, 'status_indicator'):
            self._apply_status_style(port_type)
    
    def hide_all(self):
        """Hide all port information"""
        self.info_panel.setVisible(False)
        self.separator.setVisible(False)
        self.chart_spacer.setVisible(False)  # Hide spacer when widget is hidden
        self.stop_monitoring()
    
    def send_test_tx(self):
        """Send a test TX transmission"""
        if not self.current_port:
            return
        
        test_message = "Serial TX Test\r\n"
        
        # Use shared connection if monitoring is active
        if self.port_monitor and self.port_monitor.monitoring:
            # Use the shared serial connection
            success = self.port_monitor.send_data(test_message)
            if success:
                self.tx_success_signal.emit()
            else:
                self.tx_error_signal.emit("TX failed")
        else:
            # Fallback to independent connection when not monitoring
            import serial
            import threading
            
            def send_test_data():
                try:
                    # Open port briefly to send test data
                    with serial.Serial(self.current_port.port_name, 9600, timeout=1) as ser:
                        ser.write(test_message.encode('utf-8'))
                        ser.flush()  # Ensure data is sent immediately
                        
                        # Brief visual feedback by temporarily highlighting TX indicator
                        self.tx_success_signal.emit()
                        
                except serial.SerialException as e:
                    # Handle port access errors silently or show in status
                    error_msg = str(e)
                    if "busy" in error_msg.lower() or "access" in error_msg.lower():
                        self.tx_error_signal.emit("Port busy")
                    else:
                        self.tx_error_signal.emit("TX failed")
                except Exception as e:
                    self.tx_error_signal.emit("TX error")
            
            # Run in thread to avoid blocking UI
            threading.Thread(target=send_test_data, daemon=True).start()
    
    def _show_tx_feedback(self):
        """Show visual feedback for successful TX test"""
        # Briefly highlight TX indicator
        original_style = self.tx_indicator.styleSheet()
        
        # Highlight style
        self.tx_indicator.setStyleSheet(f"""
            QLabel {{
                color: #007bff;
                font-size: 12pt;
                background: {AppColors.SUCCESS_PRIMARY};
                padding: 2px;
            }}
        """)
        
        # Reset after 200ms
        QTimer.singleShot(200, lambda: self.tx_indicator.setStyleSheet(original_style))
    
    def _show_tx_error(self, error_type=None):
        """Show visual feedback for TX test error"""
        # Briefly show error on TX indicator
        original_style = self.tx_indicator.styleSheet()
        
        # Error style
        self.tx_indicator.setStyleSheet(f"""
            QLabel {{
                color: {AppColors.ERROR_PRIMARY};
                font-size: 12pt;
                background: transparent;
            }}
        """)
        
        # Reset after 500ms
        QTimer.singleShot(500, lambda: self.tx_indicator.setStyleSheet(original_style))