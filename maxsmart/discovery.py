# discovery.py

import json
import socket
import datetime
import logging
from .exceptions import DiscoveryError, ConnectionError, FirmwareError


class MaxSmartDiscovery:
    @staticmethod
    def discover_maxsmart(ip=None):
        maxsmart_devices = []
        message = f"00dv=all,{datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S')};"
        target_ip = ip if ip else "255.255.255.255"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(message.encode(), (target_ip, 8888))
                sock.settimeout(2)
                
                while True:
                    try:
                        data, addr = sock.recvfrom(1024)
                        raw_result = data.decode("utf-8", errors="replace")
                        json_data = json.loads(raw_result)
                        ip_address = addr[0]
                        device_data = json_data.get("data", {})

                        if device_data:
                            sn = device_data.get("sn", "N/A")
                            name = device_data.get("name", "Unknown")
                            pname = device_data.get("pname", "N/A")
                            ver = device_data.get("ver", "N/A")

                            maxsmart_device = {
                                "sn": sn,
                                "name": name,
                                "pname": pname,
                                "ip": ip_address,
                                "ver": ver,
                            }
                            maxsmart_devices.append(maxsmart_device)

                        # Check if a specific IP is specified to stop after the first response
                        if ip and ip != "255.255.255.255":
                            break  # Exit loop after receiving the first response

                    except socket.timeout:
                        if not maxsmart_devices:
                            logging.info("No devices found during discovery. Trying again...")
                        break  # Exit if the timeout occurs

                    except json.JSONDecodeError:
                        logging.error(f"Failed to decode JSON from raw result: {raw_result}")
                        raise DiscoveryError("Received invalid JSON data.")  # Raise a custom error

                    except KeyError as key_error:
                        logging.error(f"Expected key not found in the JSON response: {key_error}")
                        raise DiscoveryError("Missing expected data in device response.")

        except OSError as e:
            raise ConnectionError(f"Network issue encountered: {str(e)}")  # Raise a custom error for network issues

        if not maxsmart_devices:
            raise DiscoveryError("No MaxSmart devices found.")  # Raise if no devices were discovered

        return maxsmart_devices


    @staticmethod
    def _validate_firmware_versions(devices):
        for device in devices:
            firmware_version = device.get("ver", "N/A")  # Default to "N/A" if not found
            if firmware_version == "1.30":
                continue  # Safe to proceed with version 1.30
            else:
                # Handle devices with non-1.30 firmware versions
                logging.warning(
                    f"Device with IP {device['ip']} has firmware version {firmware_version}. "
                    f"This module has not been tested with firmware version {firmware_version}."
                )
                raise FirmwareError(
                    f"Device with IP {device['ip']} has incompatible firmware version {firmware_version}. "
                    "This module has been tested with MaxSmart devices with firmware version 1.30."
                )
