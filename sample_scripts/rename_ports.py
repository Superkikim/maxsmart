#!/usr/bin/env python3
# rename_ports.py

from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError, StateError, CommandError

def discover_devices():
    print("Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()
        return discovery.discover_maxsmart()
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

def rename_ports(device):
    port_mapping = device.retrieve_port_names()
    new_names = []

    print("\nEnter new names for the strip and its ports (leave blank to keep current name):")
    for i in range(7):
        port_name = "Strip" if i == 0 else f"Port {i}"
        current_name = port_mapping.get(f"Port {i}", port_name)
        new_name = get_valid_name(port_name, current_name)
        new_names.append((i, new_name))

    for port, name in new_names:
        if name != port_mapping.get(f"Port {port}", f"Port {port}"):
            try:
                device.change_port_name(port, name)
                print(f"Successfully renamed Port {port} to '{name}'")
            except (StateError, CommandError) as e:
                print(f"Error renaming Port {port}: {e}")

def main():
    devices = discover_devices()
    if not devices:
        print("No devices found. Exiting.")
        return

    selected_device = select_device(devices)
    if not selected_device:
        return

    device = MaxSmartDevice(selected_device['ip'])
    rename_ports(device)

if __name__ == "__main__":
    main()
