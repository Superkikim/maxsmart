# maxsmart/discovery.py

import socket
import json
import asyncio
import logging
from .device import MaxSmartDevice

class MaxSmartDiscovery:
    
    @staticmethod
    async def discover_maxsmart(ip=None, user_locale="en", timeout=None, max_attempts=None):
        """
        Discover MaxSmart devices with automatic protocol detection.
        
        Returns:
            List of devices with 'protocol' field indicating 'http', 'udp_v3', or 'unknown'
        """
        devices = await MaxSmartDiscovery._udp_discovery(ip, user_locale, timeout, max_attempts)
        
        for device in devices:
            protocol = await MaxSmartDiscovery._detect_protocol(device)
            device['protocol'] = protocol
            
        return devices
    
    @staticmethod
    async def _detect_protocol(device_info):
        """
        Test device protocol support.
        
        Returns:
            'http' for current MaxSmart API, 'udp_v3' for V3 API, or 'unknown'
        """
        ip = device_info['ip']
        sn = device_info['sn']
        
        if await MaxSmartDiscovery._test_http_protocol(ip):
            return 'http'
            
        if await MaxSmartDiscovery._test_udp_v3_protocol(ip, sn):
            return 'udp_v3'
            
        return 'unknown'
    
    @staticmethod
    async def _test_http_protocol(ip):
        """Test HTTP protocol availability with cmd=511"""
        try:
            temp_device = MaxSmartDevice(ip)
            temp_device._is_temp_device = True
            temp_device.DEFAULT_TIMEOUT = 3.0
            temp_device.RETRY_COUNT = 1
            
            await temp_device.initialize_device()
            await temp_device.get_data()
            await temp_device.close()
            
            logging.debug(f"Device {ip}: HTTP protocol detected")
            return True
            
        except Exception as e:
            logging.debug(f"Device {ip}: HTTP test failed - {e}")
            return False
    
    @staticmethod
    async def _test_udp_v3_protocol(ip, sn):
        """Test UDP V3 protocol availability with cmd=90"""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', 0))
            sock.settimeout(3.0)
            
            message = f'V3{{"sn":"{sn}", "cmd":90}}'
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, sock.sendto, message.encode('utf-8'), (ip, 8888)
            )
            
            data, addr = await loop.run_in_executor(None, sock.recvfrom, 1024)
            response = json.loads(data.decode('utf-8'))
            
            if response.get('response') == 90 and response.get('code') == 200:
                logging.debug(f"Device {ip}: UDP V3 protocol detected")
                return True
                
        except Exception as e:
            logging.debug(f"Device {ip}: UDP V3 test failed - {e}")
            
        finally:
            if sock:
                sock.close()
                
        return False


# maxsmart/device/udp_v3.py

import socket
import json
import asyncio
import logging
from ..exceptions import CommandError

class UdpV3Mixin:
    """Support for UDP V3 API commands (cmd 20, 90)"""
    
    async def _send_udp_v3_command(self, command_dict, timeout=5.0):
        """
        Send UDP V3 command and return response.
        
        Args:
            command_dict: Dict with 'sn', 'cmd', and other parameters
            timeout: Response timeout in seconds
            
        Returns:
            Dict: JSON response or raises CommandError
        """
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', 0))
            sock.settimeout(timeout)
            
            message = f'V3{json.dumps(command_dict, separators=(",", ":"))}'
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, sock.sendto, message.encode('utf-8'), (self.ip, 8888)
            )
            
            data, addr = await loop.run_in_executor(None, sock.recvfrom, 1024)
            response = json.loads(data.decode('utf-8'))
            
            logging.debug(f"UDP V3 command to {self.ip}: {message}")
            return response
            
        except Exception as e:
            logging.error(f"UDP V3 command failed for {self.ip}: {e}")
            raise CommandError(
                "ERROR_COMMAND_EXECUTION",
                self.user_locale,
                ip=self.ip,
                detail=f"UDP V3 command failed: {e}"
            )
        finally:
            if sock:
                sock.close()
    
    async def turn_on_v3(self, port):
        """Turn on port via UDP V3 cmd=20"""
        command = {
            "sn": self.sn,
            "cmd": 20,
            "port": port,
            "state": 1
        }
        
        response = await self._send_udp_v3_command(command)
        
        if response and response.get('code') == 200:
            return True
        else:
            raise CommandError(
                "ERROR_COMMAND_EXECUTION",
                self.user_locale,
                ip=self.ip,
                detail=f"Turn ON failed: {response}"
            )
    
    async def turn_off_v3(self, port):
        """Turn off port via UDP V3 cmd=20"""
        command = {
            "sn": self.sn,
            "cmd": 20,
            "port": port,
            "state": 0
        }
        
        response = await self._send_udp_v3_command(command)
        
        if response and response.get('code') == 200:
            return True
        else:
            raise CommandError(
                "ERROR_COMMAND_EXECUTION",
                self.user_locale,
                ip=self.ip,
                detail=f"Turn OFF failed: {response}"
            )
    
    async def get_data_v3(self):
        """Get device status and consumption via UDP V3 cmd=90"""
        command = {
            "sn": self.sn,
            "cmd": 90
        }
        
        response = await self._send_udp_v3_command(command)
        
        if response and response.get('code') == 200:
            data = response.get('data', {})
            raw_watt = data.get('watt', [])
            
            # Use existing conversion logic: int = milliwatts, float = watts
            converted_watt = self._convert_watt_list(raw_watt)
            
            return {
                'switch': data.get('switch', []),
                'watt': converted_watt
            }
        else:
            raise CommandError(
                "ERROR_COMMAND_EXECUTION",
                self.user_locale,
                ip=self.ip,
                detail=f"Get data failed: {response}"
            )


# maxsmart/device/core.py

from .udp_v3 import UdpV3Mixin

class MaxSmartDevice(
    CommandMixin,
    ControlMixin,
    StatisticsMixin,
    ConfigurationMixin,
    TimeMixin,
    HardwareMixin,
    AdaptivePollingMixin,
    UdpV3Mixin
):
    """
    MaxSmart device with automatic protocol support (HTTP or UDP V3).
    """
    
    def __init__(self, ip_address, protocol=None, auto_polling=False):
        """
        Initialize MaxSmart device.
        
        Args:
            ip_address: Device IP address
            protocol: 'http', 'udp_v3', or None for auto-detection
            auto_polling: Start polling automatically after initialization
        """
        self.ip = ip_address
        self.protocol = protocol
        self.user_locale = get_user_locale()
        self._auto_polling = auto_polling
        
        # Initialize default values
        self.strip_name = DEFAULT_STRIP_NAME
        self.port_names = DEFAULT_PORT_NAMES
        self.sn = None
        self.name = None
        self.version = None
        
        # Session management
        self._session = None
        self._is_initialized = False

        super().__init__()
    
    async def initialize_device(self, start_polling=None):
        """Initialize device with automatic protocol detection if needed"""
        if self._is_initialized:
            return
            
        if self.protocol is None:
            self.protocol = await self._auto_detect_protocol()
            
        if self.protocol == 'http':
            await self._initialize_http_device()
        elif self.protocol == 'udp_v3':
            await self._initialize_udp_v3_device()
        else:
            raise MaxSmartConnectionError(
                user_locale=self.user_locale,
                error_key="ERROR_UNSUPPORTED_PROTOCOL",
                ip=self.ip
            )
    
    async def _auto_detect_protocol(self):
        """Auto-detect device protocol support"""
        try:
            await self._test_http_connectivity()
            return 'http'
        except:
            pass
            
        try:
            if await self._test_udp_v3_connectivity():
                return 'udp_v3'
        except:
            pass
            
        return 'unknown'
    
    async def _initialize_udp_v3_device(self):
        """Initialize UDP V3 device (no HTTP session needed)"""
        # Get device info via discovery for UDP V3 devices
        try:
            from ..discovery import MaxSmartDiscovery
            discovery_devices = await MaxSmartDiscovery.discover_maxsmart(ip=self.ip)
            if discovery_devices:
                device_info = discovery_devices[0]
                self.sn = device_info.get("sn")
                self.name = device_info.get("name")
                self.version = device_info.get("ver")
        except Exception as e:
            logging.debug(f"Could not get device info for UDP V3 device {self.ip}: {e}")
        
        self._is_initialized = True
        logging.debug(f"Device {self.ip} initialized for UDP V3 protocol")
    
    async def turn_on(self, port):
        """Turn on port with automatic protocol routing"""
        if self.protocol == 'udp_v3':
            result = await self.turn_on_v3(port)
        else:
            result = await super().turn_on(port)
            
        self.trigger_burst_mode()
        return result
    
    async def turn_off(self, port):
        """Turn off port with automatic protocol routing"""
        if self.protocol == 'udp_v3':
            result = await self.turn_off_v3(port)
        else:
            result = await super().turn_off(port)
            
        self.trigger_burst_mode()
        return result
    
    async def get_data(self):
        """Get device data with automatic protocol routing"""
        if self.protocol == 'udp_v3':
            return await self.get_data_v3()
        else:
            return await super().get_data()


# Usage example
async def main():
    """Example usage with automatic protocol detection"""
    devices = await MaxSmartDiscovery.discover_maxsmart()
    
    for device_info in devices:
        print(f"Device: {device_info['name']} - Protocol: {device_info['protocol']}")
        
        device = MaxSmartDevice(device_info['ip'], protocol=device_info['protocol'])
        await device.initialize_device()
        
        # Same API works for both HTTP and UDP V3
        await device.turn_on(1)
        data = await device.get_data()
        print(f"Port 1 power: {data['watt'][0]:.2f}W")
        
        await device.close()