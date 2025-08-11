# Release Notes

## Version 2.1 (Latest) - Protocol Transparency Release

### 🚀 MAJOR NEW FEATURES

#### Protocol Transparency
- **Unified API**: Same methods (`turn_on`, `turn_off`, `get_data`, `check_state`) work seamlessly with both HTTP and UDP V3 devices
- **Automatic Protocol Detection**: No need to specify protocol - automatically detects and uses the best available protocol
- **Smart Protocol Selection**: Prefers HTTP when available (more features), falls back to UDP V3 when necessary

#### UDP V3 Protocol Support
- **Full UDP V3 Implementation**: Support for devices that only respond to UDP commands (20, 90)
- **New**: Adding support for UDP-only devices (Revogi FW 5.x)
- **Tested**: Successfully tested discovery, state, watts, and on/off on Revogi FW 5.11
- **Command Routing**: Automatic routing between HTTP and UDP V3 based on device capabilities

#### Enhanced Device Discovery
- **Protocol Detection**: Discovery now shows which protocols each device supports
- **Firmware Awareness**: Different protocol support based on firmware version
- **Table Display**: Professional table format showing device info and supported protocols

### 🔧 TECHNICAL IMPROVEMENTS

#### Robust Error Handling
- **Unified Retry Logic**: Same robust retry mechanism (3 attempts, exponential backoff) for both protocols
- **Consistent Timeouts**: Standardized timeout handling across HTTP and UDP V3
- **Graceful Degradation**: Clear error messages when features aren't available on specific protocols

#### Device Initialization
- **Auto-Detection**: Devices automatically detect their optimal protocol during initialization
- **Protocol Parameter**: Optional manual protocol selection (`'http'`, `'udp_v3'`, or `None` for auto)
- **Enhanced Validation**: Improved protocol capability validation

#### Code Architecture
- **Command Abstraction**: Unified command interface that routes to appropriate protocol
- **Mixin Integration**: Clean integration of UDP V3 capabilities into existing device classes
- **Backward Compatibility**: Existing code continues to work without modifications

### 📊 FIRMWARE SUPPORT MATRIX

| Firmware | HTTP | UDP V3 | Auto-Detection | Recommended |
|----------|------|--------|----------------|-------------|
| 1.30     | ✅ Full | ❌ None | `HTTP` | HTTP only |
| 2.11     | ✅ Full | ⚠️ Partial | `HTTP` | HTTP preferred |
| 5.xx+    | ❌ None | ✅ Full | `UDP V3` | UDP V3 only |

### 🎯 USAGE EXAMPLES

#### Transparent Device Control
```python
# Same code works for all firmware versions!
device = MaxSmartDevice('192.168.1.100')  # Auto-detects protocol
await device.initialize_device()

# These methods work regardless of protocol:
await device.turn_on(1)                    # ✅ HTTP or UDP V3
await device.turn_off(3)                   # ✅ HTTP or UDP V3
state = await device.check_state(1)        # ✅ HTTP or UDP V3
power = await device.get_power_data(1)     # ✅ HTTP or UDP V3

print(f"Using protocol: {device.protocol}")
```

#### Enhanced Discovery
```python
devices = await MaxSmartDiscovery.discover_maxsmart()
# Now shows protocol support for each device
```

### 🐛 BUG FIXES
- Fixed device initialization to properly handle protocol detection
- Improved error messages for unsupported operations on specific protocols
- Enhanced timeout handling for UDP communications
- Fixed device representation to include protocol information

### ⚠️ BREAKING CHANGES
- `MaxSmartDevice` constructor now accepts optional `protocol` parameter
- Device string representation now includes protocol information
- Some internal method signatures changed (backward compatibility maintained for public API)

### 🔄 MIGRATION GUIDE
- **Existing Code**: No changes required - auto-detection handles protocol selection
- **Manual Protocol**: Add `protocol='http'` or `protocol='udp_v3'` parameter if needed
- **New Features**: Use same methods regardless of device protocol

### 🧪 TESTING
- Verified with real MaxSmart devices (firmware 1.30, 2.11)
- Tested protocol detection and automatic fallback
- Validated command execution on both HTTP and UDP V3 protocols
- Confirmed transparent operation across different firmware versions

---

## Version 2.0.5

### BUG FIXES
- Fixed keepalive forcing device to refuse requests
- Fixed milliwatt conversion failing for some devices
- Fixed version not being saved in device parameters during initialization
- Added missing translations for error messages
- Removed obsolete example scripts

### IMPROVEMENTS
- Enhanced device initialization to properly retrieve firmware version via UDP discovery
- Improved error handling for firmware compatibility checks
- Better device identification during initialization process
