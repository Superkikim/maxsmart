#!/usr/bin/env python3
# test_discovery_async.py

import asyncio
import logging
from maxsmart.discovery import MaxSmartDiscovery
from maxsmart.exceptions import DiscoveryError, ConnectionError

# Configure logging
logging.basicConfig(level=logging.INFO)

# Optional: Implement a simple IP validation function
def is_valid_ip(ip):
    import re
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return re.match(pattern, ip) is not None

async def main():
    ip_address = None  # You can replace None with an actual IP address if needed
    # Validate the IP only if it's specified
    if ip_address and not is_valid_ip(ip_address):
        logging.error("Invalid IP address provided.")
        return

    try:
        # Call the discover_maxsmart method
        devices = await MaxSmartDiscovery.discover_maxsmart(ip=ip_address, user_locale='en')
        
        # Output discovered devices
        if devices:
            logging.info("Discovered MaxSmart Devices:")
            for device in devices:
                logging.info(f"Device SN: {device['sn']}, Name: {device['name']}, IP: {device['ip']}, Version: {device['ver']}")
        else:
            logging.info("No devices discovered.")
    
    except DiscoveryError as e:
        logging.error(f"Discovery error: {e}")
    except ConnectionError as e:
        logging.error(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
