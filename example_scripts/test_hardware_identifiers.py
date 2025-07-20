#!/usr/bin/env python3
# test_hardware_identifiers.py

"""
Test script for MaxSmart command 124 (hardware identifiers).
Tests the new get_device_identifiers() method on all discovered devices.
"""

import asyncio
import logging
import sys
from maxsmart import MaxSmartDiscovery, MaxSmartDevice

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_hardware_identifiers():
    """Test command 124 on all discovered MaxSmart devices."""
    
    print("🔍 MaxSmart Hardware Identifiers Test")
    print("=" * 60)
    print("Testing command 124 to retrieve hardware identifiers")
    print("(MAC address, Device Access Key, CPU ID, Cloud server)")
    print()
    
    try:
        # Discover devices
        print("🔎 Discovering MaxSmart devices...")
        devices = await MaxSmartDiscovery.discover_maxsmart()
        
        if not devices:
            print("❌ No MaxSmart devices found on the network")
            return
            
        print(f"✅ Found {len(devices)} device(s)")
        print()
        
        # Test each device
        for i, device_info in enumerate(devices, 1):
            ip = device_info['ip']
            name = device_info.get('name', 'Unknown')
            version = device_info.get('ver', 'Unknown')
            sn = device_info.get('sn', 'Unknown')
            
            print(f"📱 Device {i}: {name} ({ip})")
            print(f"   Firmware: {version}")
            print(f"   Serial (UDP): {repr(sn)}")
            print()
            
            device = None
            try:
                # Initialize device
                device = MaxSmartDevice(ip)
                await device.initialize_device()
                
                print("   🔧 Testing command 124...")
                
                # Test get_device_identifiers
                identifiers = await device.get_device_identifiers()
                
                print("   ✅ Raw hardware identifiers:")
                for key, value in identifiers.items():
                    print(f"      {key}: {repr(value)}")
                print()
                
                # Test formatted display
                formatted = device.format_identifiers_for_display(identifiers)
                print("   📋 Formatted for display:")
                for key, value in formatted.items():
                    print(f"      {key}: {value}")
                print()
                
                # Test unique identifier generation
                unique_id = await device.get_unique_identifier()
                print(f"   🆔 Best unique identifier: {unique_id}")
                
                # Compare with UDP discovery serial
                print(f"   📊 Comparison:")
                print(f"      UDP Serial: {repr(sn)}")
                print(f"      Best ID: {unique_id}")
                
                # Check if UDP serial is usable
                is_sn_usable = (
                    sn and 
                    isinstance(sn, str) and 
                    sn.strip() and 
                    all(ord(c) < 128 for c in sn) and  # ASCII only
                    sn.isprintable()  # Printable characters
                )
                print(f"      UDP Serial usable: {'✅ Yes' if is_sn_usable else '❌ No (corrupted/empty)'}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error testing device {ip}: {type(e).__name__}: {e}")
                print()
                
            finally:
                if device:
                    await device.close()
                    
            print("-" * 60)
            print()
    
    except Exception as e:
        print(f"❌ Discovery failed: {type(e).__name__}: {e}")

async def test_specific_device(ip_address):
    """Test command 124 on a specific device IP."""
    
    print(f"🔍 Testing specific device: {ip_address}")
    print("=" * 60)
    
    device = None
    try:
        device = MaxSmartDevice(ip_address)
        await device.initialize_device()
        
        print("📡 Testing command 124...")
        identifiers = await device.get_device_identifiers()
        
        print("\n🔧 Raw response:")
        for key, value in identifiers.items():
            print(f"  {key}: {repr(value)}")
            
        print("\n📋 Formatted:")
        formatted = device.format_identifiers_for_display(identifiers)
        for key, value in formatted.items():
            print(f"  {key}: {value}")
            
        unique_id = await device.get_unique_identifier()
        print(f"\n🆔 Unique identifier: {unique_id}")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        
    finally:
        if device:
            await device.close()

def main():
    """Main function with command line argument handling."""
    
    if len(sys.argv) > 1:
        # Test specific IP
        ip_address = sys.argv[1]
        asyncio.run(test_specific_device(ip_address))
    else:
        # Test all discovered devices
        asyncio.run(test_hardware_identifiers())

if __name__ == "__main__":
    main()