#!/usr/bin/env python3
"""
NMEA 0183 Device Simulator with GUI
Professional marine navigation simulator with comprehensive message support
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import time
import random
import math
from datetime import datetime, timezone
import threading
import queue

class NMEASimulatorCore:
    def __init__(self):
        # Base coordinates and navigation data
        self.base_lat = 40.7128  # New York City latitude
        self.base_lon = -74.0060  # New York City longitude
        self.altitude = 10.0
        self.speed_knots = 2.5
        self.course = 45.0
        self.heading = 45.0
        
        # Environmental data
        self.depth_meters = 25.0
        self.water_temp = 15.5  # Celsius
        self.wind_speed = 8.0  # knots
        self.wind_direction = 180.0  # degrees
        self.barometric_pressure = 1013.25  # hPa
        self.air_temp = 20.0  # Celsius
        self.humidity = 65.0  # percent
        
        # Attitude data
        self.roll = 0.0
        self.pitch = 0.0
        self.heave = 0.0
        
        # GPS/GNSS data
        self.satellites_in_view = 12
        self.hdop = 1.2
        self.vdop = 1.8
        self.pdop = 2.1

    def calculate_checksum(self, sentence):
        """Calculate NMEA checksum for a sentence (without $ and *)"""
        checksum = 0
        for char in sentence:
            checksum ^= ord(char)
        return f"{checksum:02X}"

    def format_nmea_sentence(self, sentence):
        """Format a complete NMEA sentence with checksum"""
        checksum = self.calculate_checksum(sentence)
        return f"${sentence}*{checksum}\r\n"

    def format_ais_sentence(self, sentence):
        """Format AIS sentence (starts with !)"""
        checksum = self.calculate_checksum(sentence)
        return f"!{sentence}*{checksum}\r\n"

    def format_coordinate(self, coord, is_latitude=True):
        """Convert decimal degrees to NMEA format"""
        abs_coord = abs(coord)
        degrees = int(abs_coord)
        minutes = (abs_coord - degrees) * 60
        
        if is_latitude:
            formatted = f"{degrees:02d}{minutes:07.4f}"
            hemisphere = 'N' if coord >= 0 else 'S'
        else:
            formatted = f"{degrees:03d}{minutes:07.4f}"
            hemisphere = 'E' if coord >= 0 else 'W'
            
        return formatted, hemisphere

    def get_current_time(self):
        """Get current UTC time in HHMMSS.SS format"""
        now = datetime.now(timezone.utc)
        return f"{now.hour:02d}{now.minute:02d}{now.second:02d}.{now.microsecond//10000:02d}"

    def get_current_date(self):
        """Get current date in DDMMYY format"""
        now = datetime.now(timezone.utc)
        return f"{now.day:02d}{now.month:02d}{now.year % 100:02d}"

    def add_position_variation(self):
        """Add small random variations to simulate movement/drift"""
        lat_var = random.uniform(-0.001, 0.001)
        lon_var = random.uniform(-0.001, 0.001)
        alt_var = random.uniform(-5, 5)
        
        return (self.base_lat + lat_var, 
                self.base_lon + lon_var, 
                self.altitude + alt_var)

    def simulate_dynamics(self):
        """Update dynamic values with realistic variations"""
        # Position and navigation
        if random.random() < 0.1:
            self.speed_knots = max(0, self.speed_knots + random.uniform(-1, 1))
        if random.random() < 0.05:
            self.course = (self.course + random.uniform(-5, 5)) % 360
            self.heading = (self.heading + random.uniform(-2, 2)) % 360
        
        # Environmental
        self.depth_meters += random.uniform(-0.2, 0.2)
        self.depth_meters = max(1.0, self.depth_meters)
        
        self.wind_speed += random.uniform(-0.5, 0.5)
        self.wind_speed = max(0, self.wind_speed)
        self.wind_direction = (self.wind_direction + random.uniform(-2, 2)) % 360
        
        # Attitude (simulate sea motion)
        self.roll = math.sin(time.time() * 0.5) * 3 + random.uniform(-1, 1)
        self.pitch = math.sin(time.time() * 0.3) * 2 + random.uniform(-0.5, 0.5)
        self.heave = math.sin(time.time() * 0.8) * 0.3 + random.uniform(-0.1, 0.1)

    # Message Generators
    def generate_gga(self, talker='GP'):
        """Generate GGA sentence"""
        current_time = self.get_current_time()
        lat, lon, alt = self.add_position_variation()
        lat_str, lat_hem = self.format_coordinate(lat, True)
        lon_str, lon_hem = self.format_coordinate(lon, False)
        
        sentence = f"{talker}GGA,{current_time},{lat_str},{lat_hem},{lon_str},{lon_hem},1,{random.randint(8, 12):02d},{self.hdop:.1f},{alt:.1f},M,{random.uniform(-30, 30):.1f},M,,"
        return self.format_nmea_sentence(sentence)

    def generate_rmc(self, talker='GP'):
        """Generate RMC sentence"""
        current_time = self.get_current_time()
        current_date = self.get_current_date()
        lat, lon, _ = self.add_position_variation()
        lat_str, lat_hem = self.format_coordinate(lat, True)
        lon_str, lon_hem = self.format_coordinate(lon, False)
        
        sentence = f"{talker}RMC,{current_time},A,{lat_str},{lat_hem},{lon_str},{lon_hem},{self.speed_knots:.1f},{self.course:.1f},{current_date},{random.uniform(0, 20):.1f},{random.choice(['E', 'W'])},A"
        return self.format_nmea_sentence(sentence)

    def generate_gll(self, talker='GP'):
        """Generate GLL sentence"""
        lat, lon, _ = self.add_position_variation()
        current_time = self.get_current_time()
        lat_str, lat_hem = self.format_coordinate(lat, True)
        lon_str, lon_hem = self.format_coordinate(lon, False)
        
        sentence = f"{talker}GLL,{lat_str},{lat_hem},{lon_str},{lon_hem},{current_time},A,A"
        return self.format_nmea_sentence(sentence)

    def generate_gsa(self, talker='GP'):
        """Generate GSA sentence"""
        satellites = [f"{i:02d}" for i in random.sample(range(1, 32), random.randint(8, 12))]
        while len(satellites) < 12:
            satellites.append("")
        
        sat_string = ",".join(satellites[:12])
        sentence = f"{talker}GSA,A,3,{sat_string},{self.pdop:.1f},{self.hdop:.1f},{self.vdop:.1f}"
        return self.format_nmea_sentence(sentence)

    def generate_gsv(self, talker='GP'):
        """Generate GSV sentence"""
        total_sats = self.satellites_in_view
        sentences_needed = math.ceil(total_sats / 4)
        
        # Return just the first sentence for simplicity in GUI
        sats_in_sentence = min(4, total_sats)
        sat_data = []
        for i in range(sats_in_sentence):
            sat_id = i + 1
            elevation = random.randint(10, 90)
            azimuth = random.randint(0, 359)
            snr = random.randint(20, 50) if random.random() > 0.1 else ""
            sat_data.extend([f"{sat_id:02d}", f"{elevation:02d}", f"{azimuth:03d}", str(snr)])
        
        while len(sat_data) < 16:
            sat_data.append("")
        
        sentence = f"{talker}GSV,{sentences_needed},1,{total_sats:02d}," + ",".join(sat_data[:16])
        return self.format_nmea_sentence(sentence)

    def generate_vtg(self, talker='GP'):
        """Generate VTG sentence"""
        sentence = f"{talker}VTG,{self.course:.1f},T,{(self.course + random.uniform(-5, 5)) % 360:.1f},M,{self.speed_knots:.1f},N,{self.speed_knots * 1.852:.1f},K,A"
        return self.format_nmea_sentence(sentence)

    def generate_grs(self, talker='GP'):
        """Generate GRS sentence"""
        current_time = self.get_current_time()
        residuals = [f"{random.uniform(-2.0, 2.0):.1f}" for _ in range(12)]
        sentence = f"{talker}GRS,{current_time},1," + ",".join(residuals)
        return self.format_nmea_sentence(sentence)

    def generate_gst(self, talker='GP'):
        """Generate GST sentence"""
        current_time = self.get_current_time()
        sentence = f"{talker}GST,{current_time},{random.uniform(0.5, 2.0):.1f},{random.uniform(1.0, 3.0):.1f},{random.uniform(0.5, 2.0):.1f},{random.uniform(0, 180):.1f},{random.uniform(0.5, 2.0):.1f},{random.uniform(0.5, 2.0):.1f},{random.uniform(1.0, 4.0):.1f}"
        return self.format_nmea_sentence(sentence)

    def generate_zda(self, talker='GP'):
        """Generate ZDA sentence"""
        now = datetime.now(timezone.utc)
        sentence = f"{talker}ZDA,{now.hour:02d}{now.minute:02d}{now.second:02d}.00,{now.day:02d},{now.month:02d},{now.year},00,00"
        return self.format_nmea_sentence(sentence)

    def generate_dbs(self, talker='GP'):
        """Generate DBS sentence"""
        depth_feet = self.depth_meters * 3.28084
        depth_fathoms = self.depth_meters * 0.546807
        sentence = f"{talker}DBS,{depth_feet:.1f},f,{self.depth_meters:.1f},M,{depth_fathoms:.1f},F"
        return self.format_nmea_sentence(sentence)

    def generate_dbt(self, talker='GP'):
        """Generate DBT sentence"""
        depth_feet = self.depth_meters * 3.28084
        depth_fathoms = self.depth_meters * 0.546807
        sentence = f"{talker}DBT,{depth_feet:.1f},f,{self.depth_meters:.1f},M,{depth_fathoms:.1f},F"
        return self.format_nmea_sentence(sentence)

    def generate_dpt(self, talker='GP'):
        """Generate DPT sentence"""
        offset = random.uniform(-1.0, 1.0)
        sentence = f"{talker}DPT,{self.depth_meters:.1f},{offset:.1f},{self.depth_meters + 50:.1f}"
        return self.format_nmea_sentence(sentence)

    def generate_dru(self, talker='GP'):
        """Generate DRU sentence"""
        sentence = f"{talker}DRU,{random.uniform(0, 999.9):.1f},{random.uniform(0, 360):.1f}"
        return self.format_nmea_sentence(sentence)

    def generate_hdt(self, talker='GP'):
        """Generate HDT sentence"""
        sentence = f"{talker}HDT,{self.heading:.1f},T"
        return self.format_nmea_sentence(sentence)

    def generate_hev(self, talker='GP'):
        """Generate HEV sentence"""
        sentence = f"{talker}HEV,{self.heave:.2f},M"
        return self.format_nmea_sentence(sentence)

    def generate_hpr(self, talker='GP'):
        """Generate HPR sentence"""
        sentence = f"{talker}HPR,{self.heading:.2f},{self.pitch:.2f},{self.roll:.2f}"
        return self.format_nmea_sentence(sentence)

    def generate_pashr(self):
        """Generate PASHR sentence"""
        timestamp = self.get_current_time()
        sentence = f"PASHR,{timestamp},{self.heading:.2f},T,{self.roll:.2f},{self.pitch:.2f},{self.heave:.2f},3"
        return self.format_nmea_sentence(sentence)

    def generate_pdwa(self):
        """Generate PDWA sentence"""
        sentence = f"PDWA,{random.uniform(0.5, 3.0):.1f},{random.uniform(4, 12):.1f},{random.uniform(0, 360):.1f}"
        return self.format_nmea_sentence(sentence)

    def generate_psat_hpr(self):
        """Generate PSAT,HPR sentence"""
        sentence = f"PSAT,HPR,{self.heading:.2f},{self.pitch:.2f},{self.roll:.2f}"
        return self.format_nmea_sentence(sentence)

    def generate_psonnav(self):
        """Generate PSONNAV sentence"""
        timestamp = self.get_current_time()
        lat, lon, _ = self.add_position_variation()
        lat_str, lat_hem = self.format_coordinate(lat, True)
        lon_str, lon_hem = self.format_coordinate(lon, False)
        sentence = f"PSONNAV,{timestamp},{lat_str},{lat_hem},{lon_str},{lon_hem},{self.speed_knots:.1f},{self.heading:.1f}"
        return self.format_nmea_sentence(sentence)

    def generate_psxn(self):
        """Generate PSXN sentence"""
        subtype = random.choice(["20", "21", "22", "23"])
        lat, lon, _ = self.add_position_variation()
        sentence = f"PSXN,{subtype},{self.heading:.1f},{self.pitch:.2f},{self.roll:.2f},{lat:.6f},{lon:.6f}"
        return self.format_nmea_sentence(sentence)

    def generate_ptnl_avr(self):
        """Generate PTNL,AVR sentence"""
        timestamp = self.get_current_time()
        sentence = f"PTNL,AVR,{timestamp},{random.uniform(-5, 5):.2f},{random.uniform(-3, 3):.2f},{random.uniform(-10, 10):.2f},{random.uniform(-2, 2):.2f},{random.uniform(-1, 1):.2f},{random.uniform(-0.5, 0.5):.2f}"
        return self.format_nmea_sentence(sentence)

    def generate_rov(self, talker='GP'):
        """Generate ROV sentence"""
        depth = abs(self.depth_meters - 25)
        sentence = f"{talker}ROV,{depth:.1f},{random.randint(60, 100)},{random.randint(0, 100)},A"
        return self.format_nmea_sentence(sentence)

    def generate_sondep(self, talker='GP'):
        """Generate SONDEP sentence"""
        sentence = f"{talker}DEP,{self.depth_meters:.1f},M"
        return self.format_nmea_sentence(sentence)

    def generate_ths(self, talker='GP'):
        """Generate THS sentence"""
        sentence = f"{talker}THS,{self.heading:.1f},A"
        return self.format_nmea_sentence(sentence)

    def generate_vbw(self, talker='GP'):
        """Generate VBW sentence"""
        sentence = f"{talker}VBW,{self.speed_knots + random.uniform(-0.5, 0.5):.1f},{random.uniform(-2, 2):.1f},A,{self.speed_knots:.1f},{random.uniform(-1, 1):.1f},A"
        return self.format_nmea_sentence(sentence)

    def generate_vdr(self, talker='GP'):
        """Generate VDR sentence"""
        set_true = random.uniform(0, 360)
        sentence = f"{talker}VDR,{set_true:.1f},T,{(set_true + random.uniform(-5, 5)) % 360:.1f},M,{random.uniform(0, 3):.1f},N,{random.uniform(0, 3) * 1.852:.1f},K"
        return self.format_nmea_sentence(sentence)

    def generate_vhw(self, talker='GP'):
        """Generate VHW sentence"""
        heading_mag = (self.heading + random.uniform(-5, 5)) % 360
        speed_water = self.speed_knots + random.uniform(-0.5, 0.5)
        sentence = f"{talker}VHW,{self.heading:.1f},T,{heading_mag:.1f},M,{speed_water:.1f},N,{speed_water * 1.852:.1f},K"
        return self.format_nmea_sentence(sentence)

    def generate_wimda(self, talker='GP'):
        """Generate WIMDA sentence"""
        pressure_inhg = self.barometric_pressure * 0.02953
        air_temp_f = self.air_temp * 9/5 + 32
        sentence = f"{talker}MDA,{pressure_inhg:.2f},I,{self.barometric_pressure:.1f},B,{self.air_temp:.1f},C,{air_temp_f:.1f},F,{self.humidity:.1f},,{random.uniform(5, 15):.1f},,{self.air_temp - 5:.1f},C,{(self.air_temp - 5) * 9/5 + 32:.1f},F,{self.wind_direction:.1f},T,{(self.wind_direction + random.uniform(-5, 5)) % 360:.1f},M,{self.wind_speed:.1f},N,{self.wind_speed * 0.514444:.1f},M"
        return self.format_nmea_sentence(sentence)

    def generate_wimwd(self, talker='GP'):
        """Generate WIMWD sentence"""
        wind_dir_mag = (self.wind_direction + random.uniform(-5, 5)) % 360
        sentence = f"{talker}MWD,{self.wind_direction:.1f},T,{wind_dir_mag:.1f},M,{self.wind_speed:.1f},N,{self.wind_speed * 0.514444:.1f},M"
        return self.format_nmea_sentence(sentence)

    def generate_wimwv(self, talker='GP'):
        """Generate WIMWV sentence"""
        rel_angle = (self.wind_direction - self.heading) % 360
        sentence = f"{talker}MWV,{rel_angle:.1f},R,{self.wind_speed + random.uniform(-1, 1):.1f},N,A"
        return self.format_nmea_sentence(sentence)

    def generate_aivdm(self):
        """Generate AIVDM sentence"""
        payload = "13HOI:0P0000VOHLCnHQKwvL05Ip"  # Example Type 1 position report
        sentence = f"AIVDM,1,1,,A,{payload},0"
        return self.format_ais_sentence(sentence)

    def get_message_generator(self, msg_type):
        """Get the generator function for a message type"""
        generators = {
            'AIVDM': self.generate_aivdm,
            'DBS': self.generate_dbs,
            'DBT': self.generate_dbt,
            'DPT': self.generate_dpt,
            'DRU': self.generate_dru,
            'GGA': self.generate_gga,
            'GLL': self.generate_gll,
            'GRS': self.generate_grs,
            'GSA': self.generate_gsa,
            'GST': self.generate_gst,
            'GSV': self.generate_gsv,
            'HDT': self.generate_hdt,
            'HEV': self.generate_hev,
            'HPR': self.generate_hpr,
            'PASHR': self.generate_pashr,
            'PDWA': self.generate_pdwa,
            'PSAT_HPR': self.generate_psat_hpr,
            'PSONNAV': self.generate_psonnav,
            'PSXN': self.generate_psxn,
            'PTNL_AVR': self.generate_ptnl_avr,
            'RMC': self.generate_rmc,
            'ROV': self.generate_rov,
            'SONDEP': self.generate_sondep,
            'THS': self.generate_ths,
            'VBW': self.generate_vbw,
            'VDR': self.generate_vdr,
            'VHW': self.generate_vhw,
            'VTG': self.generate_vtg,
            'WIMDA': self.generate_wimda,
            'WIMWD': self.generate_wimwd,
            'WIMWV': self.generate_wimwv,
            'ZDA': self.generate_zda,
        }
        return generators.get(msg_type)


class NMEASimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NMEA 0183 Simulator")
        self.root.geometry("900x700")
        
        self.simulator = NMEASimulatorCore()
        self.serial_port = None
        self.is_running = False
        self.simulation_thread = None
        self.message_queue = queue.Queue()
        
        # Message types and their display names
        self.message_types = [
            ('AIVDM', 'AIVDM - AIS VHF Data-Link Message'),
            ('DBS', 'DBS - Depth Below Surface'),
            ('DBT', 'DBT - Depth Below Transducer'),
            ('DPT', 'DPT - Depth of Water'),
            ('DRU', 'DRU - Dead Reckoning Unit'),
            ('GGA', 'GGA - GPS Fix Data'),
            ('GLL', 'GLL - Geographic Latitude/Longitude'),
            ('GRS', 'GRS - GPS Range Residuals'),
            ('GSA', 'GSA - GPS DOP and Active Satellites'),
            ('GST', 'GST - GPS Pseudorange Noise Statistics'),
            ('GSV', 'GSV - GPS Satellites in View'),
            ('HDT', 'HDT - Heading True'),
            ('HEV', 'HEV - Heave'),
            ('HPR', 'HPR - Heading, Pitch, Roll'),
            ('PASHR', 'PASHR - Proprietary Attitude and Heading Reference'),
            ('PDWA', 'PDWA - Proprietary Dynamic Water Analysis'),
            ('PSAT_HPR', 'PSAT,HPR - Proprietary Attitude Data'),
            ('PSONNAV', 'PSONNAV - Proprietary Navigation'),
            ('PSXN', 'PSXN - Proprietary Extended Navigation'),
            ('PTNL_AVR', 'PTNL,AVR - Attitude and Velocity Reference'),
            ('RMC', 'RMC - Recommended Minimum Course'),
            ('ROV', 'ROV - Remotely Operated Vehicle'),
            ('SONDEP', 'SONDEP - Sonar Depth'),
            ('THS', 'THS - True Heading and Status'),
            ('VBW', 'VBW - Dual Ground/Water Speed'),
            ('VDR', 'VDR - Set and Drift'),
            ('VHW', 'VHW - Water Speed and Heading'),
            ('VTG', 'VTG - Track Made Good and Ground Speed'),
            ('WIMDA', 'WIMDA - Meteorological Composite'),
            ('WIMWD', 'WIMWD - Wind Direction & Speed'),
            ('WIMWV', 'WIMWV - Wind Speed and Angle'),
            ('ZDA', 'ZDA - UTC Time and Date'),
        ]
        
        self.setup_ui()
        self.update_serial_ports()
        self.check_message_queue()

    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Serial port selection
        ttk.Label(main_frame, text="Serial Port:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(main_frame, textvariable=self.port_var, state="readonly", width=50)
        self.port_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Refresh ports button
        ttk.Button(main_frame, text="Refresh", command=self.update_serial_ports).grid(row=0, column=2, padx=(10, 0), pady=(0, 10))
        
        # Baud rate selection
        ttk.Label(main_frame, text="Baud Rate:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.baud_var = tk.StringVar(value="4800")
        baud_combo = ttk.Combobox(main_frame, textvariable=self.baud_var, values=["4800", "9600", "19200", "38400", "57600", "115200"], state="readonly", width=10)
        baud_combo.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # Message selection frame
        msg_frame = ttk.LabelFrame(main_frame, text="NMEA Message Types", padding="10")
        msg_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        msg_frame.columnconfigure(1, weight=1)
        
        # Create scrollable frame for checkboxes
        canvas = tk.Canvas(msg_frame, height=200)
        scrollbar = ttk.Scrollbar(msg_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        
        # Message type checkboxes
        self.message_vars = {}
        for i, (msg_type, description) in enumerate(self.message_types):
            var = tk.BooleanVar()
            self.message_vars[msg_type] = var
            
            cb = ttk.Checkbutton(scrollable_frame, text=description, variable=var)
            cb.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
        
        # All messages checkbox
        self.all_messages_var = tk.BooleanVar()
        all_cb = ttk.Checkbutton(msg_frame, text="Select All Messages", variable=self.all_messages_var, command=self.toggle_all_messages)
        all_cb.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Interval setting
        interval_frame = ttk.Frame(main_frame)
        interval_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(interval_frame, text="Interval per message (seconds):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="1.0")
        interval_spin = ttk.Spinbox(interval_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.interval_var, width=10)
        interval_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Simulation", command=self.stop_simulation, state="disabled")
        self.stop_button.pack(side=tk.LEFT)
        
        # Clear log button
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(10, 0))
        
        # Output log
        log_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="5")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled")
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def update_serial_ports(self):
        """Update the serial port dropdown"""
        ports = serial.tools.list_ports.comports()
        port_list = [f"{port.device} - {port.description}" for port in ports]
        
        self.port_combo['values'] = port_list
        if port_list and not self.port_var.get():
            self.port_combo.current(0)

    def toggle_all_messages(self):
        """Toggle all message checkboxes"""
        state = self.all_messages_var.get()
        for var in self.message_vars.values():
            var.set(state)

    def get_selected_messages(self):
        """Get list of selected message types"""
        return [msg_type for msg_type, var in self.message_vars.items() if var.get()]

    def log_message(self, message):
        """Add message to log"""
        self.message_queue.put(message)

    def check_message_queue(self):
        """Check for new messages to log"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.log_text.config(state="normal")
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state="disabled")
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_message_queue)

    def clear_log(self):
        """Clear the output log"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def connect_serial(self):
        """Connect to selected serial port"""
        if not self.port_var.get():
            messagebox.showerror("Error", "Please select a serial port")
            return False
        
        port_device = self.port_var.get().split(" - ")[0]
        baud_rate = int(self.baud_var.get())
        
        try:
            self.serial_port = serial.Serial(
                port=port_device,
                baudrate=baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.log_message(f"Connected to {port_device} at {baud_rate} baud")
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {port_device}: {e}")
            return False

    def disconnect_serial(self):
        """Disconnect from serial port"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.log_message("Serial port disconnected")

    def send_message(self, message):
        """Send NMEA message over serial"""
        if self.serial_port and self.serial_port.is_open:
            try:
                # NMEA 0183 uses ASCII encoding
                self.serial_port.write(message.encode('ascii'))
                self.log_message(f"{message.strip()}")
                return True
            except Exception as e:
                self.log_message(f"Error sending message: {e}")
                return False
        return False

    def simulation_worker(self):
        """Worker thread for simulation"""
        selected_messages = self.get_selected_messages()
        
        if not selected_messages:
            self.log_message("No messages selected!")
            return
        
        initial_interval = float(self.interval_var.get())
        self.log_message(f"Starting simulation with {len(selected_messages)} message types")
        self.log_message(f"Initial interval: {initial_interval} seconds per message")
        
        message_count = 0
        message_index = 0
        last_logged_interval = initial_interval
        
        while self.is_running:
            try:
                # Read current interval (allows real-time changes)
                current_interval = float(self.interval_var.get())
                
                # Log interval changes
                if current_interval != last_logged_interval:
                    self.log_message(f"Interval changed to: {current_interval} seconds per message")
                    last_logged_interval = current_interval
                
                # Update dynamics periodically (every 10 messages or so)
                if message_count % 10 == 0:
                    self.simulator.simulate_dynamics()
                
                # Get current message type (cycle through selected messages)
                msg_type = selected_messages[message_index]
                message_index = (message_index + 1) % len(selected_messages)
                
                # Generate and send single message
                generator = self.simulator.get_message_generator(msg_type)
                if generator:
                    try:
                        message = generator()
                        self.send_message(message)
                        message_count += 1
                    except Exception as e:
                        self.log_message(f"Error generating {msg_type}: {e}")
                
                # Wait for the specified interval before next message
                if self.is_running:
                    time.sleep(current_interval)
                    
            except Exception as e:
                self.log_message(f"Simulation error: {e}")
                break
        
        self.log_message(f"Simulation stopped. Sent {message_count} individual messages")

    def start_simulation(self):
        """Start the NMEA simulation"""
        if self.is_running:
            return
        
        if not self.connect_serial():
            return
        
        selected_messages = self.get_selected_messages()
        if not selected_messages:
            messagebox.showwarning("Warning", "Please select at least one message type")
            self.disconnect_serial()
            return
        
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.simulation_worker, daemon=True)
        self.simulation_thread.start()

    def stop_simulation(self):
        """Stop the NMEA simulation"""
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # Wait for thread to finish
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=2)
        
        self.disconnect_serial()

    def on_closing(self):
        """Handle application closing"""
        if self.is_running:
            self.stop_simulation()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = NMEASimulatorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
