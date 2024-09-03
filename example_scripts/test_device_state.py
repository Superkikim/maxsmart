#!/usr/bin/env python3
# test_device_state.py

import asyncio
from maxsmart.device import MaxSmartDevice
from maxsmart.exceptions import ConnectionError, CommandError, StateError

async def test_device_operations(ip):
    """Test operations on the MaxSmart device."""
    try:
        # Create MaxSmartDevice instance
        print(f"Creating MaxSmartDevice instance for IP: {ip}...")
        device = MaxSmartDevice(ip)

        # 1. Check state of port 3
        print("Calling method: check_state(port=3)")
        port_3_state = await device.check_state(port=3)
        print(f"The method returned: Current state of port 3: {port_3_state}")
        print("=======================")

        # 2. Check state of all ports
        print("Calling method: check_state() for all ports")
        all_ports_state = await device.check_state()
        print(f"The method returned: Current state of all ports: {all_ports_state}")
        print("=======================")

        # 3. Turn on port 3
        print("Calling method: turn_on(port=3)")
        await device.turn_on(port=3)
        print("The method returned: Port 3 has been turned ON.")
        print("=======================")

        # 4. Verify port 3 is in the expected state (1)
        expected_state = 1
        print("Calling method: check_state(port=3) to verify state")
        port_3_verification_state = await device.check_state(port=3)
        if port_3_verification_state == expected_state:
            print("The method returned: Port 3 is in expected state: ON (1).")
        else:
            print("The method returned: Port 3 is NOT in expected state: OFF (0).")
        print("=======================")

        # 5. Turn off port 3
        print("Calling method: turn_off(port=3)")
        await device.turn_off(port=3)
        print("The method returned: Port 3 has been turned OFF.")
        print("=======================")

        # 6. Verify port 3 is in the expected state (0)
        expected_state = 0
        print("Calling method: check_state(port=3) to verify state after turning off")
        port_3_verification_state = await device.check_state(port=3)
        if port_3_verification_state == expected_state:
            print("The method returned: Port 3 is in expected state: OFF (0).")
        else:
            print("The method returned: Port 3 is NOT in expected state: ON (1).")
        print("=======================")

    except ConnectionError as ce:
        print(f"Connection error occurred: {ce}")
    except CommandError as ce:
        print(f"Command error occurred: {ce}")
    except StateError as se:
        print(f"State error occurred: {se}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        # Ensure the device session is closed
        if 'device' in locals():
            try:
                await device.close()  # Close the device session
                print("Device session closed.")
            except Exception as e:
                print(f"Error closing device session: {e}")

def main():
    ip = "172.30.47.161"  # Device IP
    asyncio.run(test_device_operations(ip))  # Run the test in an asyncio event loop

if __name__ == "__main__":
    main()  # Execute the main function
