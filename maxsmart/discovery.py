# discovery.py

import json
import socket
import datetime
import logging


class MaxSmartDiscovery:
    @staticmethod
    def discover_maxsmart(ip=None):
        maxsmart_devices = []

        message = f"00dv=all,{datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S')};"

        if ip is None:
            target_ip = "255.255.255.255"
        else:
            target_ip = ip

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(message.encode(), (target_ip, 8888))
            sock.settimeout(2)

            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    raw_result = data.decode(
                        "utf-8", errors="replace"
                    )  # Use 'replace' to handle encoding errors

                    json_data = json.loads(raw_result)
                    ip_address = addr[0]
                    device_data = json_data.get("data")

                    if device_data:
                        sn = device_data.get("sn")
                        name = device_data.get("name")
                        pname = device_data.get("pname")
                        ver = device_data.get("ver")

                        maxsmart_device = {
                            "sn": sn,
                            "name": name,
                            "pname": pname,
                            "ip": ip_address,
                            "ver": ver,
                        }

                        maxsmart_devices.append(maxsmart_device)

                    if ip not in (None, "255.255.255.255"):  # Check if IP is specified
                        break  # Exit loop after receiving the first response

                except socket.timeout:
                    break

                except json.JSONDecodeError:
                    print(
                        f"Failed to decode JSON from raw result: {raw_result}"
                    )  # Handle JSON decode errors
                except Exception as e:
                    print(f"An error occurred: {str(e)}")  # General error handling

        return maxsmart_devices

    @staticmethod
    def _validate_firmware_versions(devices):
        for device in devices:
            firmware_version = device.get("ver")
            if firmware_version != "1.30":
                raise ValueError(
                    f"Device with IP {device['ip']} has firmware version {firmware_version}. This module has been tested with MaxSmart devices with firmware version 1.30."
                )
