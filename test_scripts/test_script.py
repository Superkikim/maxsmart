import time
from maxsmart import MaxSmart

def display_table(header, data):
    print(f"{' | '.join(header)}")
    print("-" * (len(header) * 10))
    for row in data:
        print(f"{' | '.join(str(item) for item in row)}")

def discover_devices():
    print("Discovering MaxSmart devices...")
    maxsmart = MaxSmart("", "")  # Create an instance of MaxSmart
    devices = maxsmart.discover_maxsmart()  # Call the instance method
    return devices


def select_device(devices):
    print("Available MaxSmart devices:")
    device_menu = {}
    for i, device in enumerate(devices, start=1):
        sn = device["sn"]
        name = device["name"]
        ip = device["ip"]
        device_menu[i] = device
        print(f"{i}. SN: {sn}, Name: {name}, IP: {ip}")

    while True:
        choice = input("Select a device (number): ")
        try:
            choice = int(choice)
            if choice in device_menu:
                selected_device = device_menu[choice]
                return selected_device
            else:
                print("Invalid choice. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def test_powerstrip(ip, sn):
    print("WARNING: This test will power down all devices plugged into the power strip.")
    print(f"IP: {ip}, SN: {sn}")
    proceed = input("Do you want to proceed? (Y/N): ")
    if proceed.lower() != "y":
        print("Test aborted.")
        return

    maxsmart = MaxSmart(ip, sn)

    print("Powering ON port 3...")
    maxsmart.turn_on(3)
    print("Waiting 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Countdown: {i} seconds")
        time.sleep(1)
    print("Powering OFF port 3...")
    maxsmart.turn_off(3)
    print("Waiting 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Countdown: {i} seconds")
        time.sleep(1)
    print("Powering OFF all ports...")
    maxsmart.turn_off(0)
    print("Waiting 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Countdown: {i} seconds")
        time.sleep(1)
    print("Powering ON all ports...")
    maxsmart.turn_on(0)
    print("Waiting 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Countdown: {i} seconds")
        time.sleep(1)
    print("Powering OFF ports 3 to 6...")
    for port in range(3, 7):
        maxsmart.turn_off(port)
    print("Retrieving real-time consumption data...")
    consumption_data = []
    for port in range(1, 7):
        power_data = maxsmart.get_power_data(port)
        consumption_data.append([f"Port {port}", power_data["watt"], power_data["amp"]])
    display_table(["Port", "Watt", "Amp"], consumption_data)
    print("Retrieving 24-hour consumption data...")
    hourly_data = []
    for port in range(1, 7):
        hourly_data.append([f"Port {port}", maxsmart.get_hourly_data(port)])
    display_table(["Port", "Hourly Data"], hourly_data)

if __name__ == "__main__":
    devices = discover_devices()
    if devices:
        selected_device = select_device(devices)
        ip = selected_device["ip"]
        sn = selected_device["sn"]
        test_powerstrip(ip, sn)
    else:
        print("No MaxSmart devices found.")
