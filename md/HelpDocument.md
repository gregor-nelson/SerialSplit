# Serial Port Splitter
## Professional User Guide

**Version 1.0**  
**Professional Serial Port Management Solution**

---

### Document Control

**Risk Level:** GREEN  
**Document Reference:** SPS-USR-001  

| Rev No: | Date: | Description: | Author: | Reviewer: |
|---------|-------|-------------|---------|-----------|
| 1.0 | Current | Initial Release | Development Team | Technical Review |

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation and Setup](#installation-and-setup)
4. [Quick Start Guide](#quick-start-guide)
5. [Virtual Port Management](#virtual-port-management)
6. [Routing Configuration](#routing-configuration)
7. [Advanced Configuration](#advanced-configuration)
8. [Command Line Operations](#command-line-operations)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)
11. [Technical Support](#technical-support)

---

## 1. Introduction

### Welcome to Serial Port Splitter

This professional-grade application provides comprehensive serial port management capabilities for Windows environments. The Serial Port Splitter enables users to create virtual serial port pairs and route data between multiple ports with flexible configuration options, offering functionality comparable to commercial solutions whilst maintaining ease of use.

### Key Features

- **Virtual Port Management:** Automated setup of virtual port pairs with optimised settings
- **Multi-Port Routing:** Route data from one incoming port to multiple outgoing ports
- **Real-time Monitoring:** Live port status and data flow statistics
- **Modern Interface:** Professional interface with responsive design
- **Smart Detection:** Automatic classification of physical, virtual, and MOXA ports
- **Flexible Configuration:** Different baud rates and flow control options for each connection

### Use Cases

The Serial Port Splitter is designed for various professional applications:

- **Development and Testing:** Test serial applications with multiple virtual ports
- **Industrial Applications:** Route data between different baud rate devices
- **Network Integration:** Interface with MOXA device servers
- **System Monitoring:** Monitor and log serial communications
- **Application Integration:** Bridge applications requiring shared serial access

---

## 2. System Requirements

### Minimum Requirements

- **Operating System:** Windows 10 or later (for full functionality)
- **Privileges:** Administrator privileges required for driver installation
- **Dependencies:** COM0COM virtual serial port driver
- **Runtime:** Python 3.8+ with PyQt6, PyQt6-SVG, pyserial

### ⚠️ Critical Installation Requirements

**Administrator Privileges Required**

COM0COM driver installation requires Windows Administrator privileges and UAC elevation. Installation is **NOT** automatic and must be completed manually.

### Required Installation Steps

1. **Close all applications** that may use serial ports
2. **Right-click the application** and select "Run as Administrator"
3. **Accept UAC prompt** when Windows requests elevation
4. **Allow driver installation** if Windows Defender or antivirus software displays warnings
5. **Restart the system** if prompted to complete driver registration

### Enterprise Security Considerations

**Corporate/Enterprise Networks:** Group Policy or security software may prevent COM0COM installation:

- **Digital signature warnings:** COM0COM uses test-signed drivers
- **Driver installation restrictions:** IT policies may block unsigned drivers
- **Antivirus interference:** Security software may quarantine driver files

**Resolution:** Contact your IT security team for driver approval before deployment.

---

## 3. Installation and Setup

### Initial Configuration

Follow these steps to ensure proper configuration for initial use:

### Prerequisites Verification

Confirm the following requirements are met:
- Windows 10 or later operating system
- Administrator privileges available
- COM0COM driver installed
- Serial device connected (if applicable)

### Driver Installation Process

1. **Download COM0COM driver** from the official source
2. **Extract the driver files** to a temporary directory
3. **Run the installer as Administrator**
4. **Follow the installation prompts**
5. **Restart when prompted**

### Application Setup

1. **Launch Serial Port Splitter** as Administrator
2. **Click "Refresh Ports"** - available COM ports should be visible
3. **Create a test virtual pair** to verify installation
4. **Confirm new ports appear** in the port lists

---

## 4. Quick Start Guide

### Getting Started in Minutes

This guide will enable operation in just a few minutes. Follow these straightforward steps to begin splitting serial data.

### Step 1: Create Virtual Port Pairs

Virtual port pairs form the foundation of serial port splitting:

1. **Click "Create New Pair"** in the Virtual Ports section
2. **Note the assigned port numbers** (e.g., COM3 ↔ COM4)
3. **Record these port numbers** - they will be required for applications
4. **Important:** Applications should connect to the "other side" of the pair from the data source

### Step 2: Select Data Source

Choose your serial data source:

- **Physical Port:** A real COM port connected to hardware
- **MOXA Device:** Network-attached serial device
- **Virtual Port:** One side of a virtual port pair

### Step 3: Add Output Destinations

Configure ports to receive data:

1. **Click "Add Output Port"** for each destination
2. **Select the appropriate COM port** from the dropdown
3. **Set the baud rate** to match application requirements

### Step 4: Configure and Start Operations

1. **Choose your routing mode** (usually "One-Way" for basic splitting)
2. **Verify all baud rates are correct**
3. **Click "Start Routing"** to begin data flow

**Professional Tip:** Use the "Set All" button to quickly apply the same baud rate to all output ports.

---

## 5. Virtual Port Management

### Understanding Port Pairs

Virtual port pairs consist of two COM ports connected by a virtual null-modem cable. Data written to one port appears instantly on the other port.

**Example:** COM3 ⇄ COM4 means data sent to COM3 appears on COM4, and vice versa.

### Creating Port Pairs

1. **Click "Create New Pair"** in the Virtual Ports section
2. **System automatically assigns** the next available port numbers
3. **Port names follow the pattern:** CNCA0/CNCB0, CNCA1/CNCB1, etc.

### Managing Existing Pairs

- **View Details:** Double-click any pair to access advanced settings
- **Configure Features:** Right-click to access emulation options
- **Remove Pairs:** Select and click "Remove Selected Pair"

### Best Practices for Port Management

- **Create only required pairs** - each pair consumes system resources
- **Document port assignments** for applications
- **Remove unused pairs** to maintain a manageable list
- **Restart applications** after creating new pairs

### ⚠️ CRITICAL: Port Number Stability

**Port numbers CAN change after:**
- System restarts
- Hardware configuration changes
- Windows updates
- Driver reinstallation

**IMPACT:** Automated systems and applications must be reconfigured when port numbers change. Always verify port assignments before critical operations.

---

## 6. Routing Configuration

### Available Routing Modes

#### One-Way Splitting (Default)

**Data Flow:** Incoming Port → All Output Ports  
**Use Case:** Broadcasting data from one source to multiple receivers  
**Example:** GPS device sending location data to multiple navigation applications

#### Two-Way Communication

**Data Flow:** Bidirectional between incoming and output ports  
**Use Case:** Applications need to send commands back to the device  
**Example:** Terminal program communicating with a modem

#### Full Network Mode

**Data Flow:** All ports can communicate with all other ports  
**Use Case:** Creating a virtual serial network  
**Example:** Multiple devices/applications all intercommunicating

### Mode Selection Guidelines

| Scenario | Recommended Mode |
|----------|------------------|
| Simple data logging/monitoring | One-Way |
| Device control with feedback | Two-Way |
| Multi-device simulation | Full Network |

**Performance Note:** Full Network mode uses more CPU resources. Use only when necessary.

### Flow Control Configuration

#### Understanding Flow Control

Flow control prevents data loss by coordinating when devices can send data. It functions like traffic lights for serial communication.

#### Hardware Flow Control (RTS/CTS)

- **RTS (Request To Send):** Sender signals intention to transmit
- **CTS (Clear To Send):** Receiver signals readiness to receive

#### When to Enable Flow Control

- High-speed data transfers (>38,400 baud)
- Large data volumes
- When devices explicitly support it
- Experiencing data loss or corruption

#### When NOT to Use Flow Control

- Simple, low-speed connections
- Devices that don't support flow control
- 3-wire connections (TX, RX, GND only)

### Baud Rate Configuration

#### Understanding Baud Rates

Baud rate represents the speed of serial communication, measured in bits per second (bps).

#### Common Baud Rates and Applications

| Baud Rate | Typical Use | Notes |
|-----------|-------------|-------|
| 9,600 | GPS, Arduino | Most compatible, slower speed |
| 19,200 | Industrial devices | Good balance of speed/reliability |
| 38,400 | Modems | Medium speed applications |
| 57,600 | Embedded systems | Higher speed requirements |
| 115,200 | Modern devices | Fast, common default |

#### Critical Configuration Rules

**The baud rate MUST match the source device exactly.**  
Mismatched baud rates result in corrupted data or no communication.

#### Configuration Tips

- **Check device documentation** for the correct baud rate
- **Start with 9,600 baud** if uncertain - most compatible rate
- **Use "Set All" function** to quickly match all output ports
- **Higher rates require** better cable quality

---

## 7. Advanced Configuration

### ⚠️ Expert Users Only

These settings can affect system stability. Modify only when the implications are fully understood.

### COM0COM Emulation Features

#### Baud Rate Emulation (EmuBR)

- **Function:** Simulates physical port timing
- **Default (Disabled):** Data transfer occurs instantaneously
- **Enabled:** Data transfer matches specified baud rate
- **Use Case:** Testing timing-sensitive applications

#### Buffer Overrun Emulation

- **Function:** Simulates finite buffer capacity
- **Default (Disabled):** Extensive buffering prevents data loss
- **Enabled:** Port drops data if not read quickly enough
- **Use Case:** Testing application error handling

#### Exclusive Access Mode

- **Function:** Controls system-level port visibility
- **Default (Disabled):** Ports persistently visible in Device Manager
- **Enabled:** Port hidden until paired port is opened
- **Use Case:** Prevent accidental connections

#### Plug-In Mode

- **Function:** Dynamic port creation/removal
- **Default (Disabled):** Port permanently registered
- **Enabled:** Port created only when paired port is opened
- **Use Case:** Advanced dynamic port management

### Port Configuration Display

Port pairs are displayed using the following format:

**COM131 ⇄ COM132 [CNCA31 ⇄ CNCB31] [Features: Baud Rate Emulation]**

- **COM131 ⇄ COM132:** System-level port names visible to applications
- **[CNCA31 ⇄ CNCB31]:** Internal driver names
- **[Features: ...]:** Currently enabled emulation features

### Setup Recommendations

#### Standard Configuration (General Data Transfer)

For maximum performance and reliability, leave all emulation settings disabled.

#### Development and Testing Configuration

- **Enable Baud Rate Emulation** to validate application behaviour with realistic speeds
- **Enable Buffer Overrun Emulation** to test error handling logic

---

## 8. Command Line Operations

### Automation Capabilities

The Serial Port Splitter can be controlled via command line for automation and scripting.

### Basic Commands

#### List Available Ports
```cmd
hub4com.exe --list
```

#### Simple One-Way Split
```cmd
hub4com.exe COM1 COM3 COM4
```

#### Two-Way Communication
```cmd
hub4com.exe --bi-route=0:1 COM1 COM3
```

### COM0COM Commands

#### List Virtual Pairs
```cmd
setupc.exe list
```

#### Create New Pair
```cmd
setupc.exe install PortName=COM10 PortName=COM11
```

#### Remove Pair
```cmd
setupc.exe remove CNCA0
```

### Automation Examples

#### Batch File for Startup
```batch
@echo off
echo Starting Serial Port Splitter...
start hub4com.exe --load=config.txt
echo Routing started successfully!
```

#### PowerShell Script
```powershell
# Verify port exists before starting
$ports = [System.IO.Ports.SerialPort]::getportnames()
if ($ports -contains "COM3") {
    Start-Process "hub4com.exe" -ArgumentList "COM3 COM10 COM11"
}
```

---

## 9. Troubleshooting

### Common Issues and Solutions

#### "Access Denied" Error

**Cause:** Port already in use by another application  
**Resolution:**
1. Close all applications using the port
2. Check Task Manager for hidden processes
3. Restart the application

#### "Port Not Found" Error

**Cause:** Port doesn't exist or driver issue  
**Resolution:**
1. Click "Refresh Ports" button
2. Check Device Manager for the port
3. Reinstall COM0COM driver if virtual ports are missing

#### No Data Received

**Cause:** Multiple possible causes  
**Resolution:**
1. Verify source device is transmitting data
2. Check baud rate matches exactly
3. Test with a terminal program first
4. Verify cable connections (for physical ports)

#### Corrupted Data/Garbage Characters

**Cause:** Baud rate mismatch  
**Resolution:**
1. Double-check source device baud rate
2. Try common rates: 9,600, 19,200, 115,200
3. Verify data bits, parity, stop bits settings

#### Application Cannot Open Port

**Cause:** Port permissions or visibility  
**Resolution:**
1. Run application as Administrator
2. Disable Exclusive Mode in port settings
3. Restart application after creating ports

### Error Message Reference

#### Critical Errors

**"Failed to start hub4com.exe"**
- **Meaning:** Routing engine couldn't start
- **Action:** Ensure hub4com.exe is in the application folder

**"COM0COM driver not installed"**
- **Meaning:** Virtual port driver is missing
- **Action:** Restart application as Administrator for auto-installation

#### Warning Messages

**"Port already in use"**
- **Meaning:** Another application is using this port
- **Action:** Choose a different port or close the conflicting application

**"Baud rate mismatch detected"**
- **Meaning:** Output ports have different baud rates
- **Action:** Use "Set All" to synchronise rates

### Critical Process Failures

#### "HUB4COM process terminated unexpectedly"

**Immediate Action Required:**
1. **Stop all data collection** - routing has failed
2. **Check Windows Event Viewer** for crash details
3. **Verify all output ports are accessible**
4. **Restart routing service** from main application
5. **Monitor for repeated failures** - may indicate hardware issues

---

## 10. Best Practices

### Professional Implementation Guidelines

#### System Configuration

- **Test thoroughly** before deploying in production environments
- **Document all port assignments** and configurations
- **Create backup configurations** for critical setups
- **Monitor system resources** during heavy data flow

#### Port Management

- **Use descriptive names** for virtual pairs when possible
- **Implement consistent naming conventions**
- **Regular maintenance** - remove unused ports
- **Monitor port number stability** across system restarts

#### Performance Optimisation

- **Minimise active ports** to reduce system overhead
- **Use appropriate routing modes** for specific requirements
- **Configure flow control** only when necessary
- **Match baud rates precisely** to source devices

#### Security Considerations

- **Run with minimum required privileges** in production
- **Regularly update drivers** and dependencies
- **Monitor for unauthorised access** to virtual ports
- **Implement access controls** for critical applications

### Operational Procedures

#### Pre-Deployment Testing

1. **Verify all connections** in a test environment
2. **Test failover scenarios** and error conditions
3. **Validate data integrity** across all routing paths
4. **Performance testing** under expected loads

#### Deployment Checklist

- [ ] COM0COM driver installed and verified
- [ ] Virtual port pairs created and tested
- [ ] Routing configuration validated
- [ ] Applications configured for correct ports
- [ ] Documentation updated with port assignments
- [ ] Backup procedures established

#### Ongoing Maintenance

- **Regular monitoring** of system performance
- **Periodic testing** of backup configurations
- **Documentation updates** when changes are made
- **Review and update** security settings

---

## 11. Technical Support

### Getting Assistance

If you encounter issues not covered in this guide:

1. **Review the troubleshooting section** thoroughly
2. **Check the application log files** for detailed error information
3. **Note the exact error message** and circumstances
4. **Document your system configuration** and setup

### System Information to Include

When seeking support, please provide:

- **Operating System version** and build number
- **COM0COM driver version**
- **Application version**
- **Hardware configuration** (if using physical ports)
- **Exact error messages** or symptoms
- **Steps to reproduce** the issue

### Additional Resources

- **COM0COM Documentation:** Official driver documentation
- **Windows Serial Port Reference:** Microsoft technical documentation
- **Community Forums:** User community discussions and solutions

---

## Appendix A: Port Type Reference

### Port Classification Guide

#### Physical Ports
- **Description:** Hardware COM ports (built-in or USB adapters)
- **Identification:** Listed in Device Manager under "Ports (COM & LPT)"
- **Configuration:** Must match connected device specifications exactly

#### Virtual Ports
- **Description:** Software-created ports for inter-application communication
- **Identification:** Created by COM0COM driver
- **Configuration:** Baud rate settings depend on emulation mode

#### MOXA Network Devices
- **Description:** Network-attached serial device servers
- **Identification:** Accessed via network protocols
- **Configuration:** Requires network connectivity and device configuration

---

## Appendix B: Command Reference

### Complete Command Syntax

#### HUB4COM Commands
```cmd
hub4com [options] port1 port2 [port3 ...]

Options:
  --list                List available ports
  --bi-route=n:m       Enable bidirectional routing between ports n and m
  --load=filename      Load configuration from file
  --help               Display help information
```

#### SETUPC Commands
```cmd
setupc [command] [parameters]

Commands:
  list                 List all virtual port pairs
  install             Create new port pair
  remove              Remove existing port pair
  change              Modify port pair settings
```

---

*This document contains technical information for professional use. All procedures should be tested in a development environment before production deployment.*

**Document Control**  
Serial Port Splitter Professional User Guide  
Version 1.0 - Initial Release  
© 2024 Professional Serial Port Solutions