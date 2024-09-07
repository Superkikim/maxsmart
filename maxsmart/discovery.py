import asyncio
import socket
import json
import datetime

from .const import (
    DEFAULT_TARGET_IP,
    UDP_PORT,
    UDP_TIMEOUT,
    DISCOVERY_MESSAGE
)

from .exceptions import (
    DiscoveryError,
    ConnectionError,
    UdpTimeoutInfo
)

class MaxSmartDiscovery:
    @staticmethod
    async def discover_maxsmart(ip=None, user_locale="en"):  # Ensure user_locale is set
        maxsmart_devices = []
        message = DISCOVERY_MESSAGE.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S'))
        target_ip = ip if ip else DEFAULT_TARGET_IP

        loop = asyncio.get_event_loop()

        # Create a new UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setblocking(False)  # Make socket non-blocking

        try:
            # Send the discovery message
            await loop.run_in_executor(None, sock.sendto, message.encode(), (target_ip, UDP_PORT))
            sock.settimeout(UDP_TIMEOUT)

            while True:
                try:
                    # Receive responses
                    data, addr = await loop.run_in_executor(None, sock.recvfrom, 1024)
                    raw_result = data.decode("utf-8", errors="replace")
                    json_data = json.loads(raw_result)
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
                            "ip": addr[0],
                            "ver": ver,
                        }
                        maxsmart_devices.append(maxsmart_device)

                    # Check if a specific IP is specified to stop after the first response
                    if ip and ip != DEFAULT_TARGET_IP:
                        break  # Exit loop after receiving the first response

                except socket.timeout:
                    if not maxsmart_devices:
                        # Log the UDP timeout situation
                        UdpTimeoutInfo(user_locale)  # Raise the timeout error if no devices are found
                    break  # Exit if the timeout occurs

                except json.JSONDecodeError:
                    # Raise the error using the utility method, which will also log the localized error message
                    raise DiscoveryError("ERROR_INVALID_JSON", user_locale)

                except KeyError as key_error:
                    # Raise a custom error using the utility method
                    raise DiscoveryError("ERROR_MISSING_EXPECTED_DATA", user_locale)  # Ensure correct usage

        except OSError as e:
            # Raise a custom error for network issues, ensuring user_locale is passed
            raise ConnectionError(user_locale=user_locale, error_key="ERROR_NETWORK_ISSUE", detail=str(e))

        finally:
            sock.close()  # Ensure the socket is closed

        if not maxsmart_devices:
            # Raise if no devices were discovered
            raise DiscoveryError("ERROR_NO_DEVICES_FOUND", user_locale)  # Ensure correct usage

        return maxsmart_devices
