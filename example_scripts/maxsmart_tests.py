#!/usr/bin/env python3
# maxsmart_tests.py
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
import time
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError
import matplotlib.pyplot as plt

def discover_devices():
    """Discover MaxSmart devices on the network."""
    print("Discovering MaxSmart devices...")
    try:
        discovery = MaxSmartDiscovery()  # Create an instance of MaxSmartDiscovery
        devices = discovery.discover_maxsmart()  # Call the discover method
        return devices  # Return the list of discovered devices
    except ConnectionError as ce:
        print(f"Connection error occurred during discovery: {ce}")
        return []  # Return an empty list on connection error
    except DiscoveryError as de:
        print(f"Discovery error occurred: {de}")
        return []  # Return an empty list on discovery error
    except Exception as e:
        print(f"An unexpected error occurred during discovery: {e}")
        return []  # Return an empty list on unexpected error

def select_device(devices):
    """Allow the user to select a specific device."""
    if not devices:
        print("No devices available for selection.")
        return None  # Return None if no devices are found

    device_menu = {}  # Dictionary to hold device options
    for i, device in enumerate(devices, start=1):
        sn = device["sn"]
        name = device["name"]
        ip = device["ip"]
        device_menu[i] = device  # Map menu choice to device
        print(f"{i}. SN: {sn}, Name: {name}, IP: {ip}")  # Display the device info

    while True:
        choice = input("Select a device by number: ")
        try:
            choice = int(choice)  # Convert input to an integer
            if choice in device_menu:
                return device_menu[choice]  # Return the selected device
            else:
                print("Invalid choice. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")  # Handle non-integer input

def confirm_proceed(name, ip, sn):
    """Confirm with the user before proceeding with operations."""
    print("WARNING: This test will power down all devices plugged into the power strip.")
    print(f"Name: {name}, IP: {ip}, SN: {sn}")  # Display selected device details
    proceed = input("Do you want to proceed? (Y/N, default is Y): ")  # Inform user ENTER means 'Yes'
    if proceed.strip().lower() not in ("y", ""):  # Treat empty input as 'Yes'
        print("Test aborted.")
        return False  # Return False if the user does not want to proceed
    return True  # Return True if the user agrees to proceed

def select_port(port_mapping):
    """Prompt the user to select a port (1 to 6) to test, displaying current port names."""
    print("Available ports:")
    # Display the retrieved port names
    for i in range(1, 7):  # Port 1 to Port 6
        print(f"Port {i}: {port_mapping.get(f'Port {i}', f'Port {i}')}")
    
    while True:
        port = input("Select a port (1-6): ")  # Prompt for port selection
        try:
            port = int(port)  # Convert input to an integer
            if 1 <= port <= 6:
                return port  # Valid port selected
            else:
                print("Invalid choice. Please select a port number between 1 and 6.")  # Corrected message
        except ValueError:
            print("Invalid input. Please enter a number.")  # Handle non-integer input

def select_power_action():
    """Prompt the user to select whether to power on or off the port."""
    while True:
        action = input("Would you like to (1) Power ON or (2) Power OFF the port? (Enter 1 or 2): ")
        if action in ("1", "2"):
            return action  # Return the selected action
        else:
            print("Invalid choice. Please enter 1 to power ON or 2 to power OFF.")

def power_on_port(powerstrip, port):
    """Power on a specified port."""
    print(f"Powering ON port {port}...")
    try:
        powerstrip.turn_on(port)  # Turn on the specified port
    except Exception as e:
        print(f"Error while attempting to power ON port {port}: {e}")

def power_off_port(powerstrip, port):
    """Power off a specified port and wait 15 seconds."""
    print(f"Powering OFF port {port}...")
    try:
        powerstrip.turn_off(port)  # Turn off the specified port
    except Exception as e:
        print(f"Error while attempting to power OFF port {port}: {e}")

def check_state(selected_device, port):
    """Check the state of the specified port using the selected_device instance."""
    return selected_device.check_port_state(port)  # Leverage the existing check_port_state method

def retrieve_consumption_data(selected_strip):
    """Retrieve real-time consumption data for each port and return it."""
    consumption_data = []
    try:
        port_mapping = selected_strip.retrieve_port_names()  # Call to fetch the port names
        for port in range(1, 7):  # Loop through ports 1 to 6
            power_data = selected_strip.get_power_data(port)  # Get power data for each port
            watt_value = float(power_data["watt"])  # Ensure watt value is a float
            consumption_data.append([port_mapping[f"Port {port}"], watt_value])  # Append real port names and wattage
    except Exception as e:
        print(f"Error retrieving consumption data: {e}")
    return consumption_data  # Return the list of consumption data

def retrieve_hourly_data(powerstrip):
    """Retrieve hourly data for ports and return it as a list of lists, where each sublist is a port's data."""
    print("Retrieving hourly consumption data...")
    hourly_data = []
    for port in range(1, 7):
        try:
            data = powerstrip.get_hourly_data(port)  # Get hourly data for each port
            # Ensure that data is converted to float, collecting valid numbers
            if data:
                hourly_data.append([float(d) for d in data if isinstance(d, (int, float, str)) and d.replace('.', '', 1).isdigit()])
            else:
                hourly_data.append([])  # Append an empty list if no data is found for that port
        except Exception as e:
            print(f"Error retrieving hourly data for port {port}: {e}")
            hourly_data.append([])  # Append empty if there's an error retrieving data
    return hourly_data  # Return the collected hourly data

def countdown(seconds):
    """Display a countdown timer."""
    for i in range(seconds, 0, -1):
        print(f"Countdown: {i} seconds remaining ", end='\r')  # Print countdown on the same line
        time.sleep(1)  # Wait for 1 second
    print("                                 ", end='\r')  # Clear the line after countdown

def display_table(header, data):
    """Display data in a formatted table."""
    # Calculate the maximum width needed for each column
    max_widths = [len(header[0]), len(header[1])]  # Start with the header lengths
    for row in data:
        max_widths[0] = max(max_widths[0], len(row[0]))  # Port name width
        max_widths[1] = max(max_widths[1], len(f"{row[1]:.2f}"))  # Watt width, including formatting
    
    # Create formatted header with aligned columns
    header_format = " | ".join(f"{{:<{max_widths[i]}}}" for i in range(len(header)))
    print(header_format.format(*header))  # Print header
    print("-" * (sum(max_widths) + len(max_widths) + 1))  # Separator line
    
    # Print each row in a formatted way
    row_format = " | ".join(f"{{:<{max_widths[i]}}}" for i in range(len(header)))
    for row in data:
        watt_value = f"{row[1]:.2f}"  # Format the watt value to two decimal places
        # Ensure proper spacing for single-digit watt values
        if row[1] < 10:
            watt_value = " " + watt_value  # Add space for alignment
        print(row_format.format(row[0], watt_value))  # Print each row

def plot_vectorial_graph(port_mapping, data):
    """Create and display the plot in a non-blocking way and wait for user input to continue."""
    # Create the figure and set the window title
    fig, ax = plt.subplots(figsize=(12, 6), num=f"Hourly Consumption Data per Port for {port_mapping['Port 0']}")
    
    # Prepare the x-axis (hours) and the y-axis (power consumption data)
    hours = list(range(1, 25))  # Assuming you have hourly data for 24 hours
    for port_idx in range(1, 7):
        if data[port_idx - 1]:  # Adjust for zero-indexing
            ax.plot(hours, data[port_idx - 1], label=port_mapping[f'Port {port_idx}'], marker='o')  # Plot each port's data
        else:
            print(f"No data available for {port_mapping[f'Port {port_idx}']}")  # Handle ports without data
    
    ax.set_title("Hourly Consumption Data per Port")  # Title for the graph
    ax.set_xlabel("Hours (1-24)")  # X-axis label
    ax.set_ylabel("Consumption (W)")  # Y-axis label
    ax.set_xticks(hours)  # Set x-ticks to show each hour
    ax.grid(True)  # Add grid lines for better readability
    ax.legend()  # Show legend for better identification of lines
    plt.tight_layout()  # Adjust layout to prevent clipping of text
    plt.show(block=False)  # Display the plot in non-blocking mode

    # Wait for user input to continue
    input("Press Enter to continue...")  # Keep the plot open until Enter is pressed
    plt.close(fig)  # Optionally close the figure after input

def main():
    """Main function to run all tests."""
    devices = discover_devices()  # Discover MaxSmart devices
    if devices:
        print("Available MaxSmart devices:")
        selected_device = select_device(devices)  # Allow the user to select a device
        
        # Confirm before proceeding
        if not confirm_proceed(selected_device["name"], selected_device["ip"], selected_device["sn"]):
            return  # Exit main if the user does not want to proceed
        
        # Create MaxSmartDevice instance
        selected_strip = MaxSmartDevice(selected_device["ip"])  # Create instance for the selected strip
        
        # Retrieve current port names
        port_mapping = selected_strip.retrieve_port_names()  
        
        print(port_mapping)
        port = select_port(port_mapping)  # Get the port number from the user
        action = select_power_action()  # Ask user for the action they want to perform
        
        if action == "1":  # Power ON
            power_on_port(selected_strip, port)  # Power ON the specified port
            countdown(10)  # Countdown after powering ON
            power_off_port(selected_strip, port)  # Power OFF the specified port
            countdown(10)  # Countdown after powering OFF
        else:  # Power OFF
            power_off_port(selected_strip, port)  # Power OFF the specified port
            countdown(10)  # Countdown after powering OFF
            power_on_port(selected_strip, port)  # Power ON the specified port
            countdown(10)  # Countdown after powering ON
            
        # Testing Master port operations
        print("WARNING: Turning off the master port (Port 0) will power off all devices plugged into the power strip.")
        
        proceed = input("Do you want to proceed? (Y/N): ")
        if proceed.lower() != "y":
            print("Operation aborted.")
        else:
            # Power OFF the master port
            print("Powering OFF the master port (and all connected devices)...")
            power_off_port(selected_strip, 0)  # Use the existing function
            countdown(10)  # Countdown for 10 seconds
            
            # Display consumption data after turning off
            print("Consumption data after powering OFF:")
            consumption_data = retrieve_consumption_data(selected_strip)  # Retrieve consumption data
            display_table(["Port Name", "Watt"], consumption_data)  # Display the table with consumption data
            
            # Power ON the master port
            print("Powering ON the master port (restoring power to all devices)...")
            power_on_port(selected_strip, 0)  # Use the existing function
            countdown(10)  # Countdown for 10 seconds
            
            # Display consumption data after turning on
            print("Consumption data after powering ON:")
            consumption_data = retrieve_consumption_data(selected_strip)  # Retrieve consumption data again
            display_table(["Port Name", "Watt"], consumption_data)  # Display the table with consumption data
            
            # Display last 24 hours wattage for each port
            print("Displaying last 24 hours wattage for each port")
            hourly_data = retrieve_hourly_data(selected_strip)  # Get the hourly data
            
            # Display hourly data graph
            plot_vectorial_graph(port_mapping, hourly_data)  # Plot the vectorial graph
    else:
        print("No MaxSmart devices found.")  # Handle case where no devices are discovered

if __name__ == "__main__":
    main()  # Execute the main function when the script is run
