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
import asyncio, json, calendar
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

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

async def test_data_retrieval(device):
    print("\nTesting Hourly Data:")
    hourly_data = await device.get_statistics(0, 0)  # port 0, hourly
    print(json.dumps(hourly_data, indent=2))
    
    # Process hourly data (keeping this as is)
    current_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    hour_labels = [(current_time - timedelta(hours=23-i)).strftime('%H:00') for i in range(24)]
    print("\nHourly Data Interpretation:")
    for i, (label, watt) in enumerate(zip(hour_labels, hourly_data['watt'])):
        print(f"{label}: {watt:.2f} W {'(incomplete)' if i == 23 else ''}")

    print("\nTesting Daily Data:")
    daily_data = await device.get_statistics(0, 1)  # port 0, daily
    print(json.dumps(daily_data, indent=2))
    
    # Process daily data
    current_date = datetime.now().date()
    day_labels = [(current_date - timedelta(days=29-i)).strftime('%Y-%m-%d') for i in range(30)]
    print("\nDaily Data Interpretation:")
    for i, (label, watt) in enumerate(zip(day_labels, daily_data['watt'])):
        print(f"{label}: {watt/1000:.3f} kWh {'(incomplete)' if i == 29 else ''}")

    print("\nTesting Monthly Data:")
    monthly_data = await device.get_statistics(0, 2)  # port 0, monthly
    print(json.dumps(monthly_data, indent=2))
    
    # Process monthly data
    current_month = datetime.now().replace(day=1)
    month_labels = [(current_month - timedelta(days=30*i)).strftime('%b %Y') for i in range(11, -1, -1)]
    print("\nMonthly Data Interpretation:")
    for i, (label, watt) in enumerate(zip(month_labels, monthly_data['watt'])):
        print(f"{label}: {watt/1000:.3f} kWh {'(incomplete)' if i == 11 else ''}")   
                 
async def retrieve_time_based_data(powerstrip, data_type):
    """Retrieve hourly, daily, or monthly data for the strip."""
    print(f"Retrieving {data_type} consumption data...")
    data = []
    date_info = None
    for port in range(7):  # 0 to 6
        try:
            if data_type == 'hourly':
                port_data = await powerstrip.get_statistics(port, 0)
            elif data_type == 'daily':
                port_data = await powerstrip.get_statistics(port, 1)
            elif data_type == 'monthly':
                port_data = await powerstrip.get_statistics(port, 2)
            else:
                raise ValueError(f"Invalid data type: {data_type}")
            
            data.append(port_data['watt'])
            if date_info is None:
                date_info = {
                    'year': port_data['year'],
                    'month': port_data['month'],
                    'day': port_data['day'],
                    'hour': port_data['hour']
                }
                print(f"Retrieved date_info for {data_type}: {date_info}")  # Debug print
        except Exception as e:
            print(f"Error retrieving {data_type} data for port {port}: {e}")
            data.append([])
    return data, date_info

async def retrieve_hourly_data(powerstrip):
    return await retrieve_time_based_data(powerstrip, 'hourly')

async def retrieve_daily_data(powerstrip):
    return await retrieve_time_based_data(powerstrip, 'daily')

async def retrieve_monthly_data(powerstrip):
    return await retrieve_time_based_data(powerstrip, 'monthly')

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

def plot_chandelle_diagram(port_mapping, data, data_type):
    fig, ax = plt.subplots(figsize=(15, 8))
    
    num_data_points = len(data['watt'])
    x = np.arange(num_data_points)
    width = 0.35
    
    # Plot data for port 0
    ax.bar(x - width/2, data['watt'], width, label=port_mapping['Port 0'], color='blue', alpha=0.7)
    
    # Plot stacked data for ports 1-6
    bottom = np.zeros(num_data_points)
    for i in range(1, 7):
        ax.bar(x + width/2, data[f'watt_{i}'], width, bottom=bottom, label=port_mapping[f'Port {i}'], alpha=0.7)
        bottom += np.array(data[f'watt_{i}'])
    
    if data_type == 'hourly':
        ax.set_ylabel('Consumption (W)')
        end_time = datetime(data['year'], data['month'], data['day'], data['hour'])
        hours = [(end_time - timedelta(hours=23-i)).strftime('%H:00') for i in range(24)]
        ax.set_xticks(x)
        ax.set_xticklabels(hours, rotation=45, ha='right')
        title = f"Hourly consumption data ending on {end_time.strftime('%d %B %Y at %H:00')}"
    elif data_type == 'daily':
        ax.set_ylabel('Consumption (kWh)')
        end_date = datetime(data['year'], data['month'], data['day'])
        days = [(end_date - timedelta(days=29-i)).strftime('%d %b') for i in range(30)]
        ax.set_xticks(x)
        ax.set_xticklabels(days, rotation=45, ha='right')
        title = f"Daily consumption data ending on {end_date.strftime('%d %B %Y')}"
        # Convert W to kWh
        ax.set_yticklabels([f'{y/1000:.1f}' for y in ax.get_yticks()])
    elif data_type == 'monthly':
        ax.set_ylabel('Consumption (kWh)')
        end_month = datetime(data['year'], data['month'], 1)
        months = [(end_month - timedelta(days=30*i)).strftime('%b %Y') for i in range(11, -1, -1)]
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45, ha='right')
        title = f"Monthly consumption data ending on {end_month.strftime('%B %Y')}"
        # Convert W to kWh
        ax.set_yticklabels([f'{y/1000:.1f}' for y in ax.get_yticks()])
    
    ax.set_title(title)
    ax.legend(title='Ports', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
      
async def main():
    try:
        """Main function to run all tests."""
        devices = await discover_devices()  # Discover MaxSmart devices
        if devices:
            print("Available MaxSmart devices:")
            selected_device = await select_device(devices)  # Allow the user to select a device
            
            if not await confirm_proceed(selected_device["name"], selected_device["ip"], selected_device["sn"]):
                return
            
            selected_strip = MaxSmartDevice(selected_device["ip"])  # Create instance for the selected strip
            
            port_mapping = await selected_strip.retrieve_port_names()  # Retrieve current port names

            '''
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
            '''

            # Hourly data
            print("Displaying last 24 hours wattage for each port")
            hourly_data, hourly_date_info = await retrieve_hourly_data(selected_strip)
            if hourly_data and hourly_date_info:
                await plot_chandelle_diagram(port_mapping, hourly_data, 'hourly')
            else:
                print("No hourly data available")

            # Daily data
            print("Displaying daily wattage for each port")
            daily_data, daily_date_info = await retrieve_daily_data(selected_strip)
            if daily_data and daily_date_info:
                await plot_chandelle_diagram(port_mapping, daily_data, 'daily')
            else:
                print("No daily data available")

            # Monthly data
            print("Displaying monthly wattage for each port")
            monthly_data, monthly_date_info = await retrieve_monthly_data(selected_strip)
            if monthly_data and monthly_date_info:
                await plot_chandelle_diagram(port_mapping, monthly_data, 'monthly')
            else:
                print("No monthly data available")
        else:
            print("No MaxSmart devices found.")  # Handle case where no devices are discovered

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    finally:
        # This ensures that the session is closed even if an exception occurs
        if 'selected_strip' in locals():
            await selected_strip.close()

if __name__ == "__main__":
    asyncio.run(main())  # Execute the main function within an asyncio event loop

