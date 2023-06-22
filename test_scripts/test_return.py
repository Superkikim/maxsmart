#!/usr/bin/env python3
from maxsmart import MaxSmartDiscovery, MaxSmartDevice

def main():
    # Discover MaxSmart devices
    discovery = MaxSmartDiscovery()
    devices = discovery.discover_maxsmart()
    print(devices)
    
    if devices:
        # Select the Cuisine strip
        cuisine_strip = None
        for device in devices:
            if device["name"] == "Cuisine":
                cuisine_strip = device
                break
        
        if cuisine_strip:
            ip = cuisine_strip["ip"]
            
            # Create MaxSmartDevice object for the Cuisine strip
            cuisine_maxsmart = MaxSmartDevice(ip)
            
            # Retrieve the state for all ports
            port_states = []
            for port in range(1, 7):
                port_state = cuisine_maxsmart.check_port_state(port)
                port_states.append((port, port_state))
            
            # Retrieve the state of the strip
            strip_state = cuisine_maxsmart.check_state()
            
            # Display the results
            print("Port states:")
            for port, state in port_states:
                print(f"Port {port}: {state}")
            
            print(f"Strip state: {strip_state}")
        else:
            print("Cuisine strip not found.")
    else:
        print("No MaxSmart devices found.")

if __name__ == "__main__":
    main()
