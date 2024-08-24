#!/usr/bin/env python3
import sys
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError  # Import exceptions

def main():
    # Check for name argument
    if len(sys.argv) != 2:
        print("Usage: python retrieve_states.py <strip_name>")
        return

    # Get the strip name from the command line parameter
    strip_name = sys.argv[1]

    try:
        # Discover MaxSmart devices
        discovery = MaxSmartDiscovery()
        devices = discovery.discover_maxsmart()

        # Check if any devices were found
        if devices:
            # Initialize variable to hold reference to the specified strip
            specified_strip = None

            # Look for the device matching the specified name
            for device in devices:
                if device["name"].lower() == strip_name.lower():
                    specified_strip = device  # Store the found strip
                    break  # Exit the loop once the device is found

            # If the specified strip is found, proceed to check its ports
            if specified_strip:
                ip = specified_strip["ip"]  # Get the IP address of the specified strip

                # Create MaxSmartDevice object for the specified strip
                specified_maxsmart = MaxSmartDevice(ip)

                # Retrieve the state for all ports (1 to 6) and store their states
                port_states = []
                for port in range(1, 7):
                    port_state = specified_maxsmart.check_port_state(port)  # Check each port's state
                    port_states.append((port, port_state))  # Append the port number and its state

                # Retrieve the state of the strip itself
                strip_state = specified_maxsmart.check_state()
                print(strip_state)  # Print the state of the entire strip

                # Display the results for each port state
                print("Port states:")
                for port, state in port_states:
                    print(f"Port {port}: {state}")  # Output the state of each port

                # Print the overall state of the strip
                print(f"Strip state: {strip_state}")
            else:
                print(f"{strip_name} strip not found.")  # Handle case where specified strip isn't found
        else:
            print("No MaxSmart devices found.")  # Handle case where no devices are discovered
            
    except ConnectionError as ce:
        print(f"Connection error occurred: {ce}")
    except DiscoveryError as de:
        print(f"Discovery error occurred: {de}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()  # Execute the main function when the script is run
