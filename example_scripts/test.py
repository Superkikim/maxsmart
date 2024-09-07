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
        # Select the strip
        salon_strip = None
        for device in devices:
            if device["name"] == "Salon":
                strip = device
                break

        if strip:
            ip = strip["ip"]

            # Create MaxSmart object for the strip
            maxsmart = MaxSmartDevice(ip)

            # Get the example outputs
            state_output = maxsmart.check_state()

            port = 2  # Change the port number as needed
            port_state_output = maxsmart.check_port_state(port)

            # Display name ip and port
            print("Selected strip is Salon. IP is %s and port is %s" % (ip, port))

            # Display the example outputs
            print("Example output for check_state():")
            print(state_output)

            print(f"\nExample output for check_port_state({port}):")
            print(port_state_output)

            print("Retrieving real-time consumption data...")
            consumption_data = []
            for port in range(1, 7):
                power_data = maxsmart.get_power_data(port)
                consumption_data.append([f"Port {port}", power_data["watt"]])
            display_table(["Port", "Watt"], consumption_data)

        else:
            print("strip not found.")
    else:
        print("No MaxSmart devices found.")


if __name__ == "__main__":
    main()
