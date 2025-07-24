#!/usr/bin/env python3
# test_device_identification.py

"""
Comprehensive test script for MaxSmart device identification.
Shows a complete table with all available identifiers for each device.
"""

import asyncio
import logging
import sys
from maxsmart import MaxSmartDiscovery, MaxSmartDevice

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_separator(char="=", length=120):
    """Print a separator line."""
    print(char * length)

def print_table_header():
    """Print the table header."""
    print_separator()
    print("📋 MAXSMART DEVICE IDENTIFICATION TABLE")
    print_separator()
    
    # Header row
    header = (
        f"{'Device':<15} "
        f"{'IP':<15} "
        f"{'FW':<5} "
        f"{'CPU ID':<26} "
        f"{'MAC (ARP)':<18} "
        f"{'UDP Serial':<20} "
        f"{'Best ID':<32} "
        f"{'Status':<12}"
    )
    print(header)
    print_separator("-")

def print_device_row(device_info):
    """Print a single device row."""
    name = device_info.get('name', 'Unknown')[:14]
    ip = device_info['ip']
    firmware = device_info.get('ver', 'N/A')
    
    identifiers = device_info.get('all_identifiers', {})
    best_id = device_info.get('best_identifier', {})
    
    # Extract key identifiers with safe access
    cpuid_data = identifiers.get('cpuid', {})
    cpuid = cpuid_data.get('value', 'Not available') if cpuid_data else 'Not available'
    if cpuid and cpuid != 'Not available':
        cpuid = str(cpuid)[:25]
    else:
        cpuid = 'Not available'
    
    mac_arp_data = identifiers.get('mac_arp', {})
    mac_arp = mac_arp_data.get('value', 'Not available') if mac_arp_data else 'Not available'
    if mac_arp and mac_arp != 'Not available':
        # Fix: Full MAC address is 17 characters, not 16!
        mac_arp = str(mac_arp)[:17]
    else:
        mac_arp = 'Not available'
    
    udp_serial_data = identifiers.get('udp_serial', {})
    udp_serial = udp_serial_data.get('value', 'Not available') if udp_serial_data else 'Not available'
    if udp_serial and udp_serial != 'Not available':
        udp_serial = str(udp_serial)[:19]
    else:
        udp_serial = 'Not available'
    
    best_id_str = best_id.get('identifier', 'Not set') if best_id else 'Not set'
    if best_id_str and best_id_str != 'Not set':
        best_id_str = str(best_id_str)[:31]
    else:
        best_id_str = 'Not set'
    
    # Status based on best identifier reliability
    if best_id and best_id.get('reliable', False):
        if best_id.get('type') == 'cpuid':
            status = "✅ Excellent"
        elif best_id.get('type') == 'mac_address':
            status = "✅ Very Good"
        elif best_id.get('type') == 'udp_serial':
            status = "⚠️ Good"
        else:
            status = "⚠️ Fair"
    else:
        status = "❌ Poor"
    
    # Print row
    row = (
        f"{name:<15} "
        f"{ip:<15} "
        f"{firmware:<5} "
        f"{cpuid:<26} "
        f"{mac_arp:<18} "
        f"{udp_serial:<20} "
        f"{best_id_str:<32} "
        f"{status:<12}"
    )
    print(row)

def print_detailed_view(device_info):
    """Print detailed view for a single device."""
    print_separator()
    print(f"📱 DETAILED VIEW: {device_info.get('name', 'Unknown')} ({device_info['ip']})")
    print_separator()
    
    # Basic info
    print(f"Device Name: {device_info.get('name', 'Unknown')}")
    print(f"IP Address: {device_info['ip']}")
    print(f"Firmware: {device_info.get('ver', 'Unknown')}")
    print()
    
    # Best identifier
    best_id = device_info.get('best_identifier', {})
    print(f"🎯 RECOMMENDED IDENTIFIER:")
    print(f"   Value: {best_id.get('identifier', 'Not set')}")
    print(f"   Type: {best_id.get('type', 'Unknown')}")
    print(f"   Source: {best_id.get('source', 'Unknown')}")
    print(f"   Reliable: {'✅ Yes' if best_id.get('reliable', False) else '❌ No'}")
    print()
    
    # All identifiers
    all_ids = device_info.get('all_identifiers', {})
    print(f"🔍 ALL AVAILABLE IDENTIFIERS:")
    
    for id_type, data in all_ids.items():
        if isinstance(data, dict) and 'value' in data:
            available = "✅" if data.get('available', False) else "❌"
            value = data.get('value', 'Not available')
            # Handle None values
            if value is None:
                value = 'Not available'
            source = data.get('source', 'Unknown')
            print(f"   {id_type:<12}: {available} {value} (from {source})")
        elif id_type.endswith('_error'):
            # Handle error entries
            print(f"   ⚠️ {id_type}: {data}")
    
    # Show errors if any
    error_keys = [k for k in all_ids.keys() if k.endswith('_error')]
    if not error_keys:
        print("   ✅ No errors encountered")
    
    print()

def get_default_gateway():
    """Get the default gateway IP address."""
    try:
        import subprocess
        import platform
        
        system = platform.system().lower()
        if system == "windows":
            result = subprocess.run(['route', 'print', '0.0.0.0'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if '0.0.0.0' in line and 'Gateway' not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]  # Gateway IP
        elif system in ["linux", "darwin"]:
            result = subprocess.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'default via' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]  # Gateway IP
        return None
    except:
        return None

def test_getmac_functionality():
    """Test getmac library functionality."""
    print("🔧 Testing getmac functionality...")
    try:
        from getmac import get_mac_address
        
        # Try to get default gateway
        gateway_ip = get_default_gateway()
        if gateway_ip:
            print(f"   Default gateway: {gateway_ip}")
            test_mac = get_mac_address(ip=gateway_ip)
            if test_mac:
                print(f"   ✅ getmac available - Gateway MAC: {test_mac}")
                return True
            else:
                print(f"   ⚠️ getmac available but no MAC found for gateway")
                return True  # Still available, just no result
        else:
            print(f"   ⚠️ getmac available but couldn't find default gateway")
            return True  # Still available
    except ImportError:
        print(f"   ❌ getmac library not installed")
        return False
    except Exception as e:
        print(f"   ⚠️ getmac error: {e}")
        return False

async def test_all_devices():
    """Test identification for all discovered devices."""
    
    print("🔍 MaxSmart Device Identification Test")
    print("Testing all available identification methods...")
    print()
    
    try:
        # Test getmac functionality
        getmac_available = test_getmac_functionality()
        print()
        
        # Discover devices (without hardware enhancement to get raw UDP data)
        print("📡 Discovering devices...")
        devices = await MaxSmartDiscovery.discover_maxsmart(enhance_with_hardware_ids=False)
        
        if not devices:
            print("❌ No MaxSmart devices found")
            return
            
        print(f"✅ Found {len(devices)} device(s)")
        print()
        
        # Test each device for all identification methods
        device_results = []
        
        for i, device_info in enumerate(devices, 1):
            ip = device_info['ip']
            name = device_info.get('name', f'Device {i}')
            
            print(f"🔍 Testing device {i}/{len(devices)}: {name} ({ip})")
            
            device = None
            try:
                # Initialize device
                device = MaxSmartDevice(ip)
                device.udp_serial = device_info.get('sn', '')  # Store UDP serial for comparison
                await device.initialize_device()
                
                # Get all available identifiers
                all_identifiers = await device.get_all_identifiers()
                
                # Get best identifier
                best_identifier = await device.get_best_unique_identifier()
                
                # Store results
                device_result = {
                    **device_info,
                    'all_identifiers': all_identifiers,
                    'best_identifier': best_identifier
                }
                device_results.append(device_result)
                
                print(f"   ✅ Completed")
                
            except Exception as e:
                print(f"   ❌ Error: {type(e).__name__}: {e}")
                # Add error result
                device_result = {
                    **device_info,
                    'all_identifiers': {},
                    'best_identifier': {'identifier': f"ip_{ip.replace('.', '_')}", 'type': 'ip_address', 'reliable': False},
                    'error': str(e)
                }
                device_results.append(device_result)
                
            finally:
                if device:
                    await device.close()
        
        print()
        
        # Display results table
        print_table_header()
        for device_result in device_results:
            print_device_row(device_result)
        
        print_separator()
        
        # Statistics
        total_devices = len(device_results)
        excellent_count = sum(1 for d in device_results 
                            if d.get('best_identifier', {}) and d.get('best_identifier', {}).get('type') == 'cpuid')
        very_good_count = sum(1 for d in device_results 
                            if d.get('best_identifier', {}) and d.get('best_identifier', {}).get('type') == 'mac_address')
        good_count = sum(1 for d in device_results 
                       if d.get('best_identifier', {}) and d.get('best_identifier', {}).get('type') == 'udp_serial')
        poor_count = sum(1 for d in device_results 
                       if not d.get('best_identifier', {}) or not d.get('best_identifier', {}).get('reliable', True))
        
        print()
        print("📊 IDENTIFICATION STATISTICS")
        print_separator("-", 50)
        print(f"Total devices: {total_devices}")
        print(f"Excellent (CPU ID): {excellent_count} ({100*excellent_count//total_devices if total_devices > 0 else 0}%)")
        print(f"Very Good (MAC ARP): {very_good_count} ({100*very_good_count//total_devices if total_devices > 0 else 0}%)")
        print(f"Good (UDP Serial): {good_count} ({100*good_count//total_devices if total_devices > 0 else 0}%)")
        print(f"Poor (IP fallback): {poor_count} ({100*poor_count//total_devices if total_devices > 0 else 0}%)")
        print()
        
        # Ask for detailed view
        while True:
            try:
                choice = input("Enter device number for detailed view (1-{}) or 'q' to quit: ".format(len(device_results)))
                if choice.lower() == 'q':
                    break
                    
                device_num = int(choice)
                if 1 <= device_num <= len(device_results):
                    print_detailed_view(device_results[device_num - 1])
                else:
                    print("Invalid device number")
                    
            except (ValueError, KeyboardInterrupt):
                break
        
    except Exception as e:
        print(f"❌ Test failed: {type(e).__name__}: {e}")

async def test_specific_device(ip_address):
    """Test identification for a specific device."""
    
    print(f"🔍 Testing Device Identification: {ip_address}")
    print_separator()
    
    device = None
    try:
        # Test getmac functionality
        getmac_available = test_getmac_functionality()
        print()
        
        # Get UDP discovery info
        print("📡 UDP Discovery...")
        devices = await MaxSmartDiscovery.discover_maxsmart(ip=ip_address, enhance_with_hardware_ids=False)
        
        udp_info = {}
        if devices:
            udp_info = devices[0]
            print(f"   Name: {udp_info.get('name', 'Unknown')}")
            print(f"   Firmware: {udp_info.get('ver', 'Unknown')}")
            print(f"   UDP Serial: {repr(udp_info.get('sn', ''))}")
        else:
            print("   ❌ No UDP response")
        print()
        
        # Initialize device and test all identification methods
        print("🔧 Testing identification methods...")
        device = MaxSmartDevice(ip_address)
        device.udp_serial = udp_info.get('sn', '')
        await device.initialize_device()
        
        # Get all identifiers
        all_identifiers = await device.get_all_identifiers()
        best_identifier = await device.get_best_unique_identifier()
        
        # Create result for display
        device_result = {
            **udp_info,
            'ip': ip_address,
            'all_identifiers': all_identifiers,
            'best_identifier': best_identifier
        }
        
        # Display detailed view
        print_detailed_view(device_result)
        
        # Show table view
        print_table_header()
        print_device_row(device_result)
        print_separator()
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        
    finally:
        if device:
            await device.close()

def main():
    """Main function with command line argument handling."""
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--getmac-test":
            # Test getmac functionality only
            print("🔧 Testing getmac Library")
            print_separator()
            test_getmac_functionality()
        else:
            # Test specific IP
            asyncio.run(test_specific_device(arg))
    else:
        # Test all discovered devices
        asyncio.run(test_all_devices())

if __name__ == "__main__":
    main()