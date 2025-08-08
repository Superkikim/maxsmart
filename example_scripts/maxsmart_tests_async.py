#!/usr/bin/env python3
# maxsmart_tests_async.py
"""
MaxSmart Protocol Transparency Test Script - v2.1.0

This script demonstrates the unified API that works seamlessly with both
HTTP and UDP V3 devices. The same methods work regardless of protocol!

Features:
- Automatic protocol detection (HTTP or UDP V3)
- Unified control methods (turn_on, turn_off, check_state, get_data)
- Same robust error handling for both protocols
- Protocol-aware feature availability
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

        # Display raw discovery data
        print("\n" + "="*80)
        print("🔍 RAW DISCOVERY DATA:")
        print("="*80)
        import json
        for i, device in enumerate(devices, 1):
            print(f"\n📱 Device {i} RAW data:")
            print(json.dumps(device, indent=2, default=str))
        print("\n" + "="*80)
        print("🏁 END RAW DISCOVERY DATA")
        print("="*80 + "\n")

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

# Protocol detection is now handled by discovery.py

async def select_device(devices):
    """Allow the user to select a specific device with protocol detection and table format."""
    if not devices:
        print("No devices available for selection.")
        return None

    # Display devices in table format (protocol already detected by discovery)
    print("\n📋 Available MaxSmart Devices:")
    print("=" * 105)
    print(f"{'#':<3} {'Name':<20} {'IP':<15} {'Serial/MAC':<20} {'Firmware':<10} {'Protocol':<10}")
    print("-" * 105)

    device_menu = {}
    for i, device in enumerate(devices, start=1):
        name = device["name"][:19] if len(device["name"]) > 19 else device["name"]
        ip = device["ip"]
        protocol = device.get("protocol", "unknown")
        firmware = device.get("ver", "Unknown")[:9] if device.get("ver") else "Unknown"

        # Show MAC for UDP devices, Serial for HTTP devices
        if protocol == "UDP V3":
            identifier = device.get("mac", "No MAC")[:19]
        else:
            identifier = device.get("sn", "No Serial")[:19]

        device_menu[i] = device
        print(f"{i:<3} {name:<20} {ip:<15} {identifier:<20} {firmware:<10} {protocol:<10}")

    print("=" * 105)

    while True:
        choice = input("\nSelect a device by number: ")
        try:
            choice = int(choice)
            if choice in device_menu:
                return device_menu[choice]
            else:
                print("Invalid choice. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

async def confirm_proceed(device_info):
    """Confirm with the user before proceeding with operations."""
    name = device_info["name"]
    ip = device_info["ip"]
    sn = device_info.get("sn", "Unknown")
    protocol = device_info.get("protocol", "Unknown")

    print(f"\n📱 Selected device: {name}")
    print(f"   IP: {ip}")
    print(f"   Protocol: {protocol}")
    print(f"   Serial: {sn}")
    if protocol == "udp_v3":
        mac = device_info.get("mac", "Unknown")
        print(f"   MAC: {mac}")

    proceed = input("\nContinue with this device? (Y/N, default is Y): ")
    if proceed.strip().lower() not in ("y", ""):
        print("Aborted.")
        return False
    return True

async def select_port(port_mapping, port_count=6):
    """Prompt the user to select a port to test, displaying current port names."""
    print("Available ports:")
    for i in range(1, port_count + 1):
        print(f"Port {i}: {port_mapping.get(f'Port {i}', f'Port {i}')}")

    while True:
        port = input(f"Select a port (1-{port_count}): ")
        try:
            port = int(port)
            if 1 <= port <= port_count:
                return port
            else:
                print(f"Invalid choice. Please select a port number between 1 and {port_count}.")
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

async def check_master_port_state(powerstrip):
    """Check the state of master port (port 0) by checking all individual ports."""
    try:
        all_states = await powerstrip.check_state()  # Get all port states
        all_on = all(state == 1 for state in all_states)
        all_off = all(state == 0 for state in all_states)
        
        if all_on:
            print("Master port (Port 0): All ports are ON")
            return 1
        elif all_off:
            print("Master port (Port 0): All ports are OFF") 
            return 0
        else:
            on_count = sum(all_states)
            print(f"Master port (Port 0): Mixed state - {on_count}/6 ports ON")
            return -1  # Mixed state
    except Exception as e:
        print(f"❌ Error checking master port state: {e}")
        return None

async def power_on_master_port(powerstrip):
    """Power on master port (port 0) and verify all ports are on."""
    print("Powering ON master port (all ports)...")
    try:
        await powerstrip.turn_on(0)
        # Check state to confirm all ports are on
        all_states = await powerstrip.check_state()
        all_on = all(state == 1 for state in all_states)
        
        if all_on:
            print("✅ Master port (Port 0): All ports are now ON")
        else:
            on_count = sum(all_states)
            print(f"⚠️ Master port (Port 0): Only {on_count}/6 ports turned ON")
    except Exception as e:
        print(f"❌ Error powering ON master port: {e}")

async def power_off_master_port(powerstrip):
    """Power off master port (port 0) and verify all ports are off."""
    print("Powering OFF master port (all ports)...")
    try:
        await powerstrip.turn_off(0)
        # Check state to confirm all ports are off
        all_states = await powerstrip.check_state()
        all_off = all(state == 0 for state in all_states)
        
        if all_off:
            print("✅ Master port (Port 0): All ports are now OFF")
        else:
            on_count = sum(all_states)
            print(f"⚠️ Master port (Port 0): {on_count}/6 ports still ON")
    except Exception as e:
        print(f"❌ Error powering OFF master port: {e}")

async def check_port_state(powerstrip, port):
    """Check and display the current state of a port."""
    try:
        if port == 0:
            # Master port - check all individual ports
            return await check_master_port_state(powerstrip)
        else:
            # Individual port
            state = await powerstrip.check_state(port)
            state_text = "ON" if state == 1 else "OFF"
            print(f"Port {port} current state: {state_text}")
            return state
    except Exception as e:
        print(f"❌ Error checking port {port} state: {e}")
        return None

async def power_on_port(powerstrip, port):
    """Power on a specified port and verify state."""
    if port == 0:
        await power_on_master_port(powerstrip)
    else:
        print(f"Powering ON port {port}...")
        try:
            await powerstrip.turn_on(port)
            # Check state to confirm
            state = await powerstrip.check_state(port)
            if state == 1:
                print(f"✅ Port {port} is now ON")
            else:
                print(f"❌ Port {port} failed to turn ON (state: {state})")
        except Exception as e:
            print(f"❌ Error while attempting to power ON port {port}: {e}")

async def power_off_port(powerstrip, port):
    """Power off a specified port and verify state."""
    if port == 0:
        await power_off_master_port(powerstrip)
    else:
        print(f"Powering OFF port {port}...")
        try:
            await powerstrip.turn_off(port)
            # Check state to confirm
            state = await powerstrip.check_state(port)
            if state == 0:
                print(f"✅ Port {port} is now OFF")
            else:
                print(f"❌ Port {port} failed to turn OFF (state: {state})")
        except Exception as e:
            print(f"❌ Error while attempting to power OFF port {port}: {e}")

async def retrieve_consumption_data(selected_strip):
    """Retrieve real-time consumption data for each port and return it."""
    consumption_data = []
    try:
        port_mapping = await selected_strip.retrieve_port_names()  # Make this call async
        # Use actual port count instead of hardcoded 6
        for port in range(1, selected_strip.port_count + 1):
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
    
    # Get data for all ports (port 0 = sum of all ports)
    try:
        if data_type == 'hourly':
            all_ports_data = await powerstrip.get_statistics(0, 0)
        elif data_type == 'daily':
            all_ports_data = await powerstrip.get_statistics(0, 1)
        elif data_type == 'monthly':
            all_ports_data = await powerstrip.get_statistics(0, 2)
        else:
            raise ValueError(f"Invalid data type: {data_type}")
    except Exception as e:
        print(f"Error retrieving {data_type} data: {e}")
        return None, None
    
    # Get individual port data
    individual_ports_data = []
    for port in range(1, 7):  # Ports 1 to 6
        try:
            if data_type == 'hourly':
                port_data = await powerstrip.get_statistics(port, 0)
            elif data_type == 'daily':
                port_data = await powerstrip.get_statistics(port, 1)
            elif data_type == 'monthly':
                port_data = await powerstrip.get_statistics(port, 2)
            
            individual_ports_data.append(port_data['watt'])
        except Exception as e:
            print(f"Error retrieving {data_type} data for port {port}: {e}")
            individual_ports_data.append([0] * len(all_ports_data['watt']))  # Fill with zeros
    
    # Structure the data for plotting
    structured_data = {
        'watt': all_ports_data['watt'],  # Total consumption
        'year': all_ports_data['year'],
        'month': all_ports_data['month'],
        'day': all_ports_data['day'],
        'hour': all_ports_data['hour'],
        'cost': all_ports_data.get('cost', 0),
        'currency': all_ports_data.get('currency', '$')
    }
    
    # Add individual port data
    for i, port_data in enumerate(individual_ports_data, 1):
        structured_data[f'watt_{i}'] = port_data
    
    return structured_data, {
        'year': all_ports_data['year'],
        'month': all_ports_data['month'],
        'day': all_ports_data['day'],
        'hour': all_ports_data['hour']
    }

async def retrieve_hourly_data(powerstrip):
    return await retrieve_time_based_data(powerstrip, 'hourly')

async def retrieve_daily_data(powerstrip):
    return await retrieve_time_based_data(powerstrip, 'daily')

async def retrieve_monthly_data(powerstrip):
    return await retrieve_time_based_data(powerstrip, 'monthly')

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

def get_units_and_divisor(firmware_version, data_type):
    """Get appropriate units and divisor based on firmware version."""
    if firmware_version == "1.30":
        # v1.30 returns watts
        if data_type == 'hourly':
            return "W", 1
        elif data_type == 'daily':
            return "kWh", 1000  # Convert W to kWh for daily
        elif data_type == 'monthly':
            return "kWh", 1000  # Convert W to kWh for monthly
    else:
        # v2.11+ returns kWh
        return "kWh", 1

def plot_chandelle_diagram(port_mapping, data, data_type, firmware_version):
    """Plot consumption data with proper units based on firmware version."""
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Get units and divisor
    units, divisor = get_units_and_divisor(firmware_version, data_type)
    
    num_data_points = len(data['watt'])
    x = np.arange(num_data_points)
    width = 0.35
    
    # Plot data for total consumption (all ports)
    total_data = [val / divisor for val in data['watt']]
    ax.bar(x - width/2, total_data, width, label='Total', color='blue', alpha=0.7)
    
    # Plot stacked data for individual ports 1-6
    bottom = np.zeros(num_data_points)
    colors = ['red', 'green', 'orange', 'purple', 'brown', 'pink']
    
    for i in range(1, 7):
        port_key = f'watt_{i}'
        if port_key in data:
            port_data = [val / divisor for val in data[port_key]]
            port_name = port_mapping.get(f'Port {i}', f'Port {i}')
            ax.bar(x + width/2, port_data, width, bottom=bottom, 
                   label=port_name, color=colors[i-1], alpha=0.7)
            bottom += np.array(port_data)
    
    # Set labels and title based on data type
    ax.set_ylabel(f'Consumption ({units})')
    
    if data_type == 'hourly':
        end_time = datetime(data['year'], data['month'], data['day'], data['hour'])
        hours = [(end_time - timedelta(hours=23-i)).strftime('%H:00') for i in range(24)]
        ax.set_xticks(x)
        ax.set_xticklabels(hours, rotation=45, ha='right')
        title = f"Hourly consumption data ending on {end_time.strftime('%d %B %Y at %H:00')}"
    elif data_type == 'daily':
        end_date = datetime(data['year'], data['month'], data['day'])
        days = [(end_date - timedelta(days=29-i)).strftime('%d %b') for i in range(30)]
        ax.set_xticks(x)
        ax.set_xticklabels(days, rotation=45, ha='right')
        title = f"Daily consumption data ending on {end_date.strftime('%d %B %Y')}"
    elif data_type == 'monthly':
        end_month = datetime(data['year'], data['month'], 1)
        months = [(end_month - timedelta(days=30*i)).strftime('%b %Y') for i in range(11, -1, -1)]
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45, ha='right')
        title = f"Monthly consumption data ending on {end_month.strftime('%B %Y')}"
    
    # Add firmware version and cost info to title
    fw_info = f" (FW: {firmware_version})"
    if 'cost' in data and 'currency' in data and data['cost'] > 0:
        cost_info = f" - Cost: {data['cost']} {data['currency']}/kWh"
        title += fw_info + cost_info
    else:
        title += fw_info
    
    ax.set_title(title)
    ax.legend(title='Ports', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
      
async def main():
    selected_strip = None
    try:
        """Main function to run all tests."""
        devices = await discover_devices()  # Discover MaxSmart devices
        if devices:
            print("Available MaxSmart devices:")
            selected_device = await select_device(devices)  # Allow the user to select a device
            
            if not await confirm_proceed(selected_device):
                return
            
            # Create device with all info from discovery
            protocol = selected_device.get("protocol", "http")
            serial = selected_device.get("sn", "")
            selected_strip = MaxSmartDevice(selected_device["ip"], protocol=protocol, sn=serial)

            # Pre-populate device info from discovery to avoid re-discovery
            selected_strip.version = selected_device.get("ver", None)
            selected_strip.name = selected_device.get("name", None)
            selected_strip.port_count = selected_device.get("nr_of_ports", 6)  # Use detected port count

            await selected_strip.initialize_device()  # Initialize with pre-detected protocol

            # Display protocol and device information
            print(f"\n🔗 Connected to {selected_strip.name or 'Unknown Device'}")
            print(f"   Protocol: {selected_strip.protocol.upper()}")
            print(f"   Firmware: {selected_strip.version or 'Unknown'}")
            print(f"   IP: {selected_device['ip']}")
            print(f"   MAC: {selected_device.get('mac', 'Unknown')}")
            print(f"   Serial: {selected_strip.sn or 'Unknown'}")

            port_mapping = await selected_strip.retrieve_port_names()  # Retrieve current port names
            firmware_version = selected_strip.version  # Get firmware version

            # Test menu - all methods work with both HTTP and UDP V3 protocols
            print(f"\n🧪 Protocol Transparency Demo")
            print(f"   All methods below work seamlessly with {selected_strip.protocol.upper()} protocol!")

            while True:
                try:
                    print("\nWhat would you like to test?")
                    print("1. Port Control (Turn ON/OFF) - ✅ HTTP & UDP V3")
                    print("2. Master Port Control (Turn all ON/OFF) - ✅ HTTP & UDP V3")
                    print("3. Real-time Consumption Data - ✅ HTTP & UDP V3")

                    # Show all options - module will handle version restrictions
                    if selected_strip.protocol == 'http':
                        print("4. Statistics and Graphs (Hourly/Daily/Monthly) - ✅ HTTP only")
                        print("5. Raw Statistics Data - ✅ HTTP only")
                    else:
                        print("4. Statistics and Graphs - ❌ Not available on UDP V3")
                        print("5. Raw Statistics Data - ❌ Not available on UDP V3")

                    print("6. Exit")

                    choice = input("Select an option (1-6): ")
                    
                    if choice == "1":
                        # Port control testing
                        port = await select_port(port_mapping, selected_strip.port_count)  # Get the port number from the user
                        
                        # First, check current state
                        print(f"\nChecking current state of port {port}...")
                        current_state = await check_port_state(selected_strip, port)
                        
                        if current_state is not None:
                            action = await select_power_action()  # Ask user for the action they want to perform
                            
                            if action == "1":  # Power ON
                                await power_on_port(selected_strip, port)
                            else:  # Power OFF
                                await power_off_port(selected_strip, port)
                        
                        input("\nPress Enter to continue...")  # Pause before returning to menu
                    
                    elif choice == "2":
                        # Testing Master port operations
                        print("Master Port Control - Controls all 6 ports simultaneously")
                        
                        # First, check current state
                        print("Checking current state of master port (Port 0)...")
                        current_state = await check_port_state(selected_strip, 0)
                        
                        if current_state is not None:
                            action = await select_power_action()  # Ask user for the action they want to perform
                            
                            if action == "1":  # Power ON
                                await power_on_port(selected_strip, 0)
                            else:  # Power OFF
                                await power_off_port(selected_strip, 0)
                            
                            # Display consumption data after the operation
                            print("\nConsumption data after operation:")
                            consumption_data = await retrieve_consumption_data(selected_strip)
                            display_table(["Port Name", "Watt"], consumption_data)
                        
                        input("\nPress Enter to continue...")  # Pause before returning to menu
                    
                    elif choice == "3":
                        # Real-time consumption data
                        print("Current real-time consumption data:")
                        consumption_data = await retrieve_consumption_data(selected_strip)
                        display_table(["Port Name", "Watt"], consumption_data)
                        input("\nPress Enter to continue...")  # Pause before returning to menu
                    
                    elif choice == "4":
                        # Statistics and graphs (HTTP only) - module handles version check
                        if selected_strip.protocol != 'http':
                            print("❌ Statistics are only available on HTTP devices")
                            print("   Your device uses UDP V3 protocol which supports:")
                            print("   ✅ Port control (turn_on, turn_off)")
                            print("   ✅ State checking (check_state)")
                            print("   ✅ Real-time consumption (get_power_data)")
                            input("\nPress Enter to continue...")
                            continue

                        from maxsmart.const import IN_DEVICE_NAME_VERSION
                        if selected_strip.version != IN_DEVICE_NAME_VERSION:
                            print(f"❌ Statistics not available (requires firmware v{IN_DEVICE_NAME_VERSION}; current: {selected_strip.version or 'Unknown'})")
                            print("   Available features: 1) Port control, 2) Master control, 3) Real-time consumption")
                            input("\nPress Enter to continue...")
                            continue

                        try:
                            print("Displaying statistics and graphs...")

                            # Hourly data
                            print("Displaying last 24 hours wattage for each port")
                            hourly_data, hourly_date_info = await retrieve_hourly_data(selected_strip)
                            if hourly_data and hourly_date_info:
                                plot_chandelle_diagram(port_mapping, hourly_data, 'hourly', firmware_version)
                            else:
                                print("No hourly data available")

                            # Daily data
                            print("Displaying daily wattage for each port")
                            daily_data, daily_date_info = await retrieve_daily_data(selected_strip)
                            if daily_data and daily_date_info:
                                plot_chandelle_diagram(port_mapping, daily_data, 'daily', firmware_version)
                            else:
                                print("No daily data available")

                            # Monthly data
                            print("Displaying monthly wattage for each port")
                            monthly_data, monthly_date_info = await retrieve_monthly_data(selected_strip)
                            if monthly_data and monthly_date_info:
                                plot_chandelle_diagram(port_mapping, monthly_data, 'monthly', firmware_version)
                            else:
                                print("No monthly data available")

                            input("\nPress Enter to continue...")  # Pause before returning to menu

                        except Exception as e:
                            # Handle version restriction or other errors cleanly
                            error_msg = str(e)
                            if "firmware v" in error_msg:
                                print(f"\n❌ {error_msg}")
                                print("   Available features for your device:")
                                print("   ✅ Port control (options 1-2)")
                                print("   ✅ Real-time consumption (option 3)")
                            else:
                                print(f"\n❌ Error accessing statistics: {error_msg}")
                            input("\nPress Enter to continue...")
                    
                    elif choice == "5":
                        # Raw statistics data (HTTP only) - module handles version check
                        if selected_strip.protocol != 'http':
                            print("❌ Raw statistics are only available on HTTP devices")
                            print("   UDP V3 devices support real-time data only (option 3)")
                            input("\nPress Enter to continue...")
                            continue

                        from maxsmart.const import IN_DEVICE_NAME_VERSION
                        if selected_strip.version != IN_DEVICE_NAME_VERSION:
                            print(f"❌ Raw statistics not available (requires firmware v{IN_DEVICE_NAME_VERSION}; current: {selected_strip.version or 'Unknown'})")
                            print("   Available features: 1) Port control, 2) Master control, 3) Real-time consumption")
                            input("\nPress Enter to continue...")
                            continue

                        try:
                            await test_data_retrieval(selected_strip)
                            input("\nPress Enter to continue...")  # Pause before returning to menu
                        except Exception as e:
                            # Handle version restriction or other errors cleanly
                            error_msg = str(e)
                            if "firmware v" in error_msg:
                                print(f"\n❌ {error_msg}")
                                print("   Available features for your device:")
                                print("   ✅ Port control (options 1-2)")
                                print("   ✅ Real-time consumption (option 3)")
                            else:
                                print(f"\n❌ Error accessing raw statistics: {error_msg}")
                            input("\nPress Enter to continue...")
                    
                    elif choice == "6":
                        print("Exiting...")
                        break
                    
                    else:
                        print("Invalid choice. Please select 1-6.")
                
                except KeyboardInterrupt:
                    print("\n\nOperation interrupted by user (Ctrl+C)")
                    break
                except EOFError:
                    print("\n\nInput interrupted by user")
                    break
                        
        else:
            print("No MaxSmart devices found.")  # Handle case where no devices are discovered

    except KeyboardInterrupt:
        print("\n\nAborted by user (Ctrl+C)")
    except EOFError:
        print("\n\nInput interrupted by user")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always clean up the device connection
        if selected_strip:
            try:
                await selected_strip.close()
            except:
                pass  # Ignore cleanup errors

if __name__ == "__main__":
    asyncio.run(main())  # Execute the main function within an asyncio event loop