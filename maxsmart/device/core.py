# device/core.py

import aiohttp
import asyncio
import logging
from ..const import (
    DEFAULT_STRIP_NAME,
    DEFAULT_PORT_NAMES,
)
from ..utils import get_user_locale
from ..discovery import MaxSmartDiscovery
from ..exceptions import ConnectionError as MaxSmartConnectionError, DiscoveryError
from .commands import CommandMixin
from .control import ControlMixin
from .statistics import StatisticsMixin
from .configuration import ConfigurationMixin
from .time import TimeMixin


class MaxSmartDevice(CommandMixin, ControlMixin, StatisticsMixin, ConfigurationMixin, TimeMixin):
    """
    Main MaxSmart device class providing all functionality through mixins.
    
    This class combines all device functionality:
    - CommandMixin: Low-level command sending with robust error handling
    - ControlMixin: Port control (on/off, state checking)
    - StatisticsMixin: Statistics and power monitoring
    - ConfigurationMixin: Port names and device configuration
    - TimeMixin: Device time management
    """

    # Session management configuration
    DEFAULT_CONNECTOR_LIMIT = 10
    DEFAULT_CONNECTOR_LIMIT_PER_HOST = 5
    SESSION_TIMEOUT = 30.0  # seconds
    
    def __init__(self, ip_address):
        """
        Initialize a MaxSmart device with robust session management.
        
        Args:
            ip_address (str): IP address of the device
        """
        # Validate IP address format
        import socket
        try:
            socket.inet_aton(ip_address)
        except socket.error:
            raise ValueError(f"Invalid IP address format: {ip_address}")
            
        self.ip = ip_address
        self.user_locale = get_user_locale()  # Get user's locale from utils

        # Initialize default values
        self.strip_name = DEFAULT_STRIP_NAME
        self.port_names = DEFAULT_PORT_NAMES

        # Store device information
        self.sn = None
        self.name = None
        self.version = None

        # Session management
        self._session = None
        self._is_initialized = False

    @property
    def session(self):
        """
        Get aiohttp session, creating it if necessary.
        
        Returns:
            aiohttp.ClientSession: Configured HTTP session
        """
        if self._session is None or self._session.closed:
            # Create connector with reasonable limits
            connector = aiohttp.TCPConnector(
                limit=self.DEFAULT_CONNECTOR_LIMIT,
                limit_per_host=self.DEFAULT_CONNECTOR_LIMIT_PER_HOST,
                ttl_dns_cache=300,  # DNS cache for 5 minutes
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            # Create session with timeouts
            timeout = aiohttp.ClientTimeout(
                total=self.SESSION_TIMEOUT,
                connect=10.0,
                sock_read=10.0
            )
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'MaxSmart-Python/2.0.0-beta2'}
            )
            
            logging.debug(f"Created new HTTP session for device {self.ip}")
                
        return self._session

    async def initialize_device(self):
        """
        Perform device discovery and initialize properties with robust error handling.
        
        Raises:
            DiscoveryError: If device discovery fails
            MaxSmartConnectionError: If network connectivity issues occur
        """
        if self._is_initialized:
            logging.debug(f"Device {self.ip} already initialized")
            return
            
        try:
            discovery = MaxSmartDiscovery()
            devices = await discovery.discover_maxsmart(
                ip=self.ip, user_locale=self.user_locale, timeout=3.0
            )

            if not devices:
                raise DiscoveryError(
                    "ERROR_NO_DEVICES_FOUND", 
                    self.user_locale,
                    detail=f"No device found at IP {self.ip}"
                )
                
            # Use first (and should be only) device for unicast discovery
            primary_device = devices[0]
            self.sn = primary_device.get("sn", "")
            self.name = primary_device.get("name", "")
            self.version = primary_device.get("ver", "")

            # Set the strip name to the device name (for port 0)
            self.strip_name = self.name if self.name else DEFAULT_STRIP_NAME

            # Logic to set port_names based on the number of ports as inferred from the sn
            if "pname" in primary_device and primary_device["pname"]:
                self.port_names = primary_device["pname"]  # Use pname if available
            else:
                # Check 4th character to determine number of ports
                if self.sn and len(self.sn) >= 4:  # Make sure sn is long enough
                    num_ports_char = self.sn[3]  # 4th character, index 3
                    if num_ports_char == '6':
                        self.port_names = DEFAULT_PORT_NAMES  # Use default names for 6 ports
                    elif num_ports_char == '1':
                        self.port_names = [self.name or "Port 1"]  # Use list with name for single port
                    else:
                        self.port_names = DEFAULT_PORT_NAMES  # Default if other model
                else:
                    self.port_names = DEFAULT_PORT_NAMES  # Default if sn too short or empty

            self._is_initialized = True
            logging.info(f"Device initialized: {self.name} ({self.ip}) - FW: {self.version}")
            
        except (DiscoveryError, MaxSmartConnectionError):
            # Re-raise discovery and connection errors as-is
            raise
        except Exception as e:
            # Wrap unexpected errors
            raise DiscoveryError(
                "ERROR_UNEXPECTED",
                self.user_locale,
                detail=f"Device initialization failed: {type(e).__name__}: {e}"
            )

    async def health_check(self):
        """
        Perform a basic health check to verify device connectivity.
        
        Returns:
            dict: Health check results with status and response time
            
        Raises:
            MaxSmartConnectionError: If device is not reachable
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Try to get basic device data as health check
            await self.get_data()
            response_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "status": "healthy",
                "response_time": round(response_time * 1000, 2),  # milliseconds
                "device": {
                    "name": self.name,
                    "ip": self.ip,
                    "firmware": self.version
                }
            }
            
        except Exception as e:
            response_time = asyncio.get_event_loop().time() - start_time
            return {
                "status": "unhealthy",
                "response_time": round(response_time * 1000, 2),  # milliseconds
                "error": str(e),
                "device": {
                    "name": self.name,
                    "ip": self.ip,
                    "firmware": self.version
                }
            }
        
    def __repr__(self):
        """String representation of the device."""
        init_status = "initialized" if self._is_initialized else "not initialized"
        return (
            f"MaxSmartDevice(ip={self.ip}, sn={self.sn}, name={self.name}, "
            f"version={self.version}, {init_status})"
        )

    async def close(self):
        """
        Close the aiohttp ClientSession and cleanup resources.
        
        This method is safe to call multiple times.
        """
        if self._session and not self._session.closed:
            try:
                await self._session.close()
                logging.debug(f"Closed HTTP session for device {self.ip}")
            except Exception as e:
                logging.warning(f"Error closing session for device {self.ip}: {e}")
            finally:
                self._session = None
                
        self._is_initialized = False
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize_device()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.close()