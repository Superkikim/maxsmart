from maxsmart import MaxSmart  # Import the MaxSmart class from the maxsmart module

def discover_devices(ip=None):
    print("Discovering MaxSmart devices...")
    maxsmart = MaxSmart("","")  # Create an instance of MaxSmart
    devices = maxsmart.discover_maxsmart(ip)  # Call the instance method
    return devices

def main():
    devices = discover_devices()
    print(devices)  # Print the devices

if __name__ == "__main__":
    main()

