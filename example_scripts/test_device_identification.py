#!/usr/bin/env python3
# test_device_identification.py

"""
Simplified test script for MaxSmart device identification.
Shows the new simplified discovery format with essential identifiers.
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

def print_separator(char="=", length=100):
    """Print a separator line."""
    print(char * length)

def print_table_header():
    """Print the table header."""
    print_separator()
    print("📋 MAXSMART DEVICE IDENTIFICATION TABLE (Simplified Format)")
    print_separator()
    
    # Header row
    header = (
        f"{'Device':<15} "
        f"{'IP':<15} "
        f"{'FW':<5} "
        f"{'Serial Number':<20} "
        f"{'CPU ID':<26} "
        f"{'MAC (ARP)':<18} "
        f"{'Server':<20}"
    )
    print(header)
    print_separator("-")

def print_device_row(device_info):
    """Print a single device row."""
    name = device_info.get('name', 'Unknown')[:14]
    ip = device_info['ip']
    firmware = device_info.get('ver', 'N/A')
    sn = device_info.get('sn', 'N/A')[:19]
    
    # Extract simplified identifiers
    cpuid = device_info.get('cpuid', 'Not available')
    if cpuid and cpuid != 'Not available':
        cpuid = str(cpuid)[:25]
    
    mac = device_info.get('mac', 'Not available')
    if mac and mac != 'Not available':
        mac = str(mac)[:17]
    
    server = device_info.get('server', 'Not available')
    if server and server != 'Not available':
        server = str(server)[:19]
    
    # Print row
    row = (
        f"{name:<15} "
        f"{ip:<15} "
        f"{firmware:<5} "
        f"{sn:<20} "
        f"{cpuid:<26} "
        f"{mac:<18} "
        f"{server:<20}"
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
    print(f"Serial Number: {device_info.get('sn', 'Unknown')}")
    print()
    
    # Essential identifiers
    print(f"🎯 ESSENTIAL IDENTIFIERS:")
    print(f"   CPU ID: {device_info.get('cpuid', 'Not available')}")
    print(f"   MAC Address: {device_info.get('mac', 'Not available')}")
    print(f"   Cloud Server: {device_info.get('server', 'Not available')}")
    print()
    
    # Port information
    pname = device_info.get('pname', [])
    print(f"🔌 PORT CONFIGURATION:")
    print(f"   Port count: {len(pname)} configured names")
    if pname:
        for i, port_name in enumerate(pname, 1):
            print(f"   Port {i}: {port_name}")
    else:
        print(f"   No port names configured (normal for FW 2.11+)")
    print()

def test_getmac_functionality():
    """Test getmac library functionality."""
    print("🔧 Testing getmac functionality...")
    try:
        from getmac import get_mac_address
        
        # Try to get MAC for localhost
        test_mac = get_mac_address(interface="eth0")
        if test_mac:
            print(f"   ✅ getmac available - Local interface MAC found")
            return True
        else:
            print(f"   ⚠️ getmac available but no MAC found for eth0")
            return True  # Still available, just no result
    except ImportError:
        print(f"   ❌ getmac library not installed")
        return False
    except Exception as e:
        print(f"   ⚠️ getmac error: {e}")
        return False

async def test_all_devices():
    """Test simplified identification for all discovered devices."""
    
    print("🔍 MaxSmart Device Identification Test (Simplified)")
    print("Testing simplified discovery format...")
    print()
    
    try:
        # Test getmac functionality
        getmac_available = test_getmac_functionality()
        print()
        
        # Discover devices (now always includes essential hardware identifiers)
        print("📡 Discovering devices...")
        devices = await MaxSmartDiscovery.discover_maxsmart()
        
        if not devices:
            print("❌ No MaxSmart devices found")
            return
            
        print(f"✅ Found {len(devices)} device(s)")
        print()
        
        # Display results table
        print_table_header()
        for device_result in devices:
            print_device_row(device_result)
        
        print_separator()
        
        # Statistics
        total_devices = len(devices)
        devices_with_cpuid = sum(1 for d in devices if d.get('cpuid'))
        devices_with_mac = sum(1 for d in devices if d.get('mac'))
        devices_with_server = sum(1 for d in devices if d.get('server'))
        
        print()
        print("📊 IDENTIFICATION STATISTICS")
        print_separator("-", 50)
        print(f"Total devices: {total_devices}")
        print(f"With CPU ID: {devices_with_cpuid} ({100*devices_with_cpuid//total_devices if total_devices > 0 else 0}%)")
        print(f"With MAC address: {devices_with_mac} ({100*devices_with_mac//total_devices if total_devices > 0 else 0}%)")
        print(f"With cloud server: {devices_with_server} ({100*devices_with_server//total_devices if total_devices > 0 else 0}%)")
        print()
        
        # Ask for detailed view
        while True:
            try:
                choice = input("Enter device number for detailed view (1-{}) or 'q' to quit: ".format(len(devices)))
                if choice.lower() == 'q':
                    break
                    
                device_num = int(choice)
                if 1 <= device_num <= len(devices):
                    print_detailed_view(devices[device_num - 1])
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
        
        # Get discovery info
        print("📡 Discovery...")
        devices = await MaxSmartDiscovery.discover_maxsmart(ip=ip_address)
        
        if not devices:
            print("   ❌ No response from device")
            return
            
        device_info = devices[0]
        print(f"   ✅ Device responded")
        print()
        
        # Display detailed view
        print_detailed_view(device_info)
        
        # Show table view
        print_table_header()
        print_device_row(device_info)
        print_separator()
        
        # Test additional device methods
        print("🔧 Testing device methods...")
        protocol = device_info.get("protocol", "http")
        serial = device_info.get("sn", "")
        port_count = device_info.get("nr_of_ports", 6)
        device = MaxSmartDevice(ip_address, protocol=protocol, sn=serial)
        device.port_count = port_count  # Set port count from discovery
        await device.initialize_device()
        
        # Test hardware identifiers method
        try:
            hw_ids = await device.get_device_identifiers()
            print(f"   Hardware IDs via device method:")
            print(f"     CPU ID: {hw_ids.get('cpuid', 'Not available')}")
            print(f"     Server: {hw_ids.get('server', 'Not available')}")
        except Exception as e:
            print(f"   ❌ Hardware ID method failed: {e}")
            
        # Test MAC via ARP method
        try:
            mac_arp = await device.get_mac_address_via_arp()
            print(f"   MAC via ARP method: {mac_arp or 'Not found'}")
        except Exception as e:
            print(f"   ❌ ARP MAC method failed: {e}")
        
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