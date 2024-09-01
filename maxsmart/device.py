# device.py

import asyncio
import aiohttp
import json
from .exceptions import DiscoveryError, ConnectionError, StateError, CommandError
from .const import CMD_SET_PORT_STATE, CMD_GET_DEVICE_DATA, CMD_SET_PORT_NAME
from .const import DEFAULT_STRIP_NAME, DEFAULT_PORT_NAMES
from .const import RESPONSE_CODE_SUCCESS, CMD_RESPONSE_TIMEOUT, CMD_RETRIES
from .const import MAX_PORT_NUMBER, MAX_PORT_NAME_LENGTH, DEFAULT_PORT_NAMES, DEFAULT_STRIP_NAME
from .utils import get_user_locale

class MaxSmartDevice:
    def __init__(self, ip):
        self.ip = ip
        self.strip_name = DEFAULT_STRIP_NAME  # Default strip name
        self.port_names = DEFAULT_PORT_NAMES  # Default port names
        self.user_locale = get_user_locale()  # Get user's locale from utils

        try:
            self.session = aiohttp.ClientSession()  # Create a single session for the class
        except Exception as e:
            raise ConnectionError(user_locale=self.user_locale, error_key="ERROR_NETWORK_ISSUE", detail=str(e))

        self._cached_state = None  # Cache for the strip's state

    async def _send_command(self, cmd, params=None):
        if params is None:  # Check if params is None
            raise ValueError("Parameters cannot be None")  # Raise an error if so

        url = f"http://{self.ip}/?cmd={cmd}"
        cmd_json = json.dumps(params) if params else None

        retries = CMD_RETRIES
        delay = CMD_RESPONSE_TIMEOUT  # seconds

        for attempt in range(retries):
            try:
                async with self.session.get(url, params={'json': cmd_json}) as response:
                    # Log response status for troubleshooting
                    if response.status != RESPONSE_CODE_SUCCESS:
                        content = await response.text()
                        print(f"Received non-{RESPONSE_CODE_SUCCESS} response: {response.status}, content: {content}")

                    # Raise an error for non-success responses
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientConnectionError as e:
                if attempt == retries - 1:  # Last attempt
                    raise ConnectionError(f"Failed to connect to power strip at {self.ip}: {str(e)}")
            except asyncio.TimeoutError as e:
                if attempt == retries - 1:  # Last attempt
                    raise ConnectionError(f"Connection to power strip at {self.ip} timed out: {str(e)}")
            except aiohttp.ClientError as e:
                raise CommandError(f"HTTP error occurred while sending command to power strip: {str(e)}")
            except Exception as e:
                if attempt == retries - 1:  # Last attempt
                    raise CommandError(f"Error sending command to power strip: {str(e)}")

            await asyncio.sleep(delay)

        raise CommandError("Failed to send command to power strip after multiple retries.")
                       
    async def turn_on(self, port):
        try:
            params = {"port": port, "state": 1}
            await self._send_command(CMD_SET_PORT_STATE, params)
            await asyncio.sleep(1)  # Wait for command to take effect

            if port == 0:
                await self._verify_ports_state([1] * 6)
            else:
                await self._verify_port_state(port, 1)
        except CommandError as e:
            raise CommandError(f"Failed to turn on port {port}: {str(e)}")
        except StateError as e:
            raise StateError(f"Port {port} did not turn on as expected: {str(e)}")

    async def turn_off(self, port):
        try:
            params = {"port": port, "state": 0}
            await self._send_command(CMD_SET_PORT_STATE, params)
            await asyncio.sleep(1)  # Wait for command to take effect

            if port == 0:
                await self._verify_ports_state([0] * 6)
            else:
                await self._verify_port_state(port, 0)
        except CommandError as e:
            raise CommandError(f"Failed to turn off port {port}: {str(e)}")
        except StateError as e:
            raise StateError(f"Port {port} did not turn off as expected: {str(e)}")

    async def get_data(self):
        try:
            response = await self._send_command(CMD_GET_DEVICE_DATA, params=None)  # Assuming 511 is the command to get data
            state = response.get('data', {}).get('switch')
            wattage = response.get('data', {}).get('watt')
            
            if state is None or wattage is None:
                raise StateError("'switch' or 'watt' data not found in response from power strip")
            
            return {"switch": state, "watt": wattage}
        except CommandError as e:
            raise CommandError(f"Failed to get data from power strip: {str(e)}")

    async def check_ports_state(self):
        if self._cached_state is not None:
            return self._cached_state  # Return cached state if available

        try:
            # Send command to get the state of the device
            response = await self._send_command(CMD_GET_DEVICE_DATA)  # Assuming 511 is the command to check state

            # Retrieve the complete state data, which may consist of multiple values
            data = response.get('data', {})
            
            # Check if there's expected data
            if 'switch' not in data:
                raise StateError("'switch' data not found in response from power strip")
            
            # Assuming state should be a list of port states
            state = data['switch']  # This might reflect the power status of ports
            
            # Validate the structure of the state data
            if not isinstance(state, list) or len(state) != 6:  # Assuming we expect 6 ports
                raise StateError("Invalid state data format received: Expected a list of exactly 6 elements.")
            
            # Cache the state for future use
            self._cached_state = state
            
            return state  # Return the complete state data for all ports
        except CommandError as e:
            raise CommandError(f"Failed to check state of power strip: {str(e)}")
        except Exception as e:
            raise StateError(f"Unexpected error occurred while checking state: {str(e)}")

    async def check_port_state(self, port):
        if not 1 <= port <= 6:  # valid port numbers are 1 to 6
            raise StateError(f"Invalid port number: {port}. Port number must be between 1 and 6")
        try:
            state = await self.check_ports_state()
            if isinstance(state, list) and 1 <= port <= len(state):  # Check if state is a list and valid index
                return state[port - 1]  # subtract 1 because lists are 0-indexed
            else:
                raise StateError(f"Invalid state data received")
        except CommandError as e:
            raise CommandError(f"Failed to check state of port {port}: {str(e)}")
        except StateError as e:
            raise StateError(f"Failed to retrieve state for port {port}: {str(e)}")
        except IndexError:
            raise StateError(f"Invalid state data received: not enough elements for port {port}")

    async def _verify_ports_state(self, expected_state):
        try:
            for port in range(1, 7):
                if await self.check_port_state(port) != expected_state[port - 1]:
                    raise StateError(f"Port {port} is not in the expected state")
        except CommandError as e:
            raise CommandError(f"Failed to verify ports state: {str(e)}")
        except StateError as e:
            raise StateError(f"Failed to verify all ports state: {str(e)}")

    async def _verify_port_state(self, port, expected_state):
        try:
            if await self.check_port_state(port) != expected_state:
                raise StateError(f"Port {port} is not in the expected state")
        except CommandError as e:
            raise CommandError(f"Failed to verify state of port {port}: {str(e)}")
        except StateError as e:
            raise StateError(f"Failed to verify state of port {port}: {str(e)}")

    async def get_hourly_data(self, port):
        try:
            params = {"type": 0}
            response = await self._send_command(CMD_GET_HOURLY_DATA, params)
            data = response.get("data", {}).get("watt", [])
            if not data or len(data) < port:
                raise StateError("No watt data received from the device")
            return data[port - 1]
        except CommandError as e:
            raise CommandError(f"Failed to get hourly data for port {port}: {str(e)}")
        except IndexError:
            raise StateError(f"Invalid port number: {port}")

    async def get_power_data(self, port):
        try:
            response = await self._send_command(CMD_GET_DEVICE_DATA, params=None)
            data = response.get("data", {})
            watt = data.get("watt", [])
            if not watt or port < 1 or port > len(watt):
                raise StateError(f"No watt data received or invalid port number: {port}")
            return {"watt": watt[port - 1]}
        except CommandError as e:
            raise CommandError(f"Failed to get power data for port {port}: {str(e)}")

    async def retrieve_port_names(self):
        """Retrieve current port names by sending a discovery request."""
        if not self.ip:
            raise StateError("IP address must be set before retrieving port names.")

        from maxsmart import MaxSmartDiscovery

        try:
            discovery = MaxSmartDiscovery()
            devices = await discovery.discover_maxsmart(ip=self.ip)

            if not devices:
                raise DiscoveryError(f"No devices found with IP: {self.ip}")

            device = devices[0]  # Access the first (and only) device
            self.strip_name = device.get('name', self.strip_name)  # Name for port 0
            self.port_names = device.get('pname', self.port_names)  # Names for ports 1 to 6

            # Combine in a dictionary
            port_mapping = {
                "Port 0": self.strip_name,
            }
            for i in range(1, 7):
                port_mapping[f"Port {i}"] = self.port_names[i - 1] if i - 1 < len(self.port_names) else f"Port {i}"

            return port_mapping  # Return the dictionary

        except ConnectionError as e:
            raise ConnectionError(f"Failed to connect to device at {self.ip}: {str(e)}")
        except DiscoveryError as e:
            raise DiscoveryError(f"Error during device discovery: {str(e)}")
        except Exception as e:
            raise StateError(f"Unexpected error retrieving port names: {str(e)}")

    async def change_port_name(self, port, new_name):
        """
        Change the name of a specific port asynchronously.

        Args:
            port (int): The port number (0-6) to change the name for.
            new_name (str): The new name for the port (max 21 characters).

        Raises:
            StateError: If the port number is invalid, the new name is empty, or the new name is too long.
            CommandError: If there's an error sending the command to the device.
        """
        if not 0 <= port <= MAX_PORT_NUMBER:
            raise StateError(f"Invalid port number: {port}. Must be between 0 and {MAX_PORT_NUMBER}.")

        if not new_name or new_name.strip() == "":
            raise StateError("Port name cannot be empty.")

        if len(new_name) > MAX_PORT_NAME_LENGTH:
            raise StateError(f"Port name '{new_name}' is too long. Maximum length is {MAX_PORT_NAME_LENGTH} characters.")

        try:
            params = {
                "port": port,
                "name": new_name
            }
            response = await self._send_command(CMD_SET_PORT_NAME, params)

            # Check if the command was successful
            if response.get('code') == RESPONSE_CODE_SUCCESS:
                # Update the local port name storage
                if port == 0:
                    self.strip_name = new_name
                else:
                    self.port_names[port - 1] = new_name
                return True
            else:
                raise CommandError(f"Failed to change port name. Device returned unexpected code: {response.get('code')}")

        except CommandError as e:
            raise CommandError(f"Error changing port name: {str(e)}")
        except Exception as e:
            raise StateError(f"Unexpected error occurred while changing port name: {str(e)}")

    async def close(self):
        """Close the aiohttp ClientSession."""
        await self.session.close()
