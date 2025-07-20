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
    CMD_GET_DEVICE_IDS,
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

        :param cmd: Command identifier (e.g., 511, 200, 201, 124).
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
            CMD_GET_DEVICE_IDS,
        }
        if cmd not in valid_commands:
            raise CommandError(
                "ERROR_INVALID_PARAMETERS",
                self.user_locale,
                ip=self.ip,
                detail=f"Invalid command {cmd}. Must be one of {', '.join(map(str, valid_commands))}."
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
                    ip=self.ip,
                    detail=f"Failed to serialize parameters: {e}"
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
                                "ERROR_DEVICE_NOT_FOUND",
                                ip=self.ip,
                                detail=f"Device HTTP endpoint not found (HTTP 404)"
                            )
                        elif response.status >= 500:
                            raise MaxSmartConnectionError(
                                self.user_locale,
                                "ERROR_HTTP_ERROR", 
                                ip=self.ip,
                                status=response.status,
                                detail=f"Device server error: {content[:100]}"
                            )
                        else:
                            raise CommandError(
                                "ERROR_HTTP_ERROR",
                                self.user_locale,
                                ip=self.ip,
                                status=response.status,
                                detail=f"HTTP error: {content[:100]}"
                            )

                    # Read and parse response
                    try:
                        content = await response.text()
                        if not content.strip():
                            raise CommandError(
                                "ERROR_MISSING_EXPECTED_DATA",
                                self.user_locale,
                                ip=self.ip,
                                detail="Device returned empty response"
                            )
                        
                        json_response = json.loads(content)
                        
                        # Validate response structure
                        if not isinstance(json_response, dict):
                            raise CommandError(
                                "ERROR_INVALID_JSON",
                                self.user_locale,
                                ip=self.ip,
                                detail="Response is not a JSON object"
                            )
                            
                        # Check device response code if present
                        device_code = json_response.get("code")
                        if device_code is not None and device_code != RESPONSE_CODE_SUCCESS:
                            raise CommandError(
                                "ERROR_COMMAND_EXECUTION",
                                self.user_locale,
                                ip=self.ip,
                                detail=f"Device returned error code {device_code}"
                            )
                        
                        return json_response
                        
                    except json.JSONDecodeError as e:
                        raise CommandError(
                            "ERROR_INVALID_JSON",
                            self.user_locale,
                            ip=self.ip,
                            detail=f"Invalid JSON response: {e}"
                        )
                    except UnicodeDecodeError as e:
                        raise CommandError(
                            "ERROR_RESPONSE_DECODE",
                            self.user_locale,
                            ip=self.ip,
                            detail=f"Response encoding error: {e}"
                        )
                        
            except asyncio.TimeoutError as e:
                timeout_detail = f"HTTP timeout after {timeout}s (attempt {attempt + 1}/{retries + 1}) for URL: {url}"
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    "ERROR_TIMEOUT_DETAIL",
                    ip=self.ip,
                    detail=timeout_detail
                )
                
            except aiohttp.ClientConnectionError as e:
                connection_detail = f"Connection failed: {type(e).__name__} - {str(e)} (attempt {attempt + 1}/{retries + 1})"
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    "ERROR_CONNECTION_REFUSED", 
                    ip=self.ip,
                    detail=connection_detail
                )
                
            except aiohttp.ClientError as e:
                client_detail = f"HTTP client error: {type(e).__name__} - {str(e)} (attempt {attempt + 1}/{retries + 1})"
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    "ERROR_CLIENT_ERROR",
                    ip=self.ip,
                    detail=client_detail
                )
                
            except OSError as e:
                # Network-level errors (DNS, routing, etc.)
                if "Network is unreachable" in str(e):
                    error_type = "ERROR_NETWORK_ISSUE"
                    detail = f"Network unreachable: {str(e)} (attempt {attempt + 1}/{retries + 1})"
                elif "Name or service not known" in str(e):
                    error_type = "ERROR_DNS_RESOLUTION"
                    detail = f"DNS resolution failed: {str(e)} (attempt {attempt + 1}/{retries + 1})"
                else:
                    error_type = "ERROR_SOCKET_ERROR"
                    detail = f"Socket error: {str(e)} (attempt {attempt + 1}/{retries + 1})"
                
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    error_type,
                    ip=self.ip,
                    detail=detail
                )
                
            except (CommandError, MaxSmartConnectionError):
                # Re-raise our custom exceptions immediately (no retry)
                raise
                
            except Exception as e:
                # Unexpected errors - don't retry
                raise CommandError(
                    "ERROR_UNEXPECTED",
                    self.user_locale,
                    ip=self.ip,
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
                ip=self.ip,
                detail=f"All {retries + 1} attempts failed without specific error"
            )