#!/usr/bin/env python3
# get_port_names_async.py

import asyncio
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError  # Import the custom exceptions

async def discover_devices():
    """Discover MaxSmart devices and return a list of devices."""
    print("Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()  # Create a MaxSmartDiscovery instance
        devices = await discovery.discover_maxsmart()  # Discover devices asynchronously
        return devices  # Return the list of discovered devices
    except ConnectionError as ce:
        print(f"Connection error occurred during device discovery: {ce}")
        return []  # Return an empty list if discovery fails
    except DiscoveryError as de:
        print(f"Discovery error occurred: {de}")
        return []  # Return an empty list if there was a discovery issue
    except Exception as e:
        print(f"An unexpected error occurred during device discovery: {e}")
        return []  # Return an empty list if an unexpected error occurs

async def select_device(devices):
    """Prompt the user to select a device from the discovered devices."""
    print("Available MaxSmart devices:")
    for i, device in enumerate(devices, start=1):
        print(f"{i}. IP: {device['ip']}, Name: {device['name']}")  # List device IP and name
    choice = input("Select a device by number: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(devices):
            return devices[choice - 1]  # Return the selected device
        else:
            print("Invalid choice. Please select a number from the list.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

async def main():
    """Main function to execute the device selection process and retrieve port names."""
    # Discover devices
    devices = await discover_devices()
    # Check if any devices were found
    if not devices:
        print("No MaxSmart devices found.")
        return
    # Select a device
    selected_device = await select_device(devices)
    if selected_device:
        ip = selected_device["ip"]  # Get the IP address of the selected device
        device = MaxSmartDevice(ip=ip)  # Create an instance of MaxSmartDevice
        # Retrieve the current port names
        try:
            port_mapping = await device.retrieve_port_names()  # Get a dictionary of port names asynchronously
            print("Port Names:")
            for port, name in port_mapping.items():
                print(f"{port}: {name}")  # Output each port name
        except Exception as e:
            print(f"Error retrieving port names: {str(e)}")
        finally:
            await device.close()  # Ensure to close the session

if __name__ == "__main__":
    asyncio.run(main())  # Execute the main function using asyncio
