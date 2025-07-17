# device/commands.py

import json
import asyncio
import aiohttp
from ..exceptions import CommandError, ConnectionError as MaxSmartConnectionError
from ..const import (
    CMD_SET_PORT_STATE,
    CMD_GET_DEVICE_DATA,
    CMD_SET_PORT_NAME,
    CMD_GET_STATISTICS,
    CMD_GET_DEVICE_TIME,
    RESPONSE_CODE_SUCCESS,
)


class CommandMixin:
    """Mixin class providing low-level command sending functionality with robust error handling."""
    
    # Command timeout and retry configuration
    DEFAULT_TIMEOUT = 10.0  # seconds
    RETRY_COUNT = 3
    RETRY_DELAY = 1.0  # seconds between retries
    
    async def _send_command(self, cmd, params=None, timeout=None, retries=None):
        """
        Send a command to the device with robust error handling and retry logic.

        :param cmd: Command identifier (e.g., 511, 200, 201).
        :param params: Additional parameters for the command (optional).
        :param timeout: Request timeout in seconds (default: 10s).
        :param retries: Number of retry attempts (default: 3).
        :return: Response from the device as JSON.
        
        :raises CommandError: For command validation or execution errors
        :raises MaxSmartConnectionError: For network/connectivity issues
        """
        # Use default values if not specified
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        if retries is None:
            retries = self.RETRY_COUNT
            
        # Validate the command
        valid_commands = {
            CMD_GET_DEVICE_DATA,
            CMD_GET_STATISTICS,
            CMD_SET_PORT_STATE,
            CMD_SET_PORT_NAME,
            CMD_GET_DEVICE_TIME,
        }
        if cmd not in valid_commands:
            raise CommandError(
                "ERROR_INVALID_PARAMETERS",
                self.user_locale,
                detail=f"Invalid command {cmd}. Must be one of {', '.join(map(str, valid_commands))}.",
            )

        # Construct the URL with parameters, if any
        url = f"http://{self.ip}/?cmd={cmd}"
        if params:
            try:
                url += f"&json={json.dumps(params, separators=(',', ':'))}"
            except (TypeError, ValueError) as e:
                raise CommandError(
                    "ERROR_INVALID_PARAMETERS",
                    self.user_locale,
                    detail=f"Failed to serialize parameters: {e}",
                )

        # Retry loop with exponential backoff
        last_exception = None
        for attempt in range(retries + 1):
            try:
                # Create timeout configuration
                timeout_config = aiohttp.ClientTimeout(
                    total=timeout,
                    connect=timeout / 2,  # Connection timeout is half of total
                    sock_read=timeout / 2  # Socket read timeout
                )
                
                # Make the HTTP request
                async with self.session.get(url, timeout=timeout_config) as response:
                    # Check HTTP status
                    if response.status != RESPONSE_CODE_SUCCESS:
                        content = await response.text()
                        if response.status == 404:
                            raise MaxSmartConnectionError(
                                self.user_locale,
                                "ERROR_NETWORK_ISSUE",
                                detail=f"Device not found at {self.ip} (HTTP 404)"
                            )
                        elif response.status >= 500:
                            raise MaxSmartConnectionError(
                                self.user_locale,
                                "ERROR_NETWORK_ISSUE", 
                                detail=f"Device server error (HTTP {response.status})"
                            )
                        else:
                            raise CommandError(
                                "ERROR_COMMAND_EXECUTION",
                                self.user_locale,
                                detail=f"HTTP {response.status}: {content[:100]}",
                            )

                    # Read and parse response
                    try:
                        content = await response.text()
                        if not content.strip():
                            raise CommandError(
                                "ERROR_COMMAND_EXECUTION",
                                self.user_locale,
                                detail="Device returned empty response",
                            )
                        
                        json_response = json.loads(content)
                        
                        # Validate response structure
                        if not isinstance(json_response, dict):
                            raise CommandError(
                                "ERROR_INVALID_JSON",
                                self.user_locale,
                                detail="Response is not a JSON object",
                            )
                            
                        # Check device response code if present
                        device_code = json_response.get("code")
                        if device_code is not None and device_code != RESPONSE_CODE_SUCCESS:
                            raise CommandError(
                                "ERROR_COMMAND_EXECUTION",
                                self.user_locale,
                                detail=f"Device returned error code {device_code}",
                            )
                        
                        return json_response
                        
                    except json.JSONDecodeError as e:
                        raise CommandError(
                            "ERROR_INVALID_JSON",
                            self.user_locale,
                            detail=f"Invalid JSON response: {e}",
                        )
                    except UnicodeDecodeError as e:
                        raise CommandError(
                            "ERROR_COMMAND_EXECUTION",
                            self.user_locale,
                            detail=f"Response encoding error: {e}",
                        )
                        
            except asyncio.TimeoutError as e:
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    "ERROR_NETWORK_ISSUE",
                    detail=f"Request timeout after {timeout}s (attempt {attempt + 1}/{retries + 1})"
                )
                
            except aiohttp.ClientConnectionError as e:
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    "ERROR_NETWORK_ISSUE", 
                    detail=f"Connection failed: {type(e).__name__} (attempt {attempt + 1}/{retries + 1})"
                )
                
            except aiohttp.ClientError as e:
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    "ERROR_NETWORK_ISSUE",
                    detail=f"HTTP client error: {type(e).__name__} (attempt {attempt + 1}/{retries + 1})"
                )
                
            except OSError as e:
                # Network-level errors (DNS, routing, etc.)
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    "ERROR_NETWORK_ISSUE",
                    detail=f"Network error: {e} (attempt {attempt + 1}/{retries + 1})"
                )
                
            except (CommandError, MaxSmartConnectionError):
                # Re-raise our custom exceptions immediately (no retry)
                raise
                
            except Exception as e:
                # Unexpected errors - don't retry
                raise CommandError(
                    "ERROR_UNEXPECTED",
                    self.user_locale,
                    detail=f"Unexpected error: {type(e).__name__}: {e}"
                )
            
            # If this wasn't the last attempt, wait before retrying
            if attempt < retries:
                delay = self.RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                await asyncio.sleep(delay)
        
        # All retries exhausted, raise the last exception
        if last_exception:
            raise last_exception
        else:
            # This should never happen, but just in case
            raise MaxSmartConnectionError(
                self.user_locale,
                "ERROR_NETWORK_ISSUE",
                detail=f"All {retries + 1} attempts failed"
            )