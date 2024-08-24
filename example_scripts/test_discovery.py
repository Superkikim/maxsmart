#!/usr/bin/env python3
# test_discovery.py

from maxsmart import MaxSmartDiscovery

def discover_devices(ip=None):
    """Discover MaxSmart devices on the network.
    
    Args:
        ip (str): The IP address to discover devices from. Defaults to broadcast address if None.

    Returns:
        list: A list of discovered MaxSmart devices.
    """
    print("Discovering MaxSmart devices...")
    if ip is None:
        ip = "255.255.255.255"  # Use the default broadcast address for discovery
    devices = MaxSmartDiscovery.discover_maxsmart(ip)  # Call the static method directly to discover devices
    return devices  # Return the list of discovered devices

def main():
    """Main function to execute the discovery process and print the results."""
    try:
        devices = discover_devices()  # Perform device discovery
        print("Discovered devices:", devices)  # Print the discovered devices
    except ConnectionError as ce:
        print(f"Connection error occurred: {ce}")
    except DiscoveryError as de:
        print(f"Discovery error occurred: {de}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()  # Execute the main function when the script is run
