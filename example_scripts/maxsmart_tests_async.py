#!/usr/bin/env python3
# maxsmart_tests_async.py
"""
This script discovers MaxSmart devices, allows the user to select a specific device,
and tests control operations on the power strip by cycling selected port states.
"""
"""
This script requires the following modules:
- matplotlib
Please install them using pip:
pip install -r requirements.txt
"""
import asyncio
import time
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError
import matplotlib.pyplot as plt

async def discover_devices():
    """Discover MaxSmart devices on the network."""
    print("Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()
        devices = await discovery.discover_maxsmart()  # Make this call async
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

async def select_device(devices):
    """Allow the user to select a specific device."""
    if not devices:
        print("No devices available for selection.")
        return None

    device_menu = {}
    for i, device in enumerate(devices, start=1):
        sn = device["sn"]
        name = device["name"]
        ip = device["ip"]
        device_menu[i] = device
        print(f"{i}. SN: {sn}, Name: {name}, IP: {ip}")

    while True:
        choice = input("Select a device by number: ")
        try:
            choice = int(choice)
            if choice in device_menu:
                return device_menu[choice]
            else:
                print("Invalid choice. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

async def confirm_proceed(name, ip, sn):
    """Confirm with the user before proceeding with operations."""
    print("WARNING: This test will power down all devices plugged into the power strip.")
    print(f"Name: {name}, IP: {ip}, SN: {sn}")
    proceed = input("Do you want to proceed? (Y/N, default is Y): ")
    if proceed.strip().lower() not in ("y", ""):
        print("Test aborted.")
        return False
    return True

async def select_port(port_mapping):
    """Prompt the user to select a port (1 to 6) to test, displaying current port names."""
    print("Available ports:")
    for i in range(1, 7):
        print(f"Port {i}: {port_mapping.get(f'Port {i}', f'Port {i}')}")
    
    while True:
        port = input("Select a port (1-6): ")
        try:
            port = int(port)
            if 1 <= port <= 6:
                return port
            else:
                print("Invalid choice. Please select a port number between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")

async def select_power_action():
    """Prompt the user to select whether to power on or off the port."""
    while True:
        action = input("Would you like to (1) Power ON or (2) Power OFF the port? (Enter 1 or 2): ")
        if action in ("1", "2"):
            return action
        else:
            print("Invalid choice. Please enter 1 to power ON or 2 to power OFF.")

async def power_on_port(powerstrip, port):
    """Power on a specified port."""
    print(f"Powering ON port {port}...")
    try:
        await powerstrip.turn_on(port)  # Make turn_on async
    except Exception as e:
        print(f"Error while attempting to power ON port {port}: {e}")

async def power_off_port(powerstrip, port):
    """Power off a specified port and wait 15 seconds."""
    print(f"Powering OFF port {port}...")
    try:
        await powerstrip.turn_off(port)  # Make turn_off async
    except Exception as e:
        print(f"Error while attempting to power OFF port {port}: {e}")

async def check_state(selected_device, port):
    """Check the state of the specified port using the selected_device instance."""
    return await selected_device.check_port_state(port)  # Make this call async

async def retrieve_consumption_data(selected_strip):
    """Retrieve real-time consumption data for each port and return it."""
    consumption_data = []
    try:
        port_mapping = await selected_strip.retrieve_port_names()  # Make this call async
        for port in range(1, 7):
            power_data = await selected_strip.get_power_data(port)  # Make this call async
            watt_value = float(power_data["watt"])  # Ensure watt value is a float
            consumption_data.append([port_mapping[f"Port {port}"], watt_value])  # Append real port names and wattage
    except Exception as e:
        print(f"Error retrieving consumption data: {e}")
    return consumption_data

async def retrieve_hourly_data(powerstrip):
    """Retrieve hourly data for ports and return it as a list of lists."""
    print("Retrieving hourly consumption data...")
    hourly_data = []
    for port in range(1, 7):
        try:
            data = await powerstrip.get_hourly_data(port)  # Make this call async
            if data:
                hourly_data.append([float(d) for d in data if isinstance(d, (int, float, str)) and d.replace('.', '', 1).isdigit()])
            else:
                hourly_data.append([])
        except Exception as e:
            print(f"Error retrieving hourly data for port {port}: {e}")
            hourly_data.append([])
    return hourly_data

async def countdown(seconds):
    """Display a countdown timer."""
    for i in range(seconds, 0, -1):
        print(f"Countdown: {i} seconds remaining ", end='\r')
        await asyncio.sleep(1)  # Use asyncio.sleep to keep it non-blocking
    print("                                 ", end='\r')

def display_table(header, data):
    """Display data in a formatted table."""
    max_widths = [len(header[0]), len(header[1])]
    for row in data:
        max_widths[0] = max(max_widths[0], len(row[0]))
        max_widths[1] = max(max_widths[1], len(f"{row[1]:.2f}"))
    
    header_format = " | ".join(f"{{:<{max_widths[i]}}}" for i in range(len(header)))
    print(header_format.format(*header))
    print("-" * (sum(max_widths) + len(max_widths) + 1))
    
    row_format = " | ".join(f"{{:<{max_widths[i]}}}" for i in range(len(header)))
    for row in data:
        watt_value = f"{row[1]:.2f}"
        if row[1] < 10:
            watt_value = " " + watt_value
        print(row_format.format(row[0], watt_value))

def plot_vectorial_graph(port_mapping, data):
    """Create and display the plot in a non-blocking way and wait for user input to continue."""
    fig, ax = plt.subplots(figsize=(12, 6), num=f"Hourly Consumption Data per Port for {port_mapping['Port 0']}")

    hours = list(range(1, 25))
    for port_idx in range(1, 7):
        if data[port_idx - 1]:
            ax.plot(hours, data[port_idx - 1], label=port_mapping[f'Port {port_idx}'], marker='o')
        else:
            print(f"No data available for {port_mapping[f'Port {port_idx}']}")

    ax.set_title("Hourly Consumption Data per Port")
    ax.set_xlabel("Hours (1-24)")
    ax.set_ylabel("Consumption (W)")
    ax.set_xticks(hours)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    plt.show(block=False)

    input("Press Enter to continue...")
    plt.close(fig)

async def main():
    """Main function to run all tests."""
    devices = await discover_devices()  # Discover MaxSmart devices
    if devices:
        print("Available MaxSmart devices:")
        selected_device = await select_device(devices)  # Allow the user to select a device
        
        if not await confirm_proceed(selected_device["name"], selected_device["ip"], selected_device["sn"]):
            return
        
        selected_strip = MaxSmartDevice(selected_device["ip"])  # Create instance for the selected strip
        
        port_mapping = await selected_strip.retrieve_port_names()  # Retrieve current port names
        
        print(port_mapping)
        port = await select_port(port_mapping)  # Get the port number from the user
        action = await select_power_action()  # Ask user for the action they want to perform
        
        if action == "1":  # Power ON
            await power_on_port(selected_strip, port)  # Power ON the specified port
            await countdown(10)  # Countdown after powering ON
            await power_off_port(selected_strip, port)  # Power OFF the specified port
            await countdown(10)  # Countdown after powering OFF
        else:  # Power OFF
            await power_off_port(selected_strip, port)  # Power OFF the specified port
            await countdown(10)  # Countdown after powering OFF
            await power_on_port(selected_strip, port)  # Power ON the specified port
            await countdown(10)  # Countdown after powering ON
            
        # Testing Master port operations
        print("WARNING: Turning off the master port (Port 0) will power off all devices plugged into the power strip.")
        
        proceed = input("Do you want to proceed? (Y/N): ")
        if proceed.lower() != "y":
            print("Operation aborted.")
        else:
            await power_off_port(selected_strip, 0)  # Power OFF the master port (and all connected devices)
            await countdown(10)  
            
            # Display consumption data after turning off
            print("Consumption data after powering OFF:")
            consumption_data = await retrieve_consumption_data(selected_strip)  # Retrieve consumption data
            display_table(["Port Name", "Watt"], consumption_data)  # Display the table with consumption data
            
            await power_on_port(selected_strip, 0)  # Power ON the master port (restoring power)
            await countdown(10)  
            
            # Display consumption data after turning on
            print("Consumption data after powering ON:")
            consumption_data = await retrieve_consumption_data(selected_strip)  # Retrieve consumption data again
            display_table(["Port Name", "Watt"], consumption_data)  # Display the table with consumption data
            
            # Display last 24 hours wattage for each port
            print("Displaying last 24 hours wattage for each port")
            hourly_data = await retrieve_hourly_data(selected_strip)  # Get hourly data
            
            # Display hourly data graph
            await plot_vectorial_graph(port_mapping, hourly_data)  # Plot the vectorial graph
    else:
        print("No MaxSmart devices found.")  # Handle case where no devices are discovered

if __name__ == "__main__":
    asyncio.run(main())  # Execute the main function within an asyncio event loop
