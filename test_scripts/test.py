from maxsmart import MaxSmart

def main():
    # Discover MaxSmart devices
    devices = MaxSmart.discover_maxsmart()
    
    if devices:
        # Select the Cuisine strip
        cuisine_strip = None
        for device in devices:
            if device["name"] == "Cuisine":
                cuisine_strip = device
                break
        
        if cuisine_strip:
            ip = cuisine_strip["ip"]
            sn = cuisine_strip["sn"]
            
            # Create MaxSmart object for the Cuisine strip
            cuisine_maxsmart = MaxSmart(ip, sn)
            
            # Get the example outputs
            state_output = cuisine_maxsmart.check_state()
            
            port = 1  # Change the port number as needed
            port_state_output = cuisine_maxsmart.check_port_state(port)
            
            # Display the example outputs
            print("Example output for check_state():")
            print(state_output)
            
            print(f"\nExample output for check_port_state({port}):")
            print(port_state_output)
        else:
            print("Cuisine strip not found.")
    else:
        print("No MaxSmart devices found.")

if __name__ == "__main__":
    main()
