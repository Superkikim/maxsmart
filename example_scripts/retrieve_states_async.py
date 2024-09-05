#!/usr/bin/env python3
import sys
import asyncio
from maxsmart import MaxSmartDiscovery, MaxSmartDevice
from maxsmart.exceptions import DiscoveryError, ConnectionError
from aiohttp import ClientError  # Import ClientError for HTTP-related errors

async def retrieve_strip_states(strip_name):
    print(f"Starting to discover MaxSmart devices...")
    
    # Discover MaxSmart devices
    discovery = MaxSmartDiscovery()
    devices = await discovery.discover_maxsmart()  # Ensure this is an async method
    print(f"Devices discovered: {devices}")

    if devices:
        specified_strip = None

        print(f"Looking for strip: {strip_name}")
        for device in devices:
            print(f"Checking device: {device['name']}")
            if device["name"].lower() == strip_name.lower():
                specified_strip = device
                print(f"Found specified strip: {specified_strip}")
                break

        if specified_strip:
            ip = specified_strip["ip"]
            print(f"IP address of specified strip: {ip}")

            # Create MaxSmartDevice object for the specified strip
            specified_maxsmart = MaxSmartDevice(ip)

            try:
                # Retrieve the state of all ports in a single call
                print("Retrieving port state...")
                port_state = await specified_maxsmart.check_state(port=3)  # Use check_ports_state instead
                print(f"Port state: {port_state}")

                # Retrieve the state of the strip itself (assumes you have a method like check_state())
                print("Retrieving strip state...")
                strip_state = await specified_maxsmart.check_state()  # Update to call the correct method
                print(f"Strip state: {strip_state}")

            except ClientError as ce:
                print(f"HTTP error occurred: {ce}")  # Handle HTTP-related errors
            except Exception as e:
                print(f"An error occurred while retrieving states: {e}")
            finally:
                await specified_maxsmart.close()  # Close the connection when done
        else:
            print(f"{strip_name} strip not found.")
    else:
        print("No MaxSmart devices found.")

async def main():
    if len(sys.argv) != 2:
        print("Usage: python retrieve_states_async.py <strip_name>")
        return

    strip_name = sys.argv[1]

    try:
        await retrieve_strip_states(strip_name)
    except ConnectionError as ce:
        print(f"Connection error occurred: {ce}")
    except DiscoveryError as de:
        print(f"Discovery error occurred: {de}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
