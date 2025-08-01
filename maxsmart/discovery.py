# discovery.py

import asyncio
import socket
import json
import datetime
import os
import logging

from .const import (
    DEFAULT_TARGET_IP,
    UDP_PORT,
    UDP_TIMEOUT,
    DISCOVERY_MESSAGE,
    CMD_GET_DEVICE_IDS
)

from .exceptions import (
    DiscoveryError,
    ConnectionError,
    UdpTimeoutInfo
)


class MaxSmartDiscovery:
    """MaxSmart device discovery with robust error handling and hardware ID enhancement."""
    
    # Discovery configuration
    DEFAULT_DISCOVERY_TIMEOUT = 2.0  # seconds - devices respond very quickly
    MAX_DISCOVERY_ATTEMPTS = 3
    SOCKET_RETRY_DELAY = 0.5  # seconds
    
    @staticmethod
    async def discover_maxsmart(ip=None, user_locale="en", timeout=None, max_attempts=None, enhance_with_hardware_ids=True):
        """
        Discover MaxSmart devices with robust error handling and optional hardware ID enhancement.
        
        :param ip: Specific IP to query (None for broadcast)
        :param user_locale: User locale for error messages
        :param timeout: Discovery timeout in seconds
        :param max_attempts: Maximum discovery attempts
        :param enhance_with_hardware_ids: Fetch hardware IDs (CPU, MAC) via command 124
        :return: List of discovered devices with enhanced identifiers
        
        :raises DiscoveryError: For discovery-related errors
        :raises ConnectionError: For network connectivity issues
        """
        # Use default values if not specified
        if timeout is None:
            timeout = float(os.getenv("UDP_TIMEOUT", MaxSmartDiscovery.DEFAULT_DISCOVERY_TIMEOUT))
        if max_attempts is None:
            max_attempts = MaxSmartDiscovery.MAX_DISCOVERY_ATTEMPTS
            
        target_ip = ip if ip else DEFAULT_TARGET_IP
        is_broadcast = (ip is None or ip == DEFAULT_TARGET_IP)
        
        # Validate IP format for unicast
        if ip and ip != DEFAULT_TARGET_IP:
            try:
                socket.inet_aton(ip)
            except socket.error:
                raise DiscoveryError(
                    "ERROR_INVALID_IP_FORMAT",
                    user_locale,
                    ip=ip,
                    detail=f"Invalid IP address format: {ip}"
                )
        
        # Prepare discovery message
        current_time = datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S')
        message = DISCOVERY_MESSAGE.format(datetime=current_time)
        
        maxsmart_devices = []
        last_exception = None
        
        # Discovery attempt loop
        for attempt in range(max_attempts):
            try:
                devices = await MaxSmartDiscovery._single_discovery_attempt(
                    target_ip, message, timeout, user_locale, is_broadcast
                )
                
                if devices:
                    maxsmart_devices.extend(devices)
                    
                # For unicast, one successful response is enough
                if not is_broadcast and devices:
                    break
                    
                # For broadcast, continue collecting responses
                if is_broadcast and attempt == 0:
                    # First attempt successful, but continue for more devices
                    continue
                    
            except (ConnectionError, DiscoveryError) as e:
                last_exception = e
                logging.debug(f"Discovery attempt {attempt + 1} failed: {e}")
                
                # For unicast failures, wait before retry
                if not is_broadcast and attempt < max_attempts - 1:
                    await asyncio.sleep(MaxSmartDiscovery.SOCKET_RETRY_DELAY * (attempt + 1))
                    
            except Exception as e:
                # Unexpected errors
                raise DiscoveryError(
                    "ERROR_DISCOVERY_FAILED",
                    user_locale,
                    detail=f"Unexpected discovery error: {type(e).__name__}: {e}"
                )
        
        # Remove duplicates based on IP address
        seen_ips = set()
        unique_devices = []
        for device in maxsmart_devices:
            if device["ip"] not in seen_ips:
                seen_ips.add(device["ip"])
                unique_devices.append(device)
        
        # Enhance with hardware identifiers if requested
        if enhance_with_hardware_ids and unique_devices:
            unique_devices = await MaxSmartDiscovery._enhance_with_hardware_ids(
                unique_devices, user_locale
            )
        
        # Log discovery results
        if unique_devices:
            logging.info(f"Found {len(unique_devices)} MaxSmart device(s)")
            return unique_devices
        else:
            # No devices found after all attempts
            if last_exception:
                raise last_exception
            else:
                # Timeout without errors - this is normal for broadcast discovery
                if is_broadcast:
                    UdpTimeoutInfo(user_locale)  # Log timeout info
                    return []  # Return empty list for broadcast timeout
                else:
                    raise DiscoveryError("ERROR_NO_DEVICES_FOUND", user_locale)
    
    @staticmethod
    async def _single_discovery_attempt(target_ip, message, timeout, user_locale, is_broadcast):
        """
        Perform a single discovery attempt with proper error handling.
        
        :param target_ip: Target IP address
        :param message: Discovery message to send
        :param timeout: Timeout for this attempt
        :param user_locale: User locale for error messages
        :param is_broadcast: Whether this is a broadcast discovery
        :return: List of discovered devices in this attempt
        """
        loop = asyncio.get_event_loop()
        sock = None
        devices = []
        
        try:
            # Create and configure socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            if is_broadcast:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
            sock.setblocking(False)
            
            # Bind to any available port
            try:
                sock.bind(('', 0))
            except OSError as e:
                raise ConnectionError(
                    user_locale=user_locale,
                    error_key="ERROR_NETWORK_ISSUE",
                    ip=target_ip,
                    detail=f"Failed to bind socket: {e}"
                )
            
            # Send discovery message
            try:
                await loop.run_in_executor(
                    None, sock.sendto, message.encode('utf-8'), (target_ip, UDP_PORT)
                )
            except OSError as e:
                if "Network is unreachable" in str(e):
                    raise ConnectionError(
                        user_locale=user_locale,
                        error_key="ERROR_NETWORK_ISSUE",
                        ip=target_ip,
                        detail="Network unreachable - check network connectivity"
                    )
                elif "No route to host" in str(e):
                    raise ConnectionError(
                        user_locale=user_locale,
                        error_key="ERROR_NETWORK_ISSUE", 
                        ip=target_ip,
                        detail=f"No route to host {target_ip}"
                    )
                else:
                    raise ConnectionError(
                        user_locale=user_locale,
                        error_key="ERROR_NETWORK_ISSUE",
                        ip=target_ip,
                        detail=f"Failed to send discovery message: {e}"
                    )
            
            # Set socket timeout for receiving
            sock.settimeout(timeout)
            
            # Collect responses
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                try:
                    # Receive response
                    data, addr = await loop.run_in_executor(None, sock.recvfrom, 1024)
                    
                    try:
                        # Decode and parse response
                        raw_result = data.decode("utf-8", errors="replace")
                        json_data = json.loads(raw_result)
                        device_data = json_data.get("data", {})
                        
                        if device_data:
                            # Extract device information
                            device = {
                                "sn": device_data.get("sn", ""),
                                "name": device_data.get("name", ""),
                                "pname": device_data.get("pname", []),
                                "ip": addr[0],
                                "ver": device_data.get("ver", ""),
                            }
                            devices.append(device)
                            
                            # For unicast, one response is usually enough
                            if not is_broadcast:
                                break
                                
                    except json.JSONDecodeError as e:
                        logging.debug(f"Received invalid JSON from {addr[0]}: {e}")
                        continue
                    except UnicodeDecodeError as e:
                        logging.debug(f"Received invalid UTF-8 from {addr[0]}: {e}")
                        continue
                        
                except socket.timeout:
                    # Normal timeout - stop collecting responses
                    break
                except OSError as e:
                    # Socket errors during receive
                    if "Resource temporarily unavailable" in str(e):
                        # Normal case when no more data available
                        break
                    else:
                        logging.debug(f"Socket error during receive: {e}")
                        break
                        
        except Exception as e:
            # Handle any other unexpected errors
            raise DiscoveryError(
                "ERROR_DISCOVERY_FAILED",
                user_locale,
                detail=f"Discovery attempt failed: {type(e).__name__}: {e}"
            )
        finally:
            # Always close the socket
            if sock:
                try:
                    sock.close()
                except:
                    pass  # Ignore close errors
        
        return devices

    @staticmethod
    async def _enhance_with_hardware_ids(devices, user_locale):
        """
        Enhance device list with hardware identifiers from command 124.
        
        :param devices: List of devices from UDP discovery
        :param user_locale: User locale for error messages
        :return: Enhanced device list with hardware IDs
        """
        enhanced_devices = []
        
        # Import here to avoid circular imports
        from .device import MaxSmartDevice
        
        for device in devices:
            enhanced_device = device.copy()
            ip = device["ip"]
            
            try:
                # Create temporary device instance to fetch hardware IDs
                temp_device = MaxSmartDevice(ip)
                temp_device._is_temp_device = True  # Mark as temp to avoid circular calls
                await temp_device.initialize_device()
                
                # Get hardware identifiers
                try:
                    hw_ids = await temp_device.get_device_identifiers()
                    
                    # Add hardware identifiers to device info
                    enhanced_device["hw_ids"] = hw_ids
                    enhanced_device["cpuid"] = hw_ids.get("cpuid", "")
                    enhanced_device["pclmac"] = hw_ids.get("pclmac", "")
                    enhanced_device["pcldak"] = hw_ids.get("pcldak", "")
                    enhanced_device["cloud_server"] = hw_ids.get("cloud_server", "")
                    
                    # Generate best unique identifier
                    unique_id = await temp_device.get_unique_identifier()
                    enhanced_device["unique_id"] = unique_id
                    
                    # Check if UDP serial is reliable
                    udp_sn = device.get("sn", "")
                    sn_reliable = MaxSmartDiscovery._is_serial_reliable(udp_sn)
                    enhanced_device["sn_reliable"] = sn_reliable
                    
                    # If UDP serial is unreliable, prefer CPU ID as primary identifier
                    if not sn_reliable and hw_ids.get("cpuid"):
                        enhanced_device["primary_id"] = hw_ids["cpuid"]
                        enhanced_device["primary_id_type"] = "cpuid"
                    else:
                        enhanced_device["primary_id"] = udp_sn
                        enhanced_device["primary_id_type"] = "udp_serial"
                    
                    logging.debug(f"Enhanced device {ip}: {unique_id} (reliable_sn={sn_reliable})")
                    
                except Exception as e:
                    # Hardware ID fetch failed, use device as-is
                    logging.debug(f"Failed to get hardware IDs for {ip}: {e}")
                    enhanced_device["hw_ids"] = {}
                    enhanced_device["unique_id"] = f"ip_{ip.replace('.', '_')}"
                    enhanced_device["sn_reliable"] = MaxSmartDiscovery._is_serial_reliable(device.get("sn", ""))
                    
            except Exception as e:
                # Device initialization failed, use device as-is
                logging.debug(f"Failed to initialize device {ip} for enhancement: {e}")
                enhanced_device["hw_ids"] = {}
                enhanced_device["unique_id"] = f"ip_{ip.replace('.', '_')}"
                enhanced_device["sn_reliable"] = MaxSmartDiscovery._is_serial_reliable(device.get("sn", ""))
                
            finally:
                # Always cleanup temp device
                try:
                    if 'temp_device' in locals():
                        await temp_device.close()
                except:
                    pass
                    
            enhanced_devices.append(enhanced_device)
            
        return enhanced_devices

    @staticmethod
    def _is_serial_reliable(sn):
        """
        Check if a UDP serial number is reliable/usable.
        
        :param sn: Serial number from UDP discovery
        :return: True if serial is reliable, False if corrupted/empty
        """
        return (
            sn and 
            isinstance(sn, str) and 
            sn.strip() and 
            len(sn) > 3 and  # Minimum reasonable length
            all(ord(c) < 128 for c in sn) and  # ASCII only
            sn.isprintable() and  # Printable characters
            not any(c in sn for c in ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06'])  # No control chars
        )
