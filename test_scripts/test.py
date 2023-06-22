from maxsmart import MaxSmartDiscovery, MaxSmartDevice

def display_table(header, data):
    print(f"{' | '.join(header)}")
    print("-" * (len(header) * 10))
    for row in data:
        print(f"{' | '.join(str(item) for item in row)}")

def main():
    # Discover MaxSmart devices
    devices = MaxSmartDiscovery.discover_maxsmart()
    
    if devices:
        # Select the Cuisine strip
        cuisine_strip = None
        for device in devices:
            if device["name"] == "Cuisine":
                cuisine_strip = device
                break
        
        if cuisine_strip:
            ip = cuisine_strip["ip"]
            
            # Create MaxSmart object for the Cuisine strip
            cuisine_maxsmart = MaxSmartDevice(ip)
            
            # Get the example outputs
            state_output = cuisine_maxsmart.check_state()
            
            port = 1  # Change the port number as needed
            port_state_output = cuisine_maxsmart.check_port_state(port)
            
            # Display the example outputs
            print("Example output for check_state():")
            print(state_output)
            
            print(f"\nExample output for check_port_state({port}):")
            print(port_state_output)

            print("Retrieving real-time consumption data...")
            consumption_data = []
            for port in range(1, 7):
                power_data = cuisine_maxsmart.get_power_data(port)
                consumption_data.append([f"Port {port}", power_data["watt"]])
            display_table(["Port", "Watt"], consumption_data)

        else:
            print("Cuisine strip not found.")
    else:
        print("No MaxSmart devices found.")

if __name__ == "__main__":
    main()
