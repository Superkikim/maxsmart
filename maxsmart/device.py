# device.py

import asyncio
import aiohttp
import json
from .exceptions import DiscoveryError, ConnectionError, StateError, CommandError, DeviceOperationError
from .const import CMD_SET_PORT_STATE, CMD_GET_DEVICE_DATA, CMD_SET_PORT_NAME
from .const import DEFAULT_STRIP_NAME, DEFAULT_PORT_NAMES
from .const import RESPONSE_CODE_SUCCESS, CMD_RESPONSE_TIMEOUT, CMD_RETRIES
from .const import MAX_PORT_NUMBER, MAX_PORT_NAME_LENGTH, DEFAULT_PORT_NAMES, DEFAULT_STRIP_NAME
from .const import SUPPORTED_FIRMWARE_VERSION, LIMITED_SUPPORT_FIRMWARE
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
            # Raise a ConnectionError that will log the error message automatically
            raise ConnectionError(user_locale=self.user_locale, error_key="ERROR_NETWORK_ISSUE", detail=str(e))

        self._cached_state = None  # Cache for the strip's state

    async def _send_get_command(self, cmd):
        """
        Send a command to get data from the device.

        :param cmd: Command identifier (e.g., 511).
        :return: JSON response from the device.
        """
        url = f"http://{self.ip}/?cmd={cmd}"

        async with self.session.get(url) as response:
            # Check response status
            if response.status != RESPONSE_CODE_SUCCESS:
                content = await response.text()
                raise CommandError(f"Get command failed. Response: {content}")

            # Check if the response content type is JSON
            if response.headers.get('Content-Type') == 'application/json':
                return await response.json()  # Return the JSON payload
            else:
                # If the response is not JSON, handle accordingly
                content = await response.text()
                print("Received non-JSON response:", content)
                return content  # You may choose to return this or raise an error

    async def _send_set_command(self, cmd, params=None):
        """
        Send a command to set the state of the device.

        :param cmd: Command identifier (must be 200 or 201).
        :param params: Parameters required for the command.
        """
        # Validate the command for setting states
        if cmd not in {CMD_SET_PORT_STATE, CMD_SET_PORT_NAME}:
            raise CommandError("Invalid set command. Must be either 200 or 201.", self.user_locale)

        url = f"http://{self.ip}/?cmd={cmd}&json={json.dumps(params or {})}"

        async with self.session.get(url) as response:
            if response.status != RESPONSE_CODE_SUCCESS:
                content = await response.text()
                raise CommandError(f"Set command failed. Response: {content}")

        return  # Success, no payload expected

    async def turn_on(self, port):
        """Turn on a specific port."""
        params = {"port": port, "state": 1}
        # Use the set command
        await self._send_set_command(CMD_SET_PORT_STATE, params)

    async def turn_off(self, port):
        """Turn off a specific port."""
        params = {"port": port, "state": 0}
        # Use the set command
        await self._send_set_command(CMD_SET_PORT_STATE, params)

    async def get_data(self):
        try:
            response = await self._send_command(CMD_GET_DEVICE_DATA, params=None)  # Get data from the device
            data = response.get("data", {})
            state = data.get('switch')
            wattage = data.get('watt')

            if state is None or wattage is None:
                raise StateError("ERROR_MISSING_EXPECTED_DATA", self.user_locale)

            watt_value = float(wattage)  # Convert wattage to float for processing.

            # Check firmware version to determine how to interpret wattage
            if self.device_version in [SUPPORTED_FIRMWARE_VERSION, LIMITED_SUPPORT_FIRMWARE]:
                # For supported versions, return watt value directly.
                return {"switch": state, "watt": watt_value}
            else:
                # For unsupported versions, treat the value as milliWatts (mW) and convert to watts.
                return {"switch": state, "watt": watt_value / 1000.0}  # Convert to watts

        except CommandError:
            raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale)  # Use standardized error message

    async def check_state(self, port=None):
        """Check the state of a specific port or all ports."""
        if port is not None:
            # Validate the port number
            if not 1 <= port <= 6:
                raise DeviceOperationError(self.user_locale)
            
            response = await self._send_get_command(CMD_GET_DEVICE_DATA)

            if not isinstance(response, dict) or 'data' not in response or 'switch' not in response['data']:
                raise StateError("Received invalid data structure.", self.user_locale)

            return response['data']['switch'][port - 1]  # Return state for the specified port

        else:
            response = await self._send_get_command(CMD_GET_DEVICE_DATA)

            if not isinstance(response, dict) or 'data' not in response or 'switch' not in response['data']:
                raise StateError("Received invalid data structure.", self.user_locale)

            return response['data']['switch']  # Return the list of states for all ports

    async def _verify_state(self, port, expected_state):
        """
        Verify that a specific port or all ports are in the expected state.

        :param port: Port number (0 to 6). If 0, verify state for all ports.
        :param expected_state: The state expected (1 for ON, 0 for OFF).
        """
        try:
            if port == 0:
                # Check if all ports have the same expected state
                all_states = await self.check_state()  # Fetch all port states
                for state in all_states:
                    if state != expected_state:
                        raise StateError("ERROR_UNEXPECTED_STATE", self.user_locale)  # Raise if any port is not as expected
            else:
                # Validate a specific port only
                if not 1 <= port <= 6:
                    raise DeviceOperationError(self.user_locale)  # Raise with appropriate error

                current_state = await self.check_state(port)  # Check the specific port state
                if current_state != expected_state:
                    raise StateError("ERROR_UNEXPECTED_STATE", self.user_locale)  # Raise if the specific port is not as expected

        except CommandError:
            raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale)  # Raise with standardized message
        except Exception as e:
            raise StateError("ERROR_UNEXPECTED", self.user_locale)  # Handle unexpected errors

    async def get_hourly_data(self, port):
        try:
            params = {"type": 0}
            response = await self._send_command(CMD_GET_HOURLY_DATA, params)
            data = response.get("data", {}).get("watt", [])

            # Check if the data is received and valid
            if not data or len(data) < port:
                raise StateError("ERROR_MISSING_EXPECTED_DATA", self.user_locale)  # Raise using the error key

            return data[port - 1]  # Return the watt value for the specified port

        except CommandError:
            raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale)  # Raise using the error key
        except IndexError:
            raise StateError("ERROR_UNEXPECTED", self.user_locale)  # Raise using the unexpected error key

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
            raise StateError("ERROR_MISSING_EXPECTED_DATA", self.user_locale)  # Change to the error key for missing IP

        from maxsmart import MaxSmartDiscovery

        try:
            discovery = MaxSmartDiscovery()
            devices = await discovery.discover_maxsmart(ip=self.ip)

            if not devices:
                raise DiscoveryError("ERROR_NO_DEVICES_FOUND", self.user_locale)  # Use the error key for no devices found

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

        except ConnectionError:
            raise ConnectionError("ERROR_NETWORK_ISSUE", self.user_locale)  # Raise with network error key
        except DiscoveryError:
            raise DiscoveryError("ERROR_NO_DEVICES_FOUND", self.user_locale)  # Raise with standardized message
        except Exception as e:
            raise StateError("ERROR_UNEXPECTED", self.user_locale, detail=str(e))  # Use the unexpected error key

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
            raise DeviceOperationError(self.user_locale)  # Raise with invalid parameters error

        if not new_name or new_name.strip() == "":
            raise StateError("ERROR_INVALID_PARAMETERS", self.user_locale)  # Raise using the key for invalid parameters

        if len(new_name) > MAX_PORT_NAME_LENGTH:
            raise StateError("ERROR_UNEXPECTED_STATE", self.user_locale)  # Raise for invalid name length

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
                raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale)  # Use the standardized error message

        except CommandError:
            raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale)  # Handle command execution error
        except Exception as e:
            raise StateError("ERROR_UNEXPECTED", self.user_locale, detail=str(e))  # Raise unexpected error with detail

    async def close(self):
        """Close the aiohttp ClientSession."""
        await self.session.close()
