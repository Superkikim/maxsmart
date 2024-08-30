#!/usr/bin/env python3
# test_discovery_async.py

import asyncio
from maxsmart import MaxSmartDiscovery

async def discover_devices(ip=None):
    """Discover MaxSmart devices on the network.
    
    Args:
        ip (str): The IP address to discover devices from. Defaults to broadcast address if None.

    Returns:
        list: A list of discovered MaxSmart devices.
    """
    print("Discovering MaxSmart devices...")
    if ip is None:
        ip = "255.255.255.255"  # Use the default broadcast address for discovery
    devices = await MaxSmartDiscovery.discover_maxsmart(ip)  # Await the async method
    return devices  # Return the list of discovered devices

async def main():
    """Main function to execute the discovery process and print the results."""
    try:
        devices = await discover_devices()  # Await the async discovery
        print("Discovered devices:", devices)  # Print the discovered devices
    except ConnectionError as ce:
        print(f"Connection error occurred: {ce}")
    except DiscoveryError as de:
        print(f"Discovery error occurred: {de}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio to run the main async function
