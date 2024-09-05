#!/usr/bin/env python3
# test2.py
import asyncio
from maxsmart.device import MaxSmartDevice  # Adjust the import path based on your project structure

# Assuming the Device class takes an IP address and user locale during initialization
async def test_device_state(ip, port):

    try:
        # Create an instance of MaxSmartDevice
        print(f"Creating MaxSmartDevice instance for IP: {ip}...")
        device = MaxSmartDevice(ip)
        print("Device instantiated successfully.\n")
    
        # Check the current state of the specified port
        current_state = await device.check_state(port=port)
        print(f"Current state of port {port}: {current_state}")

        # Expected state for verification
        expected_state = 1  # assuming we want to check if it's ON
        await device._verify_state(port=port, expected_state=expected_state)
        
        print(f"Port {port} is in the expected state: {expected_state} (ON)" if current_state == expected_state else f"Port {port} is not in the expected state.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the test
if __name__ == "__main__":
    ip_address = "172.30.47.78"
    port = 3
    asyncio.run(test_device_state(ip_address, port))
