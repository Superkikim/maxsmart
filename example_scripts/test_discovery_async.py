#!/usr/bin/env python3
"""
MaxSmart Device Discovery Tool v2.1.0
=====================================

This script discovers MaxSmart devices on the network with protocol detection
and executes appropriate commands based on device capabilities.

Features:
- Automatic protocol detection (http vs udp_v3)
- Firmware-aware command execution
- Protocol transparency demonstration

Usage:
    python3 test_discovery_async.py [IP_ADDRESS]

Examples:
    python3 test_discovery_async.py                    # Broadcast discovery
    python3 test_discovery_async.py 192.168.1.100     # Target specific device
"""

import asyncio
import logging
import argparse
import re
from typing import List, Dict, Any, Optional
from maxsmart.discovery import MaxSmartDiscovery
from maxsmart.exceptions import DiscoveryError, ConnectionError

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def is_valid_ip(ip: str) -> bool:
    """
    
    try:
        import aiohttp
    except ImportError:
        print("❌ aiohttp is required for HTTP requests")
        print("Install it with: pip install aiohttp")
        return 1Validate IP address format."""
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    if not re.match(pattern, ip):
        return False
    
    # Additional validation for valid IP ranges
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)


def print_banner():
    """Display a nice banner for the script."""
    print("=" * 60)
    print("        MaxSmart Device Discovery Tool")
    print("=" * 60)
    print()


def print_device_summary(devices: List[Dict[str, Any]]):
    """Print a summary table of discovered devices."""
    if not devices:
        print("❌ No devices discovered.")
        return
    
    print(f"✅ Discovered {len(devices)} device(s):")
    print("-" * 115)
    print(f"{'#':<3} {'Device Name':<20} {'Serial Number':<20} {'IP Address':<15} {'Version':<8} {'Protocol':<10} {'MAC Address':<18} {'Ports'}")
    print("-" * 125)

    for i, device in enumerate(devices, 1):
        # Use protocol and port count from discovery
        protocol = device.get('protocol', 'unknown')
        mac = device.get('mac', 'N/A')
        port_count = device.get('nr_of_ports', 6)
        print(f"{i:<3} {device['name']:<20} {device['sn']:<20} {device['ip']:<15} {device['ver']:<8} {protocol:<10} {mac:<18} {port_count}P")

    print("-" * 125)
    print()


async def test_device_capabilities(device: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Test device capabilities using protocol transparency (v2.1.0).

    Args:
        device: Device information dictionary

    Returns:
        Test result or None if failed
    """
    from maxsmart import MaxSmartDevice

    try:
        # Use protocol from discovery
        protocol = device.get('protocol', 'http')

        if protocol == 'udp_v3':
            test_name = "udp_v3 get_data()"
        else:
            test_name = "HTTP get_device_identifiers()"

        logger.info(f"📡 Testing {test_name} on {device['name']} ({device['ip']}) - Protocol: {protocol}")

        # Create device with protocol and serial from discovery
        serial = device.get('sn', '')
        test_device = MaxSmartDevice(device['ip'], protocol=protocol, sn=serial)
        await test_device.initialize_device()

        # Test appropriate capability based on protocol
        if protocol == 'udp_v3':
            # Test udp_v3 capability
            data = await test_device.get_data()
            result = {
                'device_sn': device['sn'],
                'device_name': device['name'],
                'device_ip': device['ip'],
                'protocol': 'udp_v3',
                'mac': device.get('mac', 'N/A'),
                'test_result': f"get_data() returned {len(data.get('watt', []))} ports",
                'success': len(data.get('watt', [])) > 0
            }
        else:
            # Test HTTP capability
            hw_ids = await test_device.get_device_identifiers()
            result = {
                'device_sn': device['sn'],
                'device_name': device['name'],
                'device_ip': device['ip'],
                'protocol': 'http',
                'mac': device.get('mac', 'N/A'),
                'test_result': f"Hardware IDs: CPU={hw_ids.get('cpuid', 'N/A')[:8]}...",
                'success': bool(hw_ids.get('cpuid'))
            }

        await test_device.close()
        logger.info(f"✅ {test_name} completed for {device['name']}")
        return result

    except Exception as e:
        logger.error(f"❌ Failed to test {device['name']}: {e}")
        return None


async def process_devices(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process all devices with command 124 concurrently.
    
    Args:
        devices: List of discovered devices
        
    Returns:
        List of command results
    """
    if not devices:
        return []
    
    print(f"🔄 Testing protocol-specific capabilities on {len(devices)} device(s)...\n")

    # Test device capabilities concurrently
    tasks = [test_device_capabilities(device) for device in devices]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out None results and exceptions
    successful_results = [
        result for result in results 
        if result is not None and not isinstance(result, Exception)
    ]
    
    return successful_results


def print_test_results(results: List[Dict[str, Any]]):
    """Print the results of protocol-specific capability tests."""
    if not results:
        print("❌ No successful capability tests.")
        return

    print(f"\n📊 Protocol Capability Test Results ({len(results)} successful):")
    print("=" * 120)

    # Header
    header = f"{'Device Name':<15} {'IP Address':<15} {'Protocol':<10} {'MAC Address':<18} {'Test Result':<40} {'Status':<10}"
    print(header)
    print("=" * 120)

    # Data rows
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        mac = result.get('mac', 'N/A')
        row = (f"{result['device_name']:<15} "
               f"{result['device_ip']:<15} "
               f"{result['protocol']:<10} "
               f"{mac:<18} "
               f"{result['test_result']:<40} "
               f"{status:<10}")
        print(row)

    print("=" * 120)
    
    # Show any failed commands
    failed_devices = [r for r in results if not r['success']]
    if failed_devices:
        print(f"\n❌ Failed command executions ({len(failed_devices)}):")
        for failed in failed_devices:
            print(f"   • {failed['device_name']} ({failed['device_sn']})")


def export_results_to_csv(discovery_results: List[Dict[str, Any]], cmd124_results: List[Dict[str, Any]], filename: str = "maxsmart_devices.csv"):
    """Export all results to a CSV file for further analysis."""
    try:
        import csv
        
        # Combine discovery and command 124 data
        combined_data = []
        
        for device in discovery_results:
            # Find corresponding command 124 result
            cmd124_data = next(
                (r for r in cmd124_results if r['device_sn'] == device['sn'] and r['success']), 
                None
            )
            
            row = {
                'device_name': device['name'],
                'serial_number': device['sn'],
                'ip_address': device['ip'],
                'version': device['ver'],
                'discovery_cpuid': device.get('cpuid', ''),
                'discovery_plcmac': device.get('plcmac', ''),
                'discovery_plcdak': device.get('plcdak', ''),
                'discovery_cloud_server': device.get('cloud_server', ''),
            }
            
            # Add command 124 data if available
            if cmd124_data:
                cmd_data = cmd124_data['command_response']['data']
                row.update({
                    'cmd124_cpuid': cmd_data['cpuid'],
                    'cmd124_plcmac': cmd_data['plcmac'],
                    'cmd124_plcdak': cmd_data['plcdak'],
                    'cmd124_server': cmd_data['server'],
                    'cmd124_status': 'success'
                })
            else:
                row.update({
                    'cmd124_cpuid': '',
                    'cmd124_plcmac': '',
                    'cmd124_plcdak': '',
                    'cmd124_server': '',
                    'cmd124_status': 'failed'
                })
            
            combined_data.append(row)
        
        # Write to CSV
        if combined_data:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = combined_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(combined_data)
            
            print(f"📄 Results exported to {filename}")
        
    except Exception as e:
        logger.error(f"❌ Failed to export CSV: {e}")


def print_detailed_json_results(results: List[Dict[str, Any]]):
    """Print detailed JSON results for debugging purposes."""
    print(f"\n🔍 Detailed JSON Results:")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        if result['success']:
            print(f"\n📱 Device {i}: {result['device_name']} ({result['device_sn']})")
            print("-" * 50)
            
            response = result['command_response']
            print(f"Response Code: {response['code']}")
            print(f"Command: {response['response']}")
            print("Data:")
            for key, value in response['data'].items():
                print(f"  {key}: {value}")
        else:
            print(f"\n❌ Device {i}: {result['device_name']} - FAILED")
    
    print("=" * 80)


async def main():
    """Main execution function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Discover MaxSmart devices and execute command 124.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Discover all devices via broadcast
  %(prog)s 192.168.1.100     # Target specific device IP
  %(prog)s --help            # Show this help message
        """
    )
    parser.add_argument(
        'ip_address', 
        nargs='?', 
        default=None, 
        help="Target IP address for discovery (default: broadcast discovery)"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose logging"
    )
    parser.add_argument(
        '--export-csv',
        action='store_true',
        help="Export results to CSV file"
    )
    parser.add_argument(
        '--show-json',
        action='store_true',
        help="Show detailed JSON responses"
    )
    
    args = parser.parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate IP address if provided
    if args.ip_address and not is_valid_ip(args.ip_address):
        logger.error("❌ Invalid IP address format provided.")
        print("Please provide a valid IP address (e.g., 192.168.1.100)")
        return 1
    
    # Display banner
    print_banner()
    
    try:
        # Discovery phase
        discovery_mode = "targeted" if args.ip_address else "broadcast"
        logger.info(f"🔍 Starting {discovery_mode} discovery...")
        
        if args.ip_address:
            logger.info(f"🎯 Targeting device at {args.ip_address}")
        else:
            logger.info("📡 Broadcasting to discover all devices")
        
        # Discover devices
        devices = await MaxSmartDiscovery.discover_maxsmart(
            ip=args.ip_address,
            user_locale='en'
        )

        # Display raw discovery data
        print("\n" + "="*80)
        print("🔍 RAW DISCOVERY DATA:")
        print("="*80)
        import json
        for i, device in enumerate(devices, 1):
            print(f"\n📱 Device {i} RAW data:")
            print(json.dumps(device, indent=2, default=str))
        print("\n" + "="*80)
        print("🏁 END RAW DISCOVERY DATA")
        print("="*80 + "\n")

        # Print discovery results
        print_device_summary(devices)
        
        if not devices:
            logger.info("🔍 Try running with broadcast discovery or check network connectivity.")
            return 0
        
        # Process devices with command 124
        command_results = await process_devices(devices)
        
        # Print test results
        print_test_results(command_results)
        
        # Show detailed JSON if requested
        if args.show_json:
            print_detailed_json_results(command_results)
        
        # Export to CSV if requested
        if args.export_csv:
            export_results_to_csv(devices, command_results)
        
        # Final summary
        print(f"\n✨ Discovery complete! Found {len(devices)} device(s), "
              f"tested capabilities on {len(command_results)} device(s).")
        
        return 0
        
    except DiscoveryError as e:
        logger.error(f"❌ Discovery error: {e}")
        print("This might be due to network issues or no devices being available.")
        return 1
        
    except ConnectionError as e:
        logger.error(f"❌ Connection error: {e}")
        print("Please check your network connection and try again.")
        return 1
        
    except KeyboardInterrupt:
        logger.info("🛑 Discovery interrupted by user.")
        return 1
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        print("An unexpected error occurred. Run with --verbose for more details.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
        exit(1)