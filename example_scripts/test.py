#!/usr/bin/env python3
# test.py
# This script tests the methods of the MaxSmart device.

import asyncio
from maxsmart.device import MaxSmartDevice
from maxsmart.const import CMD_SET_PORT_STATE, CMD_GET_DEVICE_DATA
from maxsmart.exceptions import ConnectionError, CommandError, DeviceOperationError

async def main():
    ip = "172.30.47.161"  # Your device's IP address
    device = None  # Initialize the device variable

    try:
        print(f"Creating MaxSmartDevice instance for IP: {ip}...")
        device = MaxSmartDevice(ip)
        print("Device instantiated successfully.")

        # Test turning on port 3
        print("Turning ON port 3...")
        await device.turn_on(port=3)
        print("Port 3 has been turned ON.")

        # Test checking the state of port 3
        print("Checking state of port 3...")
        port_3_state = await device.check_state(port=3)
        print("Current state of port 3:", port_3_state)

        # Test turning off port 3
        print("Turning OFF port 3...")
        await device.turn_off(port=3)
        print("Port 3 has been turned OFF.")

        # Test checking the state of port 3 again
        print("Checking state of port 3...")
        port_3_state_after_off = await device.check_state(port=3)
        print("Current state of port 3:", port_3_state_after_off)

    except ConnectionError as ce:
        print(f"Connection error occurred: {ce}")
    except CommandError as ce:
        print(f"Command error occurred: {ce}")
    except DeviceOperationError as doe:
        print(f"Device operation error occurred: {doe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the device session is closed
        if device is not None:
            await device.close()
            print("Device session closed.")

# Execute the function
if __name__ == "__main__":
    asyncio.run(main())
