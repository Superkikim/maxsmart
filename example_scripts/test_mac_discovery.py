#!/usr/bin/env python3
# test_mac_discovery.py

"""
Test script for MAC address discovery methods.
Tests getmac, nmap, and native ARP approaches.
"""

import asyncio
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,  # Show all details for debugging
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_mac_discovery_methods(ip_address):
    """Test all MAC discovery methods for a specific IP."""
    
    print(f"🔍 Testing MAC Discovery Methods for {ip_address}")
    print("=" * 60)
    
    # Test each method individually
    methods = [
        ("getmac library", NetworkUtils._try_getmac_library),
        ("nmap scan", NetworkUtils._try_nmap_scan),
        ("native ARP", NetworkUtils._try_native_arp),
    ]
    
    results = {}
    
    for method_name, method_func in methods:
        print(f"\n🔧 Testing {method_name}...")
        try:
            mac = await method_func(ip_address, timeout=10.0)
            if mac:
                normalized = NetworkUtils._normalize_mac_address(mac)
                results[method_name] = {
                    "success": True,
                    "mac": normalized,
                    "raw": mac
                }
                print(f"   ✅ Success: {normalized} (raw: {mac})")
            else:
                results[method_name] = {
                    "success": False,
                    "error": "No MAC returned"
                }
                print(f"   ❌ Failed: No MAC returned")
                
        except Exception as e:
            results[method_name] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ Failed: {e}")
    
    # Test combined method
    print(f"\n🎯 Testing combined method (automatic fallback)...")
    try:
        combined_mac = await NetworkUtils.get_mac_from_arp(ip_address, timeout=15.0)
        if combined_mac:
            results["combined"] = {
                "success": True,
                "mac": combined_mac
            }
            print(f"   ✅ Success: {combined_mac}")
        else:
            results["combined"] = {
                "success": False,
                "error": "No MAC returned"
            }
            print(f"   ❌ Failed: No MAC returned")
    except Exception as e:
        results["combined"] = {
            "success": False,
            "error": str(e)
        }
        print(f"   ❌ Failed: {e}")
    
    # Summary
    print(f"\n📊 SUMMARY for {ip_address}")
    print("=" * 60)
    for method, result in results.items():
        status = "✅" if result["success"] else "❌"
        if result["success"]:
            print(f"{method:<20}: {status} {result['mac']}")
        else:
            print(f"{method:<20}: {status} {result['error']}")
    
    return results

async def test_system_capabilities():
    """Test system capabilities for MAC discovery."""
    
    print("🔧 Testing System Capabilities")
    print("=" * 60)
    
    # Test general ARP functionality
    arp_test = await NetworkUtils.test_arp_functionality()
    
    print(f"System: {arp_test['system']}")
    print(f"Methods available: {', '.join(arp_test.get('methods_tested', []))}")
    print(f"ARP Available: {'✅' if arp_test['arp_available'] else '❌'}")
    print(f"Ping Available: {'✅' if arp_test['ping_available'] else '❌'}")
    print()
    
    print("Gateway Tests:")
    for test_ip in arp_test['test_ips']:
        ip = test_ip['ip']
        mac = test_ip.get('mac', 'Not found')
        success = "✅" if test_ip.get('success', False) else "❌"
        error = test_ip.get('error', '')
        
        print(f"   {ip:<15} {success} {mac}")
        if error:
            print(f"                   Error: {error}")
    
    return arp_test

async def test_maxsmart_devices():
    """Test MAC discovery on actual MaxSmart devices."""
    
    print("\n🔍 Testing MAC Discovery on MaxSmart Devices")
    print("=" * 60)
    
    # Import here to avoid circular imports
    from maxsmart import MaxSmartDiscovery
    
    try:
        devices = await MaxSmartDiscovery.discover_maxsmart(enhance_with_hardware_ids=False)
        
        if not devices:
            print("❌ No MaxSmart devices found")
            return
            
        print(f"✅ Found {len(devices)} MaxSmart device(s)")
        print()
        
        # Test first few devices
        test_devices = devices[:3]  # Test first 3 devices
        
        results = {}
        for device in test_devices:
            ip = device['ip']
            name = device.get('name', 'Unknown')
            print(f"🔍 Testing {name} ({ip})")
            
            device_results = await test_mac_discovery_methods(ip)
            results[ip] = device_results
            print()
        
        # Overall summary
        print("📈 OVERALL RESULTS")
        print("=" * 60)
        
        method_success_count = {}
        for ip, device_results in results.items():
            for method, result in device_results.items():
                if method not in method_success_count:
                    method_success_count[method] = {"success": 0, "total": 0}
                method_success_count[method]["total"] += 1
                if result["success"]:
                    method_success_count[method]["success"] += 1
        
        for method, stats in method_success_count.items():
            success_rate = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            print(f"{method:<20}: {stats['success']}/{stats['total']} ({success_rate:.0f}%)")
            
    except Exception as e:
        print(f"❌ Error testing MaxSmart devices: {e}")

def main():
    """Main function."""
    
    if len(sys.argv) > 1:
        # Test specific IP
        ip_address = sys.argv[1]
        asyncio.run(test_mac_discovery_methods(ip_address))
    else:
        # Test system capabilities and MaxSmart devices
        async def run_all_tests():
            await test_system_capabilities()
            await test_maxsmart_devices()
        
        asyncio.run(run_all_tests())

if __name__ == "__main__":
    main()