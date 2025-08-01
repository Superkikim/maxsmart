# MaxSmart Python Module

[![PyPI version](https://img.shields.io/badge/PyPI-2.0.4-blue.svg)](https://pypi.org/project/maxsmart/)
[![Python versions](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://pypi.org/project/maxsmart/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Version:** 2.0.4

A comprehensive Python library for controlling Revogi-based Max Hauri MaxSmart PowerStrips and Smart Plugs over local network. Features intelligent auto-detection, adaptive polling, real-time monitoring, and robust async architecture.

## ☕ Support My Work

If this plugin helps you, consider supporting its development:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/nexusplugins)

## 🎯 What's New in v2.0

- **Full async/await architecture** - Modern Python async throughout
- **Intelligent firmware detection** - Auto-detects and adapts to different firmware versions
- **Advanced device identification** - CPU ID, MAC address, and serial-based device tracking
- **Adaptive polling system** - Mimics official app behavior (5s normal, 2s burst)
- **Real-time monitoring** - Live consumption and state change detection
- **Enhanced error handling** - Robust retry logic with localized messages
- **Session management** - Connection pooling and automatic cleanup
- **Advanced statistics** - Hourly, daily, monthly data with visualization support

## 🔧 Supported Hardware

### Firmware Compatibility & Testing Status

| Brand | Device Type | Firmware Versions | Support Level | Test Status |
|-------|-------------|-------------------|---------------|-------------|
| **Max Hauri** | Power Station (6 ports) | **v1.10, v1.30, v2.11** | [![Full](https://img.shields.io/badge/Support-Full-brightgreen.svg)]() | [![Tested](https://img.shields.io/badge/Tests-Validated-brightgreen.svg)]() |
| **Max Hauri** | Smart Plug (1 port) | **v1.10, v1.30, v2.11** | [![Full](https://img.shields.io/badge/Support-Full-brightgreen.svg)]() | [![Tested](https://img.shields.io/badge/Tests-Validated-brightgreen.svg)]() |
| **Revogi** | Power Strip (6 ports) | **v3.36, v3.49** | [![Full](https://img.shields.io/badge/Support-Full-brightgreen.svg)]() | [![Tested](https://img.shields.io/badge/Tests-Validated-brightgreen.svg)]() |
| **CoCoSo** | Power Strip (6 ports) | **v1.06** | [![Full](https://img.shields.io/badge/Support-Full-brightgreen.svg)]() | [![Tested](https://img.shields.io/badge/Tests-Validated-brightgreen.svg)]() |
| **Extel** | Soky Power Strip | Various | [![Compatible](https://img.shields.io/badge/Support-Compatible-yellow.svg)]() | [![Need Testing](https://img.shields.io/badge/Tests-Need%20Volunteers-orange.svg)]() |
| **MCL** | DOM-PPS06I | Various | [![Compatible](https://img.shields.io/badge/Support-Compatible-yellow.svg)]() | [![Need Testing](https://img.shields.io/badge/Tests-Need%20Volunteers-orange.svg)]() |

### Device Models
- Max Hauri MaxSmart Power Station (6 ports)
- Max Hauri MaxSmart Smart Plug (1 port)  
- Revogi Smart Power Strip (SOW323)
- CoCoSo Smart Power Strip (SOW323)
- Extel Soky Power Strip
- MCL DOM-PPS06I

**🤝 Help expand compatibility!** If you have Revogi-based devices with different firmware versions, please [test them and let us know](https://github.com/superkikim/maxsmart/issues/new) - we'd love to add them to the supported list!

### Data Format Detection
The module automatically detects your device's data format:
- **String floats** ("5.20") → Direct watt values
- **Integer milliwatts** (5200) → Converted to watts (×0.001)
- **Integer watts** (5) → Direct watt values

## 📦 Installation

### From PyPI
```bash
pip install maxsmart
```

### From Source
```bash
git clone https://github.com/superkikim/maxsmart.git
cd maxsmart
pip install .
```

### Dependencies
- Python 3.7+
- aiohttp (async HTTP client)
- getmac (MAC address discovery)
- matplotlib (for example scripts)

## 🚀 Quick Start

```python
import asyncio
from maxsmart import MaxSmartDiscovery, MaxSmartDevice

async def main():
    # Discover devices on network
    devices = await MaxSmartDiscovery.discover_maxsmart()
    if not devices:
        print("No devices found")
        return
        
    # Connect to first device
    device = MaxSmartDevice(devices[0]['ip'])
    await device.initialize_device()
    
    print(f"Connected to {device.name} (FW: {device.version})")
    print(f"Data format: {device._watt_format}")
    
    # Control ports
    await device.turn_on(1)                    # Turn on port 1
    state = await device.check_state(1)       # Check port 1 state
    power = await device.get_power_data(1)    # Get power consumption
    
    print(f"Port 1: {'ON' if state else 'OFF'}, {power['watt']}W")
    
    # Cleanup
    await device.close()

asyncio.run(main())
```

## 🔍 Device Discovery

### Network Scanning
```python
from maxsmart import MaxSmartDiscovery

# Discover all devices on local network
discovery = MaxSmartDiscovery()
devices = await discovery.discover_maxsmart()

for device in devices:
    print(f"Name: {device['name']}")
    print(f"IP: {device['ip']}")
    print(f"Serial: {device['sn']}")
    print(f"Firmware: {device['ver']}")
    print(f"Ports: {device['pname']}")
```

### Enhanced Discovery with Hardware Identification
```python
# Enhanced discovery with CPU ID, MAC address detection
devices = await MaxSmartDiscovery.discover_maxsmart(enhance_with_hardware_ids=True)

for device in devices:
    print(f"Name: {device['name']} ({device['ip']})")
    print(f"CPU ID: {device.get('cpuid', 'Not available')}")
    print(f"MAC Address: {device.get('mac_address', 'Not available')}")
    print(f"Unique ID: {device.get('unique_id', 'Not available')}")
    print(f"ID Method: {device.get('identification_method', 'fallback')}")
```

### Targeted Discovery
```python
# Query specific IP address
devices = await MaxSmartDiscovery.discover_maxsmart(ip="192.168.1.100")

# With custom timeout and locale
devices = await MaxSmartDiscovery.discover_maxsmart(
    ip="192.168.1.100",
    user_locale="fr",
    timeout=5.0
)
```

## 🆔 Advanced Device Identification

### Hardware Identifiers
```python
device = MaxSmartDevice('192.168.1.100')
await device.initialize_device()

# Get hardware identifiers
hw_ids = await device.get_device_identifiers()
print(f"CPU ID: {hw_ids.get('cpuid', 'Not available')}")
print(f"Device MAC: {hw_ids.get('pclmac', 'Not available')}")
print(f"Device Access Key: {hw_ids.get('pcldak', 'Not available')}")

# Get MAC address via ARP
mac_address = await device.get_mac_address_via_arp()
print(f"ARP MAC: {mac_address}")

# Get best unique identifier
unique_id = await device.get_unique_identifier()
print(f"Best unique ID: {unique_id}")

# Get all available identifiers
all_ids = await device.get_all_identifiers()
for id_type, data in all_ids.items():
    if data.get('available'):
        print(f"{id_type}: {data['value']} (from {data['source']})")
```

### Identification Priority
The module uses this priority for device identification:
1. **CPU ID** (most reliable) - Hardware-based unique identifier
2. **MAC Address** (very reliable) - Network hardware identifier  
3. **UDP Serial** (good) - Device serial from discovery
4. **IP Address** (fallback) - Network address

## 🎛️ Device Control

### Basic Port Operations
```python
device = MaxSmartDevice('192.168.1.100')
await device.initialize_device()

# Individual ports (1-6)
await device.turn_on(1)      # Turn on port 1
await device.turn_off(3)     # Turn off port 3

# Master control (port 0 = all ports)
await device.turn_on(0)      # Turn on all ports
await device.turn_off(0)     # Turn off all ports

# State checking
port1_state = await device.check_state(1)    # Single port: 0 or 1
all_states = await device.check_state()      # All ports: [0,1,0,1,1,0]
```

### Device Information
```python
# Device properties (available after initialization)
print(f"Device name: {device.name}")
print(f"IP address: {device.ip}")
print(f"Serial number: {device.sn}")
print(f"Firmware version: {device.version}")
print(f"Strip name: {device.strip_name}")
print(f"Port names: {device.port_names}")
```

### Port Name Management
```python
# Retrieve current port names
port_mapping = await device.retrieve_port_names()
print(port_mapping)
# Output: {'Port 0': 'Living Room Strip', 'Port 1': 'TV', 'Port 2': 'Lamp', ...}

# Change port names (firmware v1.30 only)
try:
    await device.change_port_name(1, "Smart TV")
    await device.change_port_name(0, "Entertainment Center")  # Strip name
    print("Port names updated successfully")
except FirmwareError as e:
    print(f"Port renaming not supported: {e}")
```

## ⚡ Advanced Polling & Monitoring

### Adaptive Polling System
```python
# Start intelligent polling (mimics official app)
await device.start_adaptive_polling()

# Polling behavior:
# - Normal: polls every 5 seconds
# - Burst: polls every 2 seconds for 4 cycles after commands
# - Auto-triggers burst mode on turn_on/turn_off operations

# Register callback for poll events
def poll_handler(poll_data):
    mode = poll_data['mode']        # 'normal' or 'burst'
    count = poll_data['poll_count'] # Poll sequence number
    data = poll_data['device_data'] # Switch states and watt values
    print(f"Poll #{count} ({mode}): {data}")

device.register_poll_callback("monitor", poll_handler)

# Commands automatically trigger burst mode
await device.turn_on(1)  # Triggers 2-second polling for 8 seconds

# Stop polling
await device.stop_adaptive_polling()
```

### Real-time Change Detection
```python
async def on_consumption_change(data):
    """Called when power consumption changes >1W"""
    port = data['port']
    port_name = data['port_name']
    change = data['change']
    current = data['current_watt']
    print(f"{port_name} (Port {port}): {current:.1f}W ({change:+.1f}W)")

async def on_state_change(data):
    """Called when port switches on/off"""
    port = data['port']
    port_name = data['port_name'] 
    state = data['state_text']  # 'ON' or 'OFF'
    print(f"{port_name} (Port {port}): {state}")

# Setup monitoring with automatic change detection
await device.setup_realtime_monitoring(
    consumption_callback=on_consumption_change,
    state_callback=on_state_change
)

# Start polling to enable monitoring
await device.start_adaptive_polling()
```

## 📊 Power Monitoring

### Real-time Data
```python
# Get current power consumption for specific port
power_data = await device.get_power_data(1)
print(f"Port 1: {power_data['watt']}W")

# Get comprehensive device data
all_data = await device.get_data()
print(f"Switch states: {all_data['switch']}")  # [0,1,0,1,1,0]
print(f"Power values: {all_data['watt']}")     # [0.0,15.2,0.0,8.7,122.5,0.0]
```

### Historical Statistics
```python
# Statistics types:
# 0 = Hourly (last 24 hours)
# 1 = Daily (last 30 days)  
# 2 = Monthly (last 12 months)

# Get hourly data for all ports combined
hourly_stats = await device.get_statistics(0, 0)  # port 0, type 0
print(f"Last 24 hours: {hourly_stats['watt']}")
print(f"Period ending: {hourly_stats['year']}-{hourly_stats['month']}-{hourly_stats['day']} {hourly_stats['hour']}:00")

# Get daily data for specific port
daily_stats = await device.get_statistics(1, 1)   # port 1, type 1
print(f"Port 1 daily consumption: {daily_stats['watt']}")

# Statistics include cost information if configured
if daily_stats['cost'] > 0:
    print(f"Estimated cost: {daily_stats['cost']} {daily_stats['currency']}/kWh")
```

### Data Visualization
```python
# The example scripts include comprehensive visualization
# See: example_scripts/maxsmart_tests_async.py

import matplotlib.pyplot as plt

# Get monthly data
monthly_data = await device.get_statistics(0, 2)
watt_values = monthly_data['watt']

# Plot consumption over time
plt.figure(figsize=(12, 6))
plt.plot(watt_values)
plt.title('Monthly Power Consumption')
plt.ylabel('Power (W)')
plt.xlabel('Month')
plt.show()
```

## 🕐 Device Time Management
```python
# Get device's real-time clock
time_data = await device.get_device_time()
print(f"Device time: {time_data['time']}")
# Output: "2024-07-17,14:30:25"
```

## 🔧 Session Management & Health Checks

### Context Manager Usage
```python
# Automatic initialization and cleanup
async with MaxSmartDevice('192.168.1.100') as device:
    await device.turn_on(1)
    power = await device.get_power_data(1)
    print(f"Power: {power['watt']}W")
# Device automatically closed on exit
```

### Health Monitoring
```python
# Check device connectivity and performance
health = await device.health_check()
print(f"Status: {health['status']}")
print(f"Response time: {health['response_time']}ms")
print(f"Polling active: {health['polling_active']}")

if health['status'] == 'unhealthy':
    print(f"Error: {health['error']}")
```

### Manual Cleanup
```python
# Always clean up resources
try:
    # ... device operations
    pass
finally:
    await device.close()  # Stops polling and closes HTTP session
```

## 🛠️ Error Handling

### Exception Types
```python
from maxsmart.exceptions import (
    DiscoveryError,        # Device discovery failures
    ConnectionError,       # Network connectivity issues
    CommandError,          # Command execution failures
    StateError,           # Device state inconsistencies
    FirmwareError,        # Firmware compatibility issues
    DeviceTimeoutError    # Device response timeouts
)

try:
    devices = await MaxSmartDiscovery.discover_maxsmart()
    device = MaxSmartDevice(devices[0]['ip'])
    await device.initialize_device()
    await device.turn_on(1)
    
except DiscoveryError as e:
    print(f"Discovery failed: {e}")
except ConnectionError as e:
    print(f"Network error: {e}")
except FirmwareError as e:
    print(f"Firmware limitation: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry Logic
The module includes built-in retry mechanisms:
- **Discovery**: 3 attempts with exponential backoff
- **Commands**: 3 retries with 1-second delays
- **State verification**: 3 verification attempts
- **Session management**: Automatic reconnection on failures

## 📁 Example Scripts

The `example_scripts/` directory contains comprehensive examples:

### Basic Examples
- `test_discovery_async.py` - Device discovery with validation
- `test_device_identification.py` - Advanced device identification testing
- `get_port_names_async.py` - Port name retrieval and display
- `retrieve_states_async.py` - Port state checking
- `show_consumption.py` - Real-time power monitoring

### Advanced Examples  
- `maxsmart_tests_async.py` - Complete feature testing with visualization
- `test_adaptive_polling.py` - Polling system demonstration
- `rename_ports.py` - Port name management (v1.30 firmware)
- `test_device_timestamps.py` - Device time synchronization

### Running Examples
```bash
# Install visualization dependencies
pip install -r example_scripts/requirements.txt

# Run comprehensive test suite
python example_scripts/maxsmart_tests_async.py

# Test device identification
python example_scripts/test_device_identification.py

# Test adaptive polling
python example_scripts/test_adaptive_polling.py

# Monitor real-time consumption
python example_scripts/show_consumption.py
```

## ⚙️ Configuration Options

### Discovery Configuration
```python
# Custom timeout and retry settings
devices = await MaxSmartDiscovery.discover_maxsmart(
    ip=None,                    # None for broadcast, IP for unicast
    user_locale="en",           # Locale for error messages
    timeout=3.0,                # Discovery timeout in seconds
    max_attempts=3,             # Maximum discovery attempts
    enhance_with_hardware_ids=True  # Enable hardware identification
)
```

### Device Configuration
```python
device = MaxSmartDevice(
    ip_address="192.168.1.100",
    auto_polling=False          # Start polling automatically after init
)

# Custom session timeouts
device.DEFAULT_TIMEOUT = 15.0  # Command timeout
device.RETRY_COUNT = 5         # Command retry attempts
```

### Polling Configuration
```python
# Customize polling intervals
device.NORMAL_INTERVAL = 10.0  # Normal polling interval (default: 5s)
device.BURST_INTERVAL = 1.0    # Burst polling interval (default: 2s)  
device.BURST_CYCLES = 6        # Burst cycle count (default: 4)
```

## 🔒 Security Considerations

### Network Security
- **Unencrypted HTTP**: All communication is in plain text
- **No authentication**: Devices don't require credentials
- **Local network only**: Devices must be on same network as client
- **Trusted networks**: Only use on secure, trusted networks

### Best Practices
```python
# Use connection limits to prevent resource exhaustion
device.DEFAULT_CONNECTOR_LIMIT = 10
device.DEFAULT_CONNECTOR_LIMIT_PER_HOST = 5

# Always clean up resources
async with MaxSmartDevice(ip) as device:
    # ... operations
    pass  # Automatic cleanup

# Handle exceptions gracefully
try:
    await device.turn_on(1)
except Exception as e:
    logging.error(f"Command failed: {e}")
```

## 🐛 Troubleshooting

### Common Issues

**Device not found during discovery**
```python
# Try targeted discovery
devices = await MaxSmartDiscovery.discover_maxsmart(ip="192.168.1.100")

# Check network connectivity
import socket
try:
    socket.create_connection(("192.168.1.100", 8888), timeout=3)
    print("Device reachable")
except:
    print("Device unreachable")
```

**Power scaling issues**
```python
# Check device firmware and data format
await device.initialize_device()
print(f"Firmware: {device.version}")
print(f"Data format: {device._watt_format}")
print(f"Conversion factor: {device._watt_multiplier}")

# Test with raw data
raw_data = await device.get_data()
print(f"Raw power values: {raw_data['watt']}")
```

**Firmware compatibility errors**
```python
# Check device firmware version
await device.initialize_device()
print(f"Firmware: {device.version}")
print(f"Data format: {device._watt_format}")

# Firmware capabilities:
# v1.06, v1.10, v1.30: Full support including port renaming
# v2.11, v3.36, v3.49: Full control, basic port renaming
```

**Connection timeouts**
```python
# Increase timeouts for slow networks
device.DEFAULT_TIMEOUT = 30.0
device.SESSION_TIMEOUT = 60.0

# Reduce retry count to fail faster
device.RETRY_COUNT = 1
```

### Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed HTTP logging
logging.getLogger('aiohttp').setLevel(logging.DEBUG)
```

## 📈 Performance Notes

### Efficient Usage
- **Reuse device instances**: Don't recreate for each operation
- **Use adaptive polling**: More efficient than manual polling
- **Batch operations**: Minimize individual command calls
- **Context managers**: Ensure proper cleanup

### Resource Management
```python
# Good: Reuse device instance
device = MaxSmartDevice(ip)
await device.initialize_device()
for port in range(1, 7):
    await device.turn_on(port)
await device.close()

# Bad: Create new instances
for port in range(1, 7):
    device = MaxSmartDevice(ip)  # Inefficient
    await device.initialize_device()
    await device.turn_on(port)
    await device.close()
```

## 🤝 Credits

This module builds upon reverse engineering work by [@altery](https://github.com/altery/mh-maxsmart-powerstation) who documented the MaxSmart communication protocol.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **GitHub Repository**: https://github.com/superkikim/maxsmart
- **PyPI Package**: https://pypi.org/project/maxsmart/
- **Issues & Support**: https://github.com/superkikim/maxsmart/issues
- **Example Scripts**: https://github.com/superkikim/maxsmart/tree/main/example_scripts