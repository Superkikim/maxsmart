#!/usr/bin/env python3
# maxsmart_tests_async.py
"""
Enhanced MaxSmart test script with dual protocol support (HTTP + UDP V3).

This script discovers MaxSmart devices, allows the user to select a specific device,
and tests control operations with full user control over which ports to test.
"""
import asyncio, json, calendar
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

async def discover_devices():
    """Discover MaxSmart devices on the network with protocol detection."""
    print("Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()
        devices = await discovery.discover_maxsmart()  # Now includes protocol detection
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
    """Allow the user to select a specific device with protocol information."""
    if not devices:
        print("No devices available for selection.")
        return None

    device_menu = {}
    print("\nAvailable MaxSmart devices:")
    print("-" * 80)
    
    for i, device in enumerate(devices, start=1):
        sn = device["sn"]
        name = device["name"]
        ip = device["ip"]
        protocol = device.get("protocol", "unknown")
        firmware = device.get("ver", "Unknown")
        
        # Protocol emoji and feature info
        if protocol == "http":
            protocol_emoji = "🌐"
            features = "Full features"
        elif protocol == "udp_v3":
            protocol_emoji = "📡"
            features = "Basic features only"
        else:
            protocol_emoji = "❓"
            features = "Unknown capabilities"
        
        device_menu[i] = device
        print(f"{i}. {protocol_emoji} {name} ({ip})")
        print(f"   Protocol: {protocol.upper()} | FW: {firmware} | SN: {sn}")
        print(f"   {features}")
        print()

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

async def confirm_proceed(name, ip, sn, protocol):
    """Confirm with the user before proceeding with operations."""
    protocol_emoji = "🌐" if protocol == "http" else "📡" if protocol == "udp_v3" else "❓"
    
    print(f"\n{protocol_emoji} Selected device: {name} ({protocol.upper()})")
    print(f"IP: {ip} | SN: {sn}")
    
    if protocol == "http":
        print("📋 Available features: Port control, data retrieval, statistics, time, hardware IDs")
    elif protocol == "udp_v3":
        print("📋 Available features: Port control, data retrieval only")
        print("⚠️  Advanced features (statistics, time, hardware IDs) not available")
    else:
        print("⚠️  Protocol unknown - limited functionality expected")
    
    proceed = input("\nContinue with this device? (Y/N, default is Y): ")
    if proceed.strip().lower() not in ("y", ""):
        print("Aborted.")
        return False
    return True

async def select_port(port_mapping):
    """Prompt the user to select a port (1 to 6) to test, displaying current port names."""
    print("\nAvailable ports:")
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
        port_mapping = await selected_strip.retrieve_port_names()  # Works with both protocols
        for port in range(1, 7):
            power_data = await selected_strip.get_power_data(port)  # Works with both protocols
            watt_value = float(power_data["watt"])  # Ensure watt value is a float
            consumption_data.append([port_mapping[f"Port {port}"], watt_value])  # Append real port names and wattage
    except Exception as e:
        print(f"Error retrieving consumption data: {e}")
    return consumption_data

async def test_data_retrieval(device):
    """Test statistics data retrieval (HTTP only)."""
    if hasattr(device, 'protocol') and device.protocol == 'udp_v3':
        print("⚠️  Statistics not available on UDP V3 devices")
        return
        
    print("\nTesting Hourly Data:")
    try:
        hourly_data = await device.get_statistics(0, 0)  # port 0, hourly
        print(json.dumps(hourly_data, indent=2))
        
        # Process hourly data
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
            
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
                 
async def retrieve_time_based_data(powerstrip, data_type):
    """Retrieve hourly, daily, or monthly data for the strip (HTTP only)."""
    if hasattr(powerstrip, 'protocol') and powerstrip.protocol == 'udp_v3':
        print(f"⚠️  {data_type.capitalize()} statistics not available on UDP V3 devices")
        return None, None
        
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
    """Plot consumption data with proper units based on firmware version (HTTP only)."""
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

async def test_protocol_specific_features(selected_strip):
    """Test protocol-specific features."""
    protocol = getattr(selected_strip, 'protocol', 'unknown')
    
    print(f"\n🧪 Testing {protocol.upper()} Protocol Features")
    print("=" * 50)
    
    if protocol == "http":
        print("🌐 HTTP Protocol - Testing Advanced Features")
        
        # Test device time
        try:
            print("🕐 Testing device time...")
            time_data = await selected_strip.get_device_time()
            print(f"✅ Device time: {time_data['time']}")
        except Exception as e:
            print(f"❌ Device time failed: {e}")
        
        # Test hardware identifiers
        try:
            print("🔧 Testing hardware identifiers...")
            hw_ids = await selected_strip.get_device_identifiers()
            print(f"✅ CPU ID: {hw_ids.get('cpuid', 'N/A')[:16]}...")
            print(f"✅ Server: {hw_ids.get('server', 'N/A')}")
        except Exception as e:
            print(f"❌ Hardware IDs failed: {e}")
            
    elif protocol == "udp_v3":
        print("📡 UDP V3 Protocol - Testing Limitations")
        
        # Test that unsupported features are blocked
        try:
            print("🕐 Testing device time (should fail)...")
            await selected_strip.get_device_time()
            print("❌ Device time should not work on UDP V3!")
        except Exception as e:
            print(f"✅ Correctly blocked: {type(e).__name__}")
        
        try:
            print("🔧 Testing hardware IDs (should fail)...")
            await selected_strip.get_device_identifiers()
            print("❌ Hardware IDs should not work on UDP V3!")
        except Exception as e:
            print(f"✅ Correctly blocked: {type(e).__name__}")
            
        try:
            print("📈 Testing statistics (should fail)...")
            await selected_strip.get_statistics(0, 0)
            print("❌ Statistics should not work on UDP V3!")
        except Exception as e:
            print(f"✅ Correctly blocked: {type(e).__name__}")
    
    else:
        print("❓ Unknown protocol - skipping advanced tests")
      
async def main():
    selected_strip = None
    try:
        """Main function to run all tests with protocol support."""
        devices = await discover_devices()  # Now includes protocol detection
        if devices:
            print("Available MaxSmart devices with protocol information:")
            selected_device = await select_device(devices)  # Enhanced device selection
            
            if not await confirm_proceed(selected_device["name"], selected_device["ip"], 
                                       selected_device["sn"], selected_device.get("protocol", "unknown")):
                return
            
            # Create device with detected protocol
            protocol = selected_device.get("protocol")
            selected_strip = MaxSmartDevice(selected_device["ip"], protocol=protocol)
            await selected_strip.initialize_device()
            
            port_mapping = await selected_strip.retrieve_port_names()  # Works with both protocols
            firmware_version = selected_strip.version
            
            print(f"\n🔗 Connected to {selected_strip.name}")
            print(f"   Protocol: {protocol.upper()} | Firmware: {firmware_version}")

            # Ask user what they want to test
            while True:
                try:
                    print(f"\n🧪 What would you like to test on this {protocol.upper()} device?")
                    print("1. Port Control (Turn ON/OFF)")
                    print("2. Master Port Control (Turn all ON/OFF)")
                    print("3. Real-time Consumption Data")
                    
                    if protocol == "http":
                        print("4. Statistics and Graphs (Hourly/Daily/Monthly)")
                        print("5. Raw Statistics Data")
                        print("6. Protocol-specific Features (Time, Hardware IDs)")
                        print("7. Exit")
                        max_choice = 7
                    else:
                        print("4. Protocol-specific Features (Test limitations)")
                        print("5. Exit")
                        max_choice = 5
                    
                    choice = input(f"Select an option (1-{max_choice}): ")
                    
                    if choice == "1":
                        # Port control testing
                        port = await select_port(port_mapping)  # User selects port
                        
                        # First, check current state
                        print(f"\nChecking current state of port {port}...")
                        current_state = await check_port_state(selected_strip, port)
                        
                        if current_state is not None:
                            action = await select_power_action()  # User selects action
                            
                            if action == "1":  # Power ON
                                await power_on_port(selected_strip, port)
                            else:  # Power OFF
                                await power_off_port(selected_strip, port)
                        
                        input("\nPress Enter to continue...")
                    
                    elif choice == "2":
                        # Testing Master port operations
                        print("Master Port Control - Controls all 6 ports simultaneously")
                        
                        # First, check current state
                        print("Checking current state of master port (Port 0)...")
                        current_state = await check_port_state(selected_strip, 0)
                        
                        if current_state is not None:
                            action = await select_power_action()  # User selects action
                            
                            if action == "1":  # Power ON
                                await power_on_port(selected_strip, 0)
                            else:  # Power OFF
                                await power_off_port(selected_strip, 0)
                            
                            # Display consumption data after the operation
                            print("\nConsumption data after operation:")
                            consumption_data = await retrieve_consumption_data(selected_strip)
                            display_table(["Port Name", "Watt"], consumption_data)
                        
                        input("\nPress Enter to continue...")
                    
                    elif choice == "3":
                        # Real-time consumption data
                        print("Current real-time consumption data:")
                        consumption_data = await retrieve_consumption_data(selected_strip)
                        display_table(["Port Name", "Watt"], consumption_data)
                        input("\nPress Enter to continue...")
                    
                    elif choice == "4" and protocol == "http":
                        # Statistics and graphs (HTTP only)
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
                        
                        input("\nPress Enter to continue...")
                    
                    elif choice == "5" and protocol == "http":
                        # Raw statistics data (HTTP only)
                        await test_data_retrieval(selected_strip)
                        input("\nPress Enter to continue...")
                    
                    elif choice == "6" and protocol == "http":
                        # Protocol-specific features (HTTP)
                        await test_protocol_specific_features(selected_strip)
                        input("\nPress Enter to continue...")
                    
                    elif choice == "4" and protocol != "http":
                        # Protocol-specific features (UDP V3 limitations)
                        await test_protocol_specific_features(selected_strip)
                        input("\nPress Enter to continue...")
                    
                    elif (choice == "7" and protocol == "http") or (choice == "5" and protocol != "http"):
                        print("Exiting...")
                        break
                    
                    else:
                        print(f"Invalid choice. Please select 1-{max_choice}.")
                
                except KeyboardInterrupt:
                    print("\n\nOperation interrupted by user (Ctrl+C)")
                    break
                except EOFError:
                    print("\n\nInput interrupted by user")
                    break
                        
        else:
            print("No MaxSmart devices found.")

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