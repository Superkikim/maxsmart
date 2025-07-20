# maxsmart/device/core.py

import aiohttp
import asyncio
import logging
from ..const import (
    DEFAULT_STRIP_NAME,
    DEFAULT_PORT_NAMES,
    CMD_GET_DEVICE_DATA,
    CMD_GET_DEVICE_IDS,
)
from ..utils import get_user_locale
from ..discovery import MaxSmartDiscovery
from ..exceptions import ConnectionError as MaxSmartConnectionError, DiscoveryError, DeviceOperationError
from .commands import CommandMixin
from .control import ControlMixin
from .statistics import StatisticsMixin
from .configuration import ConfigurationMixin
from .time import TimeMixin
from .hardware import HardwareMixin
from .polling import AdaptivePollingMixin


class MaxSmartDevice(
    CommandMixin, 
    ControlMixin, 
    StatisticsMixin, 
    ConfigurationMixin, 
    TimeMixin,
    HardwareMixin,
    AdaptivePollingMixin
):
    """
    Main MaxSmart device class with adaptive polling that mimics the official app behavior.
    
    This class combines all device functionality:
    - CommandMixin: Low-level command sending with robust error handling
    - ControlMixin: Port control (on/off, state checking)
    - StatisticsMixin: Statistics and power monitoring
    - ConfigurationMixin: Port names and device configuration
    - TimeMixin: Device time management
    - HardwareMixin: Hardware identification (MAC, CPU ID, etc.)
    - AdaptivePollingMixin: Adaptive polling (5s normal, 2s burst after commands)
    """

    # Session management configuration
    DEFAULT_CONNECTOR_LIMIT = 10
    DEFAULT_CONNECTOR_LIMIT_PER_HOST = 5
    SESSION_TIMEOUT = 30.0  # seconds
    
    def __init__(self, ip_address, auto_polling=False):
        """
        Initialize a MaxSmart device with robust session management.
        
        Args:
            ip_address (str): IP address of the device
            auto_polling (bool): Start polling automatically after initialization
        """
        # Validate IP address format
        import socket
        try:
            socket.inet_aton(ip_address)
        except socket.error:
            raise DeviceOperationError(
                user_locale=get_user_locale(),
                ip=ip_address,
                detail=f"Invalid IP address format: {ip_address}"
            )
            
        self.ip = ip_address
        self.user_locale = get_user_locale()  # Get user's locale from utils
        self._auto_polling = auto_polling

        # Initialize default values
        self.strip_name = DEFAULT_STRIP_NAME
        self.port_names = DEFAULT_PORT_NAMES

        # Store device information
        self.sn = None
        self.name = None
        self.version = None
        
        # Firmware-specific conversion factor (auto-detected after initialization)
        self._watt_multiplier = 1.0  # Default
        self._watt_format = "unknown"  # Will be detected

        # Session management
        self._session = None
        self._is_initialized = False

        # Initialize all mixins - call super() early so mixins can use our attributes
        super().__init__()

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

    async def initialize_device(self, start_polling=None):
        """
        Initialize device for HTTP operations only - no discovery.
        
        Args:
            start_polling (bool): Override auto_polling setting for this initialization
            
        Raises:
            MaxSmartConnectionError: If HTTP connectivity fails
        """
        if self._is_initialized:
            logging.debug(f"Device {self.ip} already initialized")
            # Start polling if requested and not already running
            should_start_polling = start_polling if start_polling is not None else self._auto_polling
            if should_start_polling and not self.is_polling:
                await self.start_adaptive_polling()
            return
            
        try:
            logging.debug(f"Initializing device {self.ip} via HTTP")
            
            # Test HTTP connectivity and get data for format detection
            response = await self._send_command(CMD_GET_DEVICE_DATA)
            data = response.get("data", {})
            
            if not data:
                raise MaxSmartConnectionError(
                    user_locale=self.user_locale,
                    error_key="ERROR_MISSING_EXPECTED_DATA",
                    ip=self.ip,
                    detail="No data received from device during initialization"
                )
                
            # Auto-detect watt format based on data sample
            watt_values = data.get("watt", [])
            
            if watt_values:
                sample_value = watt_values[0]
                logging.debug(f"Auto-detection sample: {sample_value} (type: {type(sample_value)})")
                
                # Check if it's a string (float format like "5.20")
                if isinstance(sample_value, str):
                    self._watt_multiplier = 1.0  # String floats are in watts
                    self._watt_format = "string_float"
                    logging.info(f"Auto-detected format: string float (watts) - sample: {sample_value}")
                else:
                    # It's an integer/number, check magnitude to distinguish watts vs milliwatts
                    float_value = float(sample_value)
                    if float_value > 100:  # Likely milliwatts (anything >100 is probably mW)
                        self._watt_multiplier = 0.001  # Convert milliwatts to watts
                        self._watt_format = "int_milliwatt"
                        logging.info(f"Auto-detected format: integer milliwatts - sample: {sample_value}")
                    else:
                        self._watt_multiplier = 1.0  # Integer watts (rare but possible)
                        self._watt_format = "int_watt"
                        logging.info(f"Auto-detected format: integer watts - sample: {sample_value}")
            else:
                # No watt data - use default
                self._watt_multiplier = 1.0
                self._watt_format = "default_watt"
                logging.warning(f"No watt data for format detection, using default")
                
            self._is_initialized = True
            
            logging.info(f"Device initialized: {self.ip} - Format: {self._watt_format}")
            
            # Start polling if requested
            should_start_polling = start_polling if start_polling is not None else self._auto_polling
            if should_start_polling:
                await self.start_adaptive_polling()
            
        except MaxSmartConnectionError:
            # Re-raise connection errors as-is
            raise
        except Exception as e:
            logging.error(f"Device initialization failed for {self.ip}: {e}")
            raise MaxSmartConnectionError(
                user_locale=self.user_locale,
                error_key="ERROR_NETWORK_ISSUE",
                ip=self.ip,
                detail=f"HTTP connection failed during initialization: {type(e).__name__}: {e}"
            )

    def _convert_watt(self, raw_watt):
        """
        Convert raw watt value based on firmware version.
        
        Args:
            raw_watt: Raw watt value from device
            
        Returns:
            float: Converted watt value
        """
        return float(raw_watt) * self._watt_multiplier
        
    def _convert_watt_list(self, raw_watt_list):
        """
        Convert a list of raw watt values based on firmware version.
        
        Args:
            raw_watt_list: List of raw watt values from device
            
        Returns:
            list: List of converted watt values
        """
        return [self._convert_watt(watt) for watt in raw_watt_list]

    async def setup_realtime_monitoring(self, consumption_callback=None, state_callback=None):
        """
        Setup real-time monitoring with consumption and state change detection.
        
        Args:
            consumption_callback: Called when consumption changes significantly (>1W)
            state_callback: Called when port states change
        """
        if not self.is_polling:
            await self.start_adaptive_polling()
            
        # Setup change detection callbacks
        if consumption_callback or state_callback:
            await self._setup_change_detection(consumption_callback, state_callback)
            
    async def setup_realtime_monitoring_with_baseline(self, consumption_callback=None, state_callback=None, initial_watt=None, initial_switch=None):
        """
        Setup real-time monitoring with provided baseline values.
        
        Args:
            consumption_callback: Called when consumption changes significantly
            state_callback: Called when port states change
            initial_watt: Initial watt values to use as baseline
            initial_switch: Initial switch states to use as baseline
        """
        if not self.is_polling:
            await self.start_adaptive_polling()
            
        # Setup change detection callbacks with baseline
        if consumption_callback or state_callback:
            await self._setup_change_detection_with_baseline(
                consumption_callback, 
                state_callback, 
                initial_watt or [0] * 6, 
                initial_switch or [0] * 6
            )

    async def _setup_change_detection_with_baseline(self, consumption_callback, state_callback, initial_watt, initial_switch):
        """Setup callbacks for detecting consumption and state changes with baseline."""
        last_data = {
            "watt": initial_watt[:6] if initial_watt else [0] * 6, 
            "switch": initial_switch[:6] if initial_switch else [0] * 6
        }
        
        async def change_detector(poll_data):
            try:
                device_data = poll_data.get("device_data", {})
                current_watt = device_data.get("watt", [])
                current_switch = device_data.get("switch", [])
                
                # Detect significant consumption changes (>1W)
                if consumption_callback and current_watt and len(current_watt) >= 6:
                    for i, (curr, prev) in enumerate(zip(current_watt, last_data["watt"])):
                        if abs(curr - prev) > 1.0:
                            await self._safe_callback(consumption_callback, {
                                "port": i + 1,
                                "port_name": self.port_names[i] if i < len(self.port_names) else f"Port {i+1}",
                                "previous_watt": prev,
                                "current_watt": curr,
                                "change": curr - prev,
                                "timestamp": poll_data["timestamp"]
                            })
                            
                # Detect state changes
                if state_callback and current_switch and len(current_switch) >= 6:
                    for i, (curr, prev) in enumerate(zip(current_switch, last_data["switch"])):
                        if curr != prev:
                            await self._safe_callback(state_callback, {
                                "port": i + 1,
                                "port_name": self.port_names[i] if i < len(self.port_names) else f"Port {i+1}",
                                "previous_state": prev,
                                "current_state": curr,
                                "state_text": "ON" if curr else "OFF",
                                "timestamp": poll_data["timestamp"]
                            })
                            
                # Update last known values ONLY if we have valid data
                if current_watt and len(current_watt) >= 6:
                    last_data["watt"] = current_watt[:6]  # Take only first 6 values
                if current_switch and len(current_switch) >= 6:
                    last_data["switch"] = current_switch[:6]  # Take only first 6 values
                    
            except Exception as e:
                logging.error(f"Error in change detector: {e}")
                
        self.register_poll_callback("change_detector", change_detector)
        
    async def _safe_callback(self, callback, data):
        """Safely execute a callback with error handling."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logging.warning(f"Callback error: {e}")

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
                "polling_active": self.is_polling,
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
                "polling_active": self.is_polling,
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
        polling_status = "polling" if self.is_polling else "not polling"
        return (
            f"MaxSmartDevice(ip={self.ip}, sn={self.sn}, name={self.name}, "
            f"version={self.version}, {init_status}, {polling_status})"
        )

    async def close(self):
        """
        Close the aiohttp ClientSession and cleanup resources.
        
        This method is safe to call multiple times.
        """
        # Stop polling first
        await self.stop_adaptive_polling()
        
        # Close HTTP session
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