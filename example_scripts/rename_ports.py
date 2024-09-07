#!/usr/bin/env python3
# rename_ports.py

import asyncio
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError, StateError, CommandError

async def discover_devices():
    print("Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()
        devices = await discovery.discover_maxsmart()  # Await the async method
        return devices
    except (ConnectionError, DiscoveryError) as e:
        print(f"Error during device discovery: {e}")
        return []

def select_device(devices):
    if not devices:
        print("No devices available.")
        return None
    
    print("Available devices:")
    for i, device in enumerate(devices, 1):
        print(f"{i}. {device['name']} ({device['ip']})")
    
    while True:
        try:
            choice = int(input("Select a device (enter the number): "))
            if 1 <= choice <= len(devices):
                return devices[choice - 1]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_valid_name(port_name, current_name):
    while True:
        new_name = input(f"{port_name} (current: {current_name}): ").strip()
        if not new_name:
            return current_name  # Keep current name if input is empty
        elif len(new_name) > 21:
            print(f"Error: Name '{new_name}' is too long (max 21 characters).")
            if input("Do you want to try again? (y/n): ").lower() != 'y':
                return current_name  # Keep current name if user doesn't want to retry
        else:
            return new_name  # Return the valid new name

async def rename_ports(device):
    # Check if the device version is supported
    if device.version != "1.30":
        print("Renaming ports is not supported for firmware version:", device.version)
        return  # Stop execution if the version is not supported

    # Display the stored port names from the MaxSmartDevice instance
    print("\nCurrent port names:")
    print(f"Strip: {device.strip_name}")  # Use device.strip_name for the strip name
    for i in range(1, 7):  # Ports 1 to 6
        current_name = device.port_names[i - 1] if i - 1 < len(device.port_names) else f"Port {i}"
        print(f"Port {i}: {current_name}")

    new_names = []

    print("\nEnter new names for the strip and its ports (leave blank to keep current name):")
    # Get new name for the strip
    new_strip_name = get_valid_name("Strip", device.strip_name)
    new_names.append((0, new_strip_name))  # Append the strip name change

    for i in range(1, 7):
        current_name = device.port_names[i - 1] if i - 1 < len(device.port_names) else f"Port {i}"
        new_name = get_valid_name(f"Port {i}", current_name)
        new_names.append((i, new_name))

    # Rename ports and confirm the changes
    for port, name in new_names:
        # Only rename if the name has changed
        if port == 0 and name != device.strip_name:  # Check for strip renaming
            try:
                await device.change_port_name(0, name)  # Rename the strip
                print(f"Successfully renamed Strip to '{name}'")
            except (StateError, CommandError) as e:
                print(f"Error renaming Strip: {e}")
        elif port != 0 and name != device.port_names[port - 1]:  # Check for port renaming
            try:
                await device.change_port_name(port, name)  # Rename the port
                print(f"Successfully renamed Port {port} to '{name}'")
            except (StateError, CommandError) as e:
                print(f"Error renaming Port {port}: {e}")

    # Display the updated port names after all renames
    print("\nUpdated port names:")
    print(f"Strip: {device.strip_name}")  # Display updated strip name
    for i in range(1, 7):
        updated_name = device.port_names[i - 1] if i - 1 < len(device.port_names) else f"Port {i}"
        print(f"Port {i}: {updated_name}")

async def main():
    devices = await discover_devices()  # Await the discovery function
    if not devices:
        print("No devices found. Exiting.")
        return

    # Allow the user to select a device from the discovered devices
    selected_device = select_device(devices)
    if not selected_device:
        return

    # Create an instance of MaxSmartDevice with the selected device's IP
    device = MaxSmartDevice(selected_device['ip'])
    await device.initialize_device()  # Ensure the device is initialized after instantiation

    try:
        # Proceed to rename ports
        await rename_ports(device)  # Await the rename function
    finally:
        await device.close()  # Ensure the session is closed

if __name__ == "__main__":
    asyncio.run(main())  # Run the main async function
