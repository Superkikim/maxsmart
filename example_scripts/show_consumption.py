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
        devices = await discovery.discover_maxsmart()
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

    print("\nAvailable MaxSmart devices:")
    for i, device in enumerate(devices, start=1):
        fw_info = f" (FW: {device.get('ver', 'Unknown')})" if device.get('ver') else ""
        print(f"{i}. {device['name']} - {device['ip']}{fw_info}")

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
    """Retrieve real-time consumption data for each port using centralized conversion."""
    consumption_data = []
    try:
        # Get port names
        port_mapping = await device.retrieve_port_names()
        
        # Get all data at once for better performance
        all_data = await device.get_data()
        watt_values = all_data.get('watt', [])
        switch_states = all_data.get('switch', [])
        
        # Build consumption data with state info
        for port in range(1, min(7, len(watt_values) + 1)):
            port_name = port_mapping.get(f"Port {port}", f"Port {port}")
            watt_value = watt_values[port - 1] if port - 1 < len(watt_values) else 0.0
            state = switch_states[port - 1] if port - 1 < len(switch_states) else 0
            state_text = "ON" if state else "OFF"
            
            consumption_data.append([port_name, watt_value, state_text])
            
    except Exception as e:
        print(f"Error retrieving consumption data: {e}")
    return consumption_data

def display_table(header, data):
    """Display data in a formatted table with proper alignment."""
    if not data:
        print("No data to display.")
        return
        
    # Calculate column widths
    col_widths = []
    for i in range(len(header)):
        max_width = len(header[i])
        for row in data:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width)
    
    # Print header
    header_format = " | ".join(f"{{:<{w}}}" for w in col_widths)
    print(header_format.format(*header))
    print("-" * (sum(col_widths) + 3 * (len(header) - 1)))
    
    # Print data rows
    row_format = " | ".join(f"{{:<{w}}}" for w in col_widths)
    for row in data:
        if len(row) >= 3:  # Port name, watt, state
            print(row_format.format(row[0], f"{row[1]:.2f}", row[2]))
        else:
            print(row_format.format(*row))

async def show_device_info(device):
    """Display device information and auto-detection results."""
    print(f"\n{'='*60}")
    print("DEVICE INFORMATION")
    print(f"{'='*60}")
    print(f"Name: {device.name}")
    print(f"IP Address: {device.ip}")
    print(f"Serial Number: {device.sn}")
    print(f"Firmware Version: {device.version}")
    print(f"Data Format: {getattr(device, '_watt_format', 'unknown')}")
    print(f"Conversion Factor: {getattr(device, '_watt_multiplier', 1.0)}")
    
    # Show total consumption
    try:
        all_data = await device.get_data()
        watt_values = all_data.get('watt', [])
        switch_states = all_data.get('switch', [])
        
        total_watts = sum(watt_values) if watt_values else 0
        active_ports = sum(switch_states) if switch_states else 0
        
        print(f"Total Consumption: {total_watts:.2f}W")
        print(f"Active Ports: {active_ports}/6")
    except Exception as e:
        print(f"Error getting device summary: {e}")
    
    print(f"{'='*60}")

async def main_loop():
    """Main application loop with device selection."""
    while True:
        device = None
        
        try:
            # Discover devices
            devices = await discover_devices()
            if not devices:
                print("No MaxSmart devices found.")
                choice = input("Try again? (y/N): ")
                if choice.lower() != 'y':
                    break
                continue

            # Select device
            selected_device = select_device(devices)
            if not selected_device:
                break

            # Create and initialize device
            print(f"\nConnecting to {selected_device['name']} ({selected_device['ip']})...")
            device = MaxSmartDevice(selected_device['ip'])
            await device.initialize_device()
            
            # Show device info
            await show_device_info(device)

            # Get and display consumption data
            consumption_data = await retrieve_consumption_data(device)
            if consumption_data:
                print("\nReal-time Port Consumption:")
                display_table(["Port Name", "Watts", "State"], consumption_data)
                
                # Calculate totals
                total_consumption = sum(row[1] for row in consumption_data)
                active_count = sum(1 for row in consumption_data if row[2] == "ON")
                
                print(f"\nSummary:")
                print(f"  Total Consumption: {total_consumption:.2f}W")
                print(f"  Active Ports: {active_count}/6")
                print(f"  Average per Active Port: {total_consumption/active_count:.2f}W" if active_count > 0 else "  No active ports")
            else:
                print("Unable to retrieve consumption data.")
                
            # Ask what to do next
            print(f"\nOptions:")
            print("  1. Refresh data")
            print("  2. Select different device") 
            print("  3. Exit")
            
            choice = input("\nSelect option (1-3): ")
            
            if choice == "1":
                # Refresh current device data
                continue
            elif choice == "2":
                # Go back to device selection
                await device.close()
                device = None
                continue
            else:
                # Exit
                break
                
        except KeyboardInterrupt:
            print("\n\nInterrupted by user (Ctrl+C)")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
            
            choice = input("Continue? (y/N): ")
            if choice.lower() != 'y':
                break
        finally:
            # Cleanup
            if device:
                try:
                    await device.close()
                except Exception as e:
                    print(f"Error closing device: {e}")
    
    print("\nGoodbye!")

async def main():
    """Main entry point."""
    print("MaxSmart Device Consumption Monitor")
    print("===================================")
    print("Monitor real-time power consumption with auto-detection")
    print()
    
    await main_loop()

if __name__ == "__main__":
    asyncio.run(main())