#!/usr/bin/env python3
# test_discovery.py

from maxsmart import MaxSmartDiscovery  # Import the MaxSmartDiscovery class from the maxsmart module

def discover_devices(ip=None):
    """Discover MaxSmart devices on the network.
    
    Args:
        ip (str): The IP address to discover devices from. Defaults to broadcast address if None.

    Returns:
        list: A list of discovered MaxSmart devices.
    """
    print("Discovering MaxSmart devices...")
    ip = "255.255.255.255"  # Use the default broadcast address for discovery
    devices = MaxSmartDiscovery.discover_maxsmart(ip)  # Call the static method directly to discover devices
    return devices  # Return the list of discovered devices

def main():
    """Main function to execute the discovery process and print the results."""
    devices = discover_devices()  # Perform device discovery
    print(devices)  # Print the discovered devices

if __name__ == "__main__":
    main()  # Execute the main function when the script is run
