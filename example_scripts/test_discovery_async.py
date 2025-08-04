#!/usr/bin/env python3
"""
MaxSmart Device Discovery Tool
=============================

This script discovers MaxSmart devices on the network and executes command 124
on each discovered device for detailed information.

Usage:
    python3 maxsmart_discovery.py [IP_ADDRESS]
    
Examples:
    python3 maxsmart_discovery.py                    # Broadcast discovery
    python3 maxsmart_discovery.py 192.168.1.100     # Target specific device
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
    print("-" * 80)
    print(f"{'#':<3} {'Device Name':<20} {'Serial Number':<20} {'IP Address':<15} {'Version':<8}")
    print("-" * 80)
    
    for i, device in enumerate(devices, 1):
        print(f"{i:<3} {device['name']:<20} {device['sn']:<20} {device['ip']:<15} {device['ver']:<8}")
    
    print("-" * 80)
    print()


async def execute_command_124(device: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Execute command 124 on a specific device via HTTP request.
    
    Args:
        device: Device information dictionary
        
    Returns:
        Command result or None if failed
    """
    import aiohttp
    import asyncio
    
    try:
        logger.info(f"📡 Executing command 124 on {device['name']} ({device['ip']})...")
        
        # Make actual HTTP request to the device
        url = f"http://{device['ip']}/?cmd=124"
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    response_text = await response.text()
                    
                    # Parse JSON response
                    import json
                    cmd124_response = json.loads(response_text)
                    
                    # Add device context for table display
                    result = {
                        'device_sn': device['sn'],
                        'device_name': device['name'],
                        'device_ip': device['ip'],
                        'command_response': cmd124_response,
                        'success': cmd124_response.get('code') == 200
                    }
                    
                    logger.info(f"✅ Command 124 completed for {device['name']}")
                    return result
                else:
                    logger.error(f"❌ HTTP {response.status} from {device['name']}")
                    return None
        
    except asyncio.TimeoutError:
        logger.error(f"❌ Timeout executing command 124 on {device['name']}")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to execute command 124 on {device['name']}: {e}")
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
    
    print(f"🔄 Executing command 124 on {len(devices)} device(s)...\n")
    
    # Execute command 124 on all devices concurrently
    tasks = [execute_command_124(device) for device in devices]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out None results and exceptions
    successful_results = [
        result for result in results 
        if result is not None and not isinstance(result, Exception)
    ]
    
    return successful_results


def print_command_results(results: List[Dict[str, Any]]):
    """Print the results of command 124 execution in a formatted table."""
    if not results:
        print("❌ No successful command executions.")
        return
    
    print(f"\n📊 Command 124 Results ({len(results)} successful):")
    print("=" * 120)
    
    # Header
    header = f"{'Device Name':<15} {'Serial Number':<20} {'IP Address':<15} {'CPU ID':<25} {'PLC MAC':<15} {'PLC DAK':<20} {'Server':<15}"
    print(header)
    print("=" * 120)
    
    # Data rows
    for result in results:
        if not result['success']:
            continue
            
        data = result['command_response']['data']
        row = (f"{result['device_name']:<15} "
               f"{result['device_sn']:<20} "
               f"{result['device_ip']:<15} "
               f"{data['cpuid']:<25} "
               f"{data['plcmac']:<15} "
               f"{data['plcdak']:<20} "
               f"{data['server']:<15}")
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
        
        # Print discovery results
        print_device_summary(devices)
        
        if not devices:
            logger.info("🔍 Try running with broadcast discovery or check network connectivity.")
            return 0
        
        # Process devices with command 124
        command_results = await process_devices(devices)
        
        # Print command results
        print_command_results(command_results)
        
        # Show detailed JSON if requested
        if args.show_json:
            print_detailed_json_results(command_results)
        
        # Export to CSV if requested
        if args.export_csv:
            export_results_to_csv(devices, command_results)
        
        # Final summary
        print(f"\n✨ Discovery complete! Found {len(devices)} device(s), "
              f"executed command 124 on {len(command_results)} device(s).")
        
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