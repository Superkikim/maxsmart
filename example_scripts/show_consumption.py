#!/usr/bin/env python3
# show_consumption.py

import asyncio
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError

async def discover_devices():
    """Discover MaxSmart devices on the network."""
    print("Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()
        devices = await discovery.discover_maxsmart()  # NOW ASYNC!
        return devices
    except ConnectionError as ce:
        print(f"Connection error occurred during discovery: {ce}")
    except DiscoveryError as de:
        print(f"Discovery error occurred: {de}")
    except Exception as e:
        print(f"An unexpected error occurred during discovery: {e}")
    return []

def select_device(devices):
    """Allow the user to select a specific device."""
    if not devices:
        print("No devices available for selection.")
        return None

    for i, device in enumerate(devices, start=1):
        print(f"{i}. Name: {device['name']}, IP: {device['ip']}")

    while True:
        choice = input("Select a device by number: ")
        try:
            choice = int(choice)
            if 1 <= choice <= len(devices):
                return devices[choice - 1]
            else:
                print("Invalid choice. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

async def retrieve_consumption_data(device):
    """Retrieve real-time consumption data for each port."""
    consumption_data = []
    try:
        port_mapping = await device.retrieve_port_names()  # NOW ASYNC!
        for port in range(1, 7):
            power_data = await device.get_power_data(port)  # NOW ASYNC!
            watt_value = float(power_data["watt"])
            consumption_data.append([port_mapping[f"Port {port}"], watt_value])
    except Exception as e:
        print(f"Error retrieving consumption data: {e}")
    return consumption_data

def display_table(header, data):
    """Display data in a formatted table."""
    max_widths = [max(len(str(row[i])) for row in data + [header]) for i in range(len(header))]
    
    header_format = " | ".join(f"{{:<{w}}}" for w in max_widths)
    print(header_format.format(*header))
    print("-" * sum(max_widths + [len(max_widths) - 1]))
    
    row_format = " | ".join(f"{{:<{w}}}" for w in max_widths)
    for row in data:
        print(row_format.format(row[0], f"{row[1]:.2f}"))

async def main():
    """Main function - now async!"""
    device = None
    
    try:
        devices = await discover_devices()  # NOW ASYNC!
        if not devices:
            print("No MaxSmart devices found.")
            return

        selected_device = select_device(devices)
        if not selected_device:
            return

        print(f"\nSelected device: {selected_device['name']} (IP: {selected_device['ip']})")
        device = MaxSmartDevice(selected_device['ip'])
        
        # Initialize device - REQUIRED for new version!
        await device.initialize_device()

        consumption_data = await retrieve_consumption_data(device)  # NOW ASYNC!
        if consumption_data:
            print("\nCurrent Consumption Data:")
            display_table(["Port Name", "Watt"], consumption_data)
        else:
            print("Unable to retrieve consumption data.")
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if device:
            try:
                await device.close()  # REQUIRED cleanup!
                print("Device closed successfully")
            except Exception as e:
                print(f"Error closing device: {e}")

if __name__ == "__main__":
    asyncio.run(main())  # RUN WITH ASYNCIO!