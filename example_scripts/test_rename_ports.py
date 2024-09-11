#!/usr/bin/env python3
# test_rename_ports.py

import asyncio
from maxsmart import MaxSmartDevice
from maxsmart.exceptions import StateError, CommandError, FirmwareError

async def main():
    # Create an instance of MaxSmartDevice with the IP 172.30.47.78
    device_ip = "172.30.47.78"  # This is the correct IP
    device = MaxSmartDevice(device_ip)
    
    try:
        # Initialize the device
        await device.initialize_device()
        
        # Change the port names
        print("Renaming ports...")
        
        try:
            await device.change_port_name(3, "Not  Port 4")  # Rename Port 
 
            print("Port names changed successfully.")
        
        except FirmwareError as e:
            print("Firmware Error:")
            print(f"  {e}")
            print("Unable to rename ports due to firmware version limitations.")
        except (StateError, CommandError) as e:
            print(f"An error occurred while changing port names: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        # Close the session when done
        await device.close()

if __name__ == "__main__":
    asyncio.run(main())  # Run the main async function