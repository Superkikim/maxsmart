#!/usr/bin/env python3
# test_enhanced_discovery.py

"""
Test script for the enhanced MaxSmart discovery with hardware IDs.
Compares standard discovery vs enhanced discovery with command 124.
"""

import asyncio
import logging
import sys
from maxsmart import MaxSmartDiscovery

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_enhanced_discovery():
    """Test enhanced discovery with hardware ID enhancement."""
    
    print("🔍 MaxSmart Enhanced Discovery Test")
    print("=" * 70)
    print("Comparing standard UDP discovery vs enhanced discovery with CPU IDs")
    print()
    
    try:
        # Test 1: Standard discovery (no hardware enhancement)
        print("📡 Step 1: Standard UDP Discovery...")
        standard_devices = await MaxSmartDiscovery.discover_maxsmart(enhance_with_hardware_ids=False)
        
        print(f"✅ Found {len(standard_devices)} devices via UDP")
        print()
        
        # Test 2: Enhanced discovery (with hardware IDs)
        print("🔧 Step 2: Enhanced Discovery (UDP + Hardware IDs)...")
        enhanced_devices = await MaxSmartDiscovery.discover_maxsmart(enhance_with_hardware_ids=True)
        
        print(f"✅ Enhanced {len(enhanced_devices)} devices with hardware IDs")
        print()
        
        # Compare results
        print("📊 COMPARISON RESULTS")
        print("=" * 70)
        
        for i, (std_dev, enh_dev) in enumerate(zip(standard_devices, enhanced_devices), 1):
            ip = std_dev['ip']
            name = std_dev.get('name', 'Unknown')
            firmware = std_dev.get('ver', 'Unknown')
            
            print(f"📱 Device {i}: {name} ({ip}) - FW: {firmware}")
            print(f"   Standard Discovery:")
            print(f"      UDP Serial: {repr(std_dev.get('sn', ''))}")
            
            print(f"   Enhanced Discovery:")
            print(f"      UDP Serial: {repr(enh_dev.get('sn', ''))}")
            print(f"      Serial Reliable: {'✅' if enh_dev.get('sn_reliable', False) else '❌'}")
            print(f"      CPU ID: {enh_dev.get('cpuid', 'Not available')}")
            print(f"      Primary ID: {enh_dev.get('primary_id', 'Not set')}")
            print(f"      Primary ID Type: {enh_dev.get('primary_id_type', 'Not set')}")
            print(f"      Unique ID: {enh_dev.get('unique_id', 'Not set')}")
            
            # Show improvement for problematic devices
            std_sn = std_dev.get('sn', '')
            enh_reliable = enh_dev.get('sn_reliable', False)
            
            if not enh_reliable:
                print(f"      🎯 IMPROVEMENT: Corrupted UDP serial fixed with CPU ID!")
            
            print()
            
        # Summary
        problematic_devices = sum(1 for dev in enhanced_devices if not dev.get('sn_reliable', True))
        fixed_devices = sum(1 for dev in enhanced_devices if not dev.get('sn_reliable', True) and dev.get('cpuid'))
        
        print("📈 ENHANCEMENT SUMMARY")
        print("=" * 70)
        print(f"Total devices discovered: {len(enhanced_devices)}")
        print(f"Devices with reliable UDP serial: {len(enhanced_devices) - problematic_devices}")
        print(f"Devices with corrupted UDP serial: {problematic_devices}")
        print(f"Corrupted serials fixed with CPU ID: {fixed_devices}")
        
        if problematic_devices > 0:
            print(f"✅ Success rate: {fixed_devices}/{problematic_devices} ({100*fixed_devices//problematic_devices if problematic_devices > 0 else 0}%)")
        else:
            print("✅ All devices have reliable UDP serials")
            
    except Exception as e:
        print(f"❌ Test failed: {type(e).__name__}: {e}")

async def test_specific_device(ip_address):
    """Test enhanced discovery on a specific device."""
    
    print(f"🔍 Testing Enhanced Discovery: {ip_address}")
    print("=" * 50)
    
    try:
        # Test both modes on specific device
        print("📡 Standard discovery...")
        standard = await MaxSmartDiscovery.discover_maxsmart(ip=ip_address, enhance_with_hardware_ids=False)
        
        print("🔧 Enhanced discovery...")
        enhanced = await MaxSmartDiscovery.discover_maxsmart(ip=ip_address, enhance_with_hardware_ids=True)
        
        if enhanced:
            device = enhanced[0]
            print(f"\n📊 Results for {ip_address}:")
            print(f"   Name: {device.get('name', 'Unknown')}")
            print(f"   Firmware: {device.get('ver', 'Unknown')}")
            print(f"   UDP Serial: {repr(device.get('sn', ''))}")
            print(f"   Serial Reliable: {'✅' if device.get('sn_reliable', False) else '❌'}")
            print(f"   CPU ID: {device.get('cpuid', 'Not available')}")
            print(f"   Primary ID: {device.get('primary_id', 'Not set')}")
            print(f"   Primary ID Type: {device.get('primary_id_type', 'Not set')}")
            print(f"   Unique ID: {device.get('unique_id', 'Not set')}")
            
            if not device.get('sn_reliable', True) and device.get('cpuid'):
                print(f"   🎯 FIXED: Corrupted serial replaced with reliable CPU ID!")
        else:
            print(f"❌ No device found at {ip_address}")
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

def main():
    """Main function with command line argument handling."""
    
    if len(sys.argv) > 1:
        # Test specific IP
        ip_address = sys.argv[1]
        asyncio.run(test_specific_device(ip_address))
    else:
        # Test all discovered devices
        asyncio.run(test_enhanced_discovery())

if __name__ == "__main__":
    main()