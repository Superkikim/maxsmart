#!/usr/bin/env python3
# test_device_timestamps.py

import asyncio
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError

async def discover_devices():
    """Discover MaxSmart devices on the network."""
    print("Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()
        devices = await discovery.discover_maxsmart()
        return devices
    except ConnectionError as ce:
        print(f"Connection error occurred during discovery: {ce}")
        return []
    except DiscoveryError as de:
        print(f"Discovery error occurred: {de}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during discovery: {e}")
        return []

async def get_device_timestamp(device_info):
    """Get timestamp from a specific device using CMD 502."""
    device_ip = device_info["ip"]
    device_name = device_info["name"]
    device_sn = device_info["sn"]
    device_ver = device_info.get("ver", "Unknown")
    protocol = device_info.get("protocol", "http")
    mac = device_info.get("mac", "Unknown")

    print(f"📱 Testing device: {device_name}")
    print(f"   IP: {device_ip}")
    print(f"   Protocol: {protocol}")
    print(f"   MAC: {mac}")
    print(f"   Serial: {device_sn}")

    device = MaxSmartDevice(device_ip, protocol=protocol, sn=device_sn)
    
    try:
        # Initialize device
        await device.initialize_device()
        
        # Get device timestamp
        try:
            response = await device.get_device_time()  # Use public method instead of _send_command
            device_time = response.get("time", "Unknown")
            return {
                "ip": device_ip,
                "name": device_name, 
                "sn": device_sn,
                "firmware": device_ver,
                "timestamp": device_time,
                "status": "SUCCESS"
            }
        except Exception as e:
            return {
                "ip": device_ip,
                "name": device_name,
                "sn": device_sn, 
                "firmware": device_ver,
                "timestamp": "ERROR",
                "status": "COMMAND_FAILED",
                "error": str(e)
            }
            
    except Exception as e:
        return {
            "ip": device_ip,
            "name": device_name,
            "sn": device_sn,
            "firmware": device_ver, 
            "timestamp": "ERROR",
            "status": "INIT_FAILED",
            "error": str(e)
        }
        
    finally:
        try:
            await device.close()
        except:
            pass  # Ignore close errors

def print_results_table(results):
    """Print results in a formatted table."""
    if not results:
        print("No results to display.")
        return
    
    # Table headers
    headers = ["IP", "Name", "SN", "FW", "Timestamp"]
    
    # Calculate column widths
    col_widths = {
        "ip": max(len("IP"), max(len(r["ip"]) for r in results)),
        "name": max(len("Name"), max(len(r["name"] or "N/A") for r in results)),
        "sn": max(len("SN"), max(len(r["sn"] or "N/A") for r in results)),
        "firmware": max(len("FW"), max(len(r["firmware"] or "N/A") for r in results)),
        "timestamp": max(len("Timestamp"), max(len(r["timestamp"] or "N/A") for r in results))
    }
    
    # Print header
    print(f"\n{'='*80}")
    print("DEVICE TIMESTAMPS")
    print(f"{'='*80}")
    
    header_line = (f"{headers[0]:<{col_widths['ip']}} | "
                  f"{headers[1]:<{col_widths['name']}} | "
                  f"{headers[2]:<{col_widths['sn']}} | "
                  f"{headers[3]:<{col_widths['firmware']}} | "
                  f"{headers[4]:<{col_widths['timestamp']}}")
    
    print(header_line)
    print("-" * len(header_line))
    
    # Print each row
    for result in results:
        name = result["name"] or "N/A"
        sn = result["sn"] or "N/A"
        firmware = result["firmware"] or "N/A"
        timestamp = result["timestamp"] or "N/A"
        
        # Add status indicator
        if result["status"] == "SUCCESS":
            status_icon = "✅"
        else:
            status_icon = "❌"
            
        row_line = (f"{result['ip']:<{col_widths['ip']}} | "
                   f"{name:<{col_widths['name']}} | "
                   f"{sn:<{col_widths['sn']}} | "
                   f"{firmware:<{col_widths['firmware']}} | "
                   f"{timestamp:<{col_widths['timestamp']}} {status_icon}")
        
        print(row_line)
    
    print(f"{'='*80}")
    
    # Summary
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    total_count = len(results)
    print(f"Summary: {success_count}/{total_count} devices responded successfully")
    
    # Show errors if any
    failed_devices = [r for r in results if r["status"] != "SUCCESS"]
    if failed_devices:
        print(f"\nFailed devices:")
        for device in failed_devices:
            print(f"  ❌ {device['name']} ({device['ip']}): {device['status']}")

async def main():
    """Main function to discover devices and get all timestamps."""
    try:
        # Discover all devices
        devices = await discover_devices()
        if not devices:
            print("No MaxSmart devices found.")
            return

        print(f"Found {len(devices)} device(s). Getting timestamps...\n")
        
        # Get timestamp from each device
        results = []
        for i, device_info in enumerate(devices, 1):
            print(f"Processing device {i}/{len(devices)}: {device_info['name']} ({device_info['ip']})...")
            result = await get_device_timestamp(device_info)
            results.append(result)
        
        # Display results table
        print_results_table(results)
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())