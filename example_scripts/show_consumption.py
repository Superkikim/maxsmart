#!/usr/bin/env python3
# example_scripts/show_consumption.py

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
    print("  R. Rescan network")
    print("  0. Exit")

    while True:
        try:
            choice = input("Select device number, R to rescan, or 0 to exit: ").strip()
            
            if choice == "0":
                return "exit"
            elif choice.upper() == "R":
                return "rescan"
            
            choice_int = int(choice)
            if 1 <= choice_int <= len(devices):
                return devices[choice_int - 1]
            else:
                print(f"Invalid choice. Please enter 1-{len(devices)}, R, or 0.")
                
        except ValueError:
            print("Invalid input. Please enter a number, R, or 0.")
        except (KeyboardInterrupt, EOFError):
            print("\nAborted by user")
            return "exit"

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
        
        # Build consumption data with state info - detect actual port count
        actual_port_count = len(watt_values) if watt_values else 0
        for port in range(1, actual_port_count + 1):
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
        actual_port_count = len(switch_states) if switch_states else 0
        
        print(f"Total Consumption: {total_watts:.2f}W")
        print(f"Active Ports: {active_ports}/{actual_port_count}")
        print(f"Device Type: {'Smart Plug' if actual_port_count == 1 else f'{actual_port_count}-Port Power Station'}")
    except Exception as e:
        print(f"Error getting device summary: {e}")
    
    print(f"{'='*60}")

async def device_loop(device):
    """Handle operations for a single device with refresh capability."""
    while True:
        try:
            # Show device info
            await show_device_info(device)

            # Get and display consumption data
            consumption_data = await retrieve_consumption_data(device)
            if consumption_data:
                print("\nReal-time Port Consumption:")
                display_table(["Port Name", "Watts", "State"], consumption_data)
                
                # Calculate totals
                total_consumption = sum(row[1] for row in consumption_data)
                actual_port_count = len(consumption_data)
                active_count = sum(1 for row in consumption_data if row[2] == "ON")
                
                print(f"\nSummary:")
                print(f"  Total Consumption: {total_consumption:.2f}W")
                print(f"  Active Ports: {active_count}/{actual_port_count}")
                print(f"  Device Type: {'Smart Plug' if actual_port_count == 1 else f'{actual_port_count}-Port Power Station'}")
                print(f"  Average per Active Port: {total_consumption/active_count:.2f}W" if active_count > 0 else "  No active ports")
            else:
                print("Unable to retrieve consumption data.")
                
            # Ask what to do next
            print(f"\nOptions:")
            print("  1. Refresh data (same device)")
            print("  2. Select different device") 
            print("  3. Exit")
            
            try:
                choice = input("\nSelect option (1-3): ")
            except (KeyboardInterrupt, EOFError):
                print("\nAborted by user")
                return "exit"
            
            if choice == "1":
                # Refresh current device data - stay in device loop
                print("\n" + "="*40)
                print("REFRESHING DATA...")
                print("="*40)
                continue
            elif choice == "2":
                # Go back to device selection - exit device loop
                return "select_different"
            elif choice == "3":
                # Exit completely
                return "exit"
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                
        except (KeyboardInterrupt, EOFError):
            print("\nAborted by user")
            return "exit"
        except Exception as e:
            print(f"Error in device operations: {e}")
            
            try:
                retry = input("Retry with same device? (y/N): ")
                if retry.lower() != 'y':
                    return "select_different"
            except (KeyboardInterrupt, EOFError):
                print("\nAborted by user")
                return "exit"

async def main_loop():
    """Main application loop with device selection."""
    # Initial discovery at startup
    print("🔍 Scanning network for MaxSmart devices...")
    devices = await discover_devices()
    
    if not devices:
        print("❌ No MaxSmart devices found on initial scan.")
        try:
            choice = input("Exit? (Y/n): ")
            if choice.lower() != 'n':
                return
        except (KeyboardInterrupt, EOFError):
            print("\nAborted by user")
            return
    else:
        print(f"✅ Found {len(devices)} device(s)")
    
    while True:
        device = None
        
        try:
            # Select device from cached list
            selected_device = select_device(devices)
            if not selected_device or selected_device == "exit":
                break
            elif selected_device == "rescan":
                # Rescan network
                print("\n🔍 Rescanning network...")
                devices = await discover_devices()
                if not devices:
                    print("❌ No devices found after rescan.")
                    continue
                else:
                    print(f"✅ Found {len(devices)} device(s) after rescan")
                continue

            # Create and initialize device
            print(f"\nConnecting to {selected_device['name']} ({selected_device['ip']})...")
            device = MaxSmartDevice(selected_device['ip'])
            await device.initialize_device()
            
            # Enter device-specific operations loop
            result = await device_loop(device)
            
            if result == "exit":
                break
            elif result == "select_different":
                # Continue to select a different device
                continue
                
        except KeyboardInterrupt:
            print("\n\nAborted by user (Ctrl+C)")
            break
        except EOFError:
            print("\n\nAborted by user")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                choice = input("Continue? (y/N): ")
                if choice.lower() != 'y':
                    break
            except (KeyboardInterrupt, EOFError):
                print("\nAborted by user")
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