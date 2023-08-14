from maxsmart import MaxSmartDiscovery  # Import the MaxSmartDiscovery class from the maxsmart module

def discover_devices(ip=None):
    print("Discovering MaxSmart devices...")
    discovery = MaxSmartDiscovery()  # Create an instance of MaxSmartDiscovery
    ip = "255.255.255.255"
    devices = discovery.discover_maxsmart(ip)  # Call the instance method
    return devices

def main():
    devices = discover_devices()
    print(devices)  # Print the devices

if __name__ == "__main__":
    main()
