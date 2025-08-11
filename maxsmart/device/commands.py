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
        Routes to HTTP or UDP V3 based on device protocol.

        :param cmd: Command identifier (e.g., 511, 200, 201, 124).
        :param params: Additional parameters for the command (optional).
        :param timeout: Request timeout in seconds (default: 10s).
        :param retries: Number of retry attempts (default: 3).
        :return: Response from the device as JSON.

        :raises CommandError: For command validation or execution errors
        :raises MaxSmartConnectionError: For network/connectivity issues
        """
        # Check if command requires specific firmware version
        from ..const import IN_DEVICE_NAME_VERSION
        statistics_commands = [201, 510]  # Commands that require specific firmware (exclude 124 - hardware IDs)

        if cmd in statistics_commands:
            if not self.version or self.version != IN_DEVICE_NAME_VERSION:
                from ..exceptions import StateError
                raise StateError(
                    "ERROR_FEATURE_NOT_AVAILABLE",
                    self.user_locale,
                    detail=f"Statistics commands require firmware v{IN_DEVICE_NAME_VERSION}. Current version: {self.version or 'Unknown'}"
                )

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

        # Route to appropriate protocol
        import logging
        protocol = getattr(self, 'protocol', None)
        logging.debug(f"_send_command routing: protocol={protocol}, cmd={cmd}, ip={self.ip}")

        if protocol == 'udp_v3':
            logging.debug(f"Routing to UDP V3 for {self.ip}")
            return await self._send_udp_v3_command(cmd, params, timeout, retries)
        else:
            logging.debug(f"Routing to HTTP for {self.ip} (protocol={protocol})")
            return await self._send_http_command(cmd, params, timeout, retries)

    async def _send_http_command(self, cmd, params=None, timeout=None, retries=None):
        """Send command via HTTP protocol."""
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

    async def _send_udp_v3_command(self, cmd, params=None, timeout=None, retries=None):
        """Send command via UDP V3 protocol."""
        import socket
        import asyncio
        from ..const import UDP_PORT

        if not hasattr(self, 'sn') or not self.sn:
            raise CommandError(
                "ERROR_INVALID_PARAMETERS",
                self.user_locale,
                ip=self.ip,
                detail="Serial number required for UDP V3 commands"
            )

        last_exception = None

        for attempt in range(retries + 1):
            try:
                # Construct UDP V3 message (map HTTP-style command IDs to UDP V3 equivalents)
                udp_cmd = cmd
                try:
                    # Known mapping: HTTP 511 (CMD_GET_DEVICE_DATA) -> UDP V3 90
                    if cmd == CMD_GET_DEVICE_DATA:
                        udp_cmd = 90  # UDP V3 data command
                except NameError:
                    pass  # Fallback to original cmd if constants not in scope

                payload = {"sn": self.sn, "cmd": udp_cmd}
                if params:
                    payload.update(params)

                message = f"V3{json.dumps(payload, separators=(',', ':'))}"

                # Create UDP socket
                loop = asyncio.get_event_loop()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setblocking(False)

                try:
                    # Send UDP message
                    await loop.run_in_executor(
                        None, sock.sendto, message.encode('utf-8'), (self.ip, UDP_PORT)
                    )

                    # Set timeout and receive response
                    sock.settimeout(timeout or self.DEFAULT_TIMEOUT)
                    data, addr = await loop.run_in_executor(None, sock.recvfrom, 1024)

                    # Parse response
                    response_text = data.decode('utf-8', errors='replace')

                    # Remove V3 prefix if present
                    json_text = response_text[2:] if response_text.startswith("V3") else response_text
                    response_json = json.loads(json_text)

                    # Validate response
                    if response_json.get("response") == cmd and response_json.get("code") == 200:
                        return response_json
                    else:
                        raise CommandError(
                            "ERROR_COMMAND_EXECUTION",
                            self.user_locale,
                            ip=self.ip,
                            detail=f"UDP V3 command {cmd} failed: {response_json}"
                        )

                finally:
                    sock.close()

            except socket.timeout:
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    "ERROR_TIMEOUT_DETAIL",
                    ip=self.ip,
                    detail=f"UDP V3 timeout after {timeout or self.DEFAULT_TIMEOUT}s (attempt {attempt + 1}/{retries + 1})"
                )

            except Exception as e:
                last_exception = MaxSmartConnectionError(
                    self.user_locale,
                    "ERROR_NETWORK_ISSUE",
                    ip=self.ip,
                    detail=f"UDP V3 error: {type(e).__name__}: {e} (attempt {attempt + 1}/{retries + 1})"
                )

            # If this wasn't the last attempt, wait before retrying
            if attempt < retries:
                delay = self.RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                await asyncio.sleep(delay)

        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise MaxSmartConnectionError(
                self.user_locale,
                "ERROR_NETWORK_ISSUE",
                ip=self.ip,
                detail=f"All UDP V3 attempts failed"
            )