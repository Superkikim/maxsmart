#!/usr/bin/env python3
import asyncio
from maxsmart.device import MaxSmartDevice  # Import the MaxSmartDevice class from the maxsmart module

async def list_maxsmart_device_content(device):
    """List the contents of a MaxSmartDevice object."""
    properties = vars(device)  # Using __dict__ to get attributes

    # Print the properties/attributes with their values
    for attribute in properties:
        if not attribute.startswith('__') and not callable(getattr(device, attribute)):
            print(f"{attribute}: {getattr(device, attribute)}")

async def main():
    device_ip = "172.30.47.130"  # Update this to the actual device IP
    maxsmart_device = MaxSmartDevice(device_ip)

    # Call the asynchronous initialization method
    await maxsmart_device.initialize_device()

    # Display all attributes of the MaxSmartDevice instance
    await list_maxsmart_device_content(maxsmart_device)

    # Close the session when done
    await maxsmart_device.close()

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
