#!/usr/bin/env python3
# test.py
# A simple script to test turning on and off port 3 and checking its state.

import asyncio
from maxsmart.device import MaxSmartDevice
from maxsmart.exceptions import ConnectionError, CommandError, DeviceOperationError


async def countdown(seconds):
    """Display a countdown."""
    for i in range(seconds, 0, -1):
        print(f"\rCountdown: {i} seconds remaining", end="")
        await asyncio.sleep(1)
    print("\rCountdown completed!                ")

async def main():
    ip = "172.30.47.78"  # Your device's IP address
    selected_port = 0
    try:
        # Create an instance of MaxSmartDevice
        print(f"Creating MaxSmartDevice instance for IP: {ip}...")
        device = MaxSmartDevice(ip)
        print("Device instantiated successfully.\n")

        '''
        # 1. Turn ON port 3
        print("Turning ON port 3...")
        await device.turn_on(port=selected_port)
        print("Port 3 has been successfully turned ON.\n")

        # 2. Check state of port 3
        print("Checking port state...")
        await device._verify_state(port=selected_port, expected_state=1)  # Use the verify method
        print("Port 3 is correctly verified as ON.\n")

        # 3. Wait for 5 seconds with a countdown
        print("Waiting for 5 seconds...")
        await countdown(1)

        # 4. Turn OFF port 3
        print("Turning OFF port 3...")
        await device.turn_off(port=selected_port)
        print("Port 3 has been successfully turned OFF.\n")

        # 5. Check state of port 3 again
        print("Checking port state...")
        await device._verify_state(port=selected_port, expected_state=0)  # Use the verify method
        print("Port 3 is correctly verified as OFF.")

        # 6. Getting wattage data
        # Call get_data to retrieve device information
        print("Getting device data...")
        data_response = await device.get_data()
        print("Response from get_data:", data_response)

        # 7. Getting statistics data
        # Retrieve statistics data
        print("Retrieving hourly statistics...")
        hourly_data = await device.get_statistics(port=selected_port,stat_type=0)  # Type 0 for hourly data
        print("Hourly Data for all ports:", hourly_data)
        '''
        print("Retrieving daily statistics...")
        daily_data1 = await device.get_statistics(port=1,stat_type=1)  # Type 1 for daily data
        daily_data2 = await device.get_statistics(port=2,stat_type=1)  # Type 1 for daily data
        daily_data3 = await device.get_statistics(port=3,stat_type=1)  # Type 1 for daily data
        daily_data4 = await device.get_statistics(port=4,stat_type=1)  # Type 1 for daily data
        daily_data5 = await device.get_statistics(port=5,stat_type=1)  # Type 1 for daily data
        daily_data6 = await device.get_statistics(port=6,stat_type=1)  # Type 1 for daily data

        '''
        print("Retrieving monthly statistics...")
        monthly_data = await device.get_statistics(port=selected_port,stat_type=2)  # Type 2 for monthly data
        print("Monthly Data for all ports:", monthly_data)
        '''        
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

