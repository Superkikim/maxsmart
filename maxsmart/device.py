# device.py

import asyncio
import aiohttp
import json
from .exceptions import DiscoveryError, ConnectionError, StateError, CommandError, DeviceOperationError
from .const import CMD_SET_PORT_STATE, CMD_GET_DEVICE_DATA, CMD_SET_PORT_NAME, CMD_GET_STATISTICS
from .const import DEFAULT_STRIP_NAME, DEFAULT_PORT_NAMES
from .const import RESPONSE_CODE_SUCCESS, CMD_RESPONSE_TIMEOUT, CMD_RETRIES
from .const import MAX_PORT_NUMBER, MAX_PORT_NAME_LENGTH, DEFAULT_PORT_NAMES, DEFAULT_STRIP_NAME
from .const import SUPPORTED_FIRMWARE_VERSION, LIMITED_SUPPORT_FIRMWARE
from .const import DEVICE_ERROR_MESSAGES
from .const import CURRENCY_SYMBOLS, STATISTICS_TIME_FRAME
from .discovery import MaxSmartDiscovery
from .utils import get_user_locale, get_user_message

class MaxSmartDevice:
    def __init__(self, ip_address):
        self.ip = ip_address
        self.user_locale = get_user_locale()  # Get user's locale from utils
        
        # Initialize default values
        self.strip_name = DEFAULT_STRIP_NAME
        self.port_names = DEFAULT_PORT_NAMES
        
        # Store device information
        self.sn = None
        self.name = None
        self.version = None

        # Create an HTTP session
        self.session = aiohttp.ClientSession()  # Create a single session for the class

    async def initialize_device(self):
        """Perform device discovery and initialize properties based on the results."""
        discovery = MaxSmartDiscovery()
        devices = await discovery.discover_maxsmart(ip=self.ip, user_locale=self.user_locale)

        if devices:
            primary_device = devices[0]
            self.sn = primary_device.get('sn')
            self.name = primary_device.get('name')
            self.version = primary_device.get('ver')
            
            if 'pname' in primary_device:
                self.port_names = primary_device['pname']
            
            if self.version != "1.30":
                self.strip_name = DEFAULT_STRIP_NAME
                self.port_names = DEFAULT_PORT_NAMES
        else:
            raise Exception("No devices found during discovery.")
    def __repr__(self):
        return (f"MaxSmartDevice(ip={self.ip}, sn={self.sn}, name={self.name}, "
                f"version={self.version}, strip_name={self.strip_name})")

       
    async def _send_get_command(self, cmd, params=None):
        """
        Send a command to get data from the device.

        :param cmd: Command identifier (e.g., 511).
        :param params: Additional parameters for the command.
        :return: Response from the device as plain text or JSON if applicable.
        """
        # Validate the command
        if cmd not in {CMD_GET_DEVICE_DATA, CMD_GET_STATISTICS}:
            raise CommandError("ERROR_INVALID_PARAMETERS", self.user_locale,
                            detail="Invalid get command. Must be either {} or {}.".format(CMD_GET_STATISTICS, CMD_GET_DEVICE_DATA))

        # Construct the URL with parameters, if any
        url = f"http://{self.ip}/?cmd={cmd}&json={json.dumps(params or {})}"

        async with self.session.get(url) as response:
            # Check for success
            if response.status != RESPONSE_CODE_SUCCESS:
                content = await response.text()
                raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale,
                                detail=f"Get command failed. Response: {content}")

            content = await response.text()
            try:
                return json.loads(content)  # Try parsing the content as JSON
            except json.JSONDecodeError:
                raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale,
                                detail=f"Received invalid JSON: {content}")

    async def _send_set_command(self, cmd, params=None):
        """
        Send a command to set the state of the device.

        :param cmd: Command identifier (must be 200 or 201).
        :param params: Parameters required for the command.
        """
        # Validate the command for setting states
        if cmd not in {CMD_SET_PORT_STATE, CMD_SET_PORT_NAME}:
            error_key = "ERROR_INVALID_PARAMETERS"
            detail_message = get_user_message(DEVICE_ERROR_MESSAGES, error_key, self.user_locale).format(CMD_SET_PORT_STATE, CMD_SET_PORT_NAME)
            raise CommandError(error_key, self.user_locale, detail=detail_message)

        url = f"http://{self.ip}/?cmd={cmd}&json={json.dumps(params or {})}"

        async with self.session.get(url) as response:
            if response.status != RESPONSE_CODE_SUCCESS:
                content = await response.text()
                error_key = "ERROR_COMMAND_EXECUTION"
                detail_message = get_user_message(DEVICE_ERROR_MESSAGES, error_key, self.user_locale).format(content=content)
                raise CommandError(error_key, self.user_locale, detail=detail_message)

        return  # Success, no payload expected

    async def turn_on(self, port):
        """Turn on a specific port."""
        params = {"port": port, "state": 1}
        # Use the set command
        await self._send_set_command(CMD_SET_PORT_STATE, params)

        # Verify the state after turning on
        attempts = 0
        while attempts < 3:
            try:
                await self._verify_state(port, 1)  # Check if the port is ON
                return  # Exit after successful operation
            except StateError:
                attempts += 1

        # Raise an error indicating the state is unexpected after 3 attempts
        raise StateError("ERROR_UNEXPECTED_STATE", self.user_locale)  # Localized error for unexpected state

    async def turn_off(self, port):
        """Turn off a specific port."""
        params = {"port": port, "state": 0}
        # Use the set command
        await self._send_set_command(CMD_SET_PORT_STATE, params)

        # Verify the state after turning off
        attempts = 0
        while attempts < 3:
            try:
                await self._verify_state(port, 0)  # Check if the port is OFF
                return  # Exit after successful operation
            except StateError:
                attempts += 1

        # Raise an error indicating the state is unexpected after 3 attempts
        raise StateError("ERROR_UNEXPECTED_STATE", self.user_locale)  # Localized error for unexpected state

    async def get_data(self):
        """
        Retrieve device data, including wattage and switch states.
        :return: Dictionary containing switch state and wattage data.
        """
        try:
            response = await self._send_get_command(CMD_GET_DEVICE_DATA)

            # Validate the response structure
            if not isinstance(response, dict) or 'data' not in response or 'switch' not in response['data']:
                raise CommandError("ERROR_INVALID_JSON", self.user_locale, detail="Received invalid data structure from device.")

            # Extract necessary information
            data = response['data']
            switch_states = data.get('switch')
            wattages = data.get('watt')

            if switch_states is None or wattages is None:
                raise CommandError("ERROR_MISSING_EXPECTED_DATA", self.user_locale)

            # Convert wattage values to float
            watt_value = [float(watt) for watt in wattages]

            # Return the structured data
            return {
                "switch": switch_states,
                "watt": watt_value
            }

        except CommandError:
            raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale)  # Use standardized error message
        except Exception as e:
            raise CommandError("ERROR_UNEXPECTED", self.user_locale, detail=str(e))  # Handle unexpected errors

    async def check_state(self, port=None):
        """Check the state of a specific port or all ports."""
        try:
            data = await self.get_data()  # Use the get_data method to retrieve device information

            # Validate the response structure
            if 'switch' not in data:
                raise StateError(self.user_locale)

            # If a specific port number is provided, return its state
            if port is not None:
                # Validate the port number
                if not 1 <= port <= 6:
                    raise DeviceOperationError(self.user_locale)

                return data['switch'][port - 1]  # Return state for the specified port

            # Return the list of states for all ports
            return data['switch']

        except CommandError as e:
            raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale, detail=str(e))
        except Exception as e:
            raise StateError(self.user_locale)  # Simplified error handling

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
                        raise StateError(self.user_locale)  # Raise if any port is not as expected
            else:
                # Validate a specific port only
                if not 1 <= port <= 6:
                    raise DeviceOperationError(self.user_locale)

                current_state = await self.check_state(port)  # Get the specific port state
                if current_state != expected_state:
                    raise StateError(self.user_locale)  # Raise if the specific port is not as expected

        except CommandError as e:
            raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale, detail=str(e))
        except Exception as e:
            raise StateError(self.user_locale)  # Handle unexpected errors

    async def get_statistics(self, port, stat_type):
        """
        Retrieve statistics for a specific port or all ports.

        :param port: The port number (0 for all ports).
        :param stat_type: The type of statistics (0 = hourly, 1 = daily, 2 = monthly).
        :return: A dictionary containing statistics data.
        """
        if not (0 <= port <= MAX_PORT_NUMBER):
            raise DeviceOperationError(self.user_locale)  # Raise with invalid parameters error

        if stat_type not in STATISTICS_TIME_FRAME.keys():
            raise CommandError("ERROR_INVALID_PARAMETERS", self.user_locale)  # Raise with invalid parameters error

        try:
            response = await self._send_get_command(CMD_GET_STATISTICS, params={"type": stat_type})

            # Validate the response structure
            if not isinstance(response, dict) or 'data' not in response:
                raise CommandError("ERROR_INVALID_JSON", self.user_locale, detail="Received invalid data structure from device.")

            data = response['data']
            cost = float(data.get('cost', 0))
            currency = CURRENCY_SYMBOLS.get(data['money'], "$")  # Use default $ if not found
            watt_data = data['watt']

            # Extract date
            date_str = data['date']
            year, month = map(int, date_str.split('-')[:2])
            day = hour = 0  # Initialize default values for day and hour

            # If type is 0 (hourly): use last two digits as hour, if type is 1 (daily): day is irrelevant
            if stat_type == 0:  # hourly
                hour = int(date_str.split('-')[-1])
            elif stat_type == 1:  # daily
                day = int(date_str.split('-')[-1])

            # If port is 0, sum the watt data across all ports
            if port == 0:
                # Convert watt_data values from strings to floats before summation
                summed_watt = [sum(float(value) for value in port_data) for port_data in zip(*watt_data)]
            else:  # For specific port
                if not watt_data or (port - 1) >= len(watt_data):
                    raise StateError("ERROR_MISSING_EXPECTED_DATA", self.user_locale) 
                # Convert watt values from strings to floats for the specific port
                summed_watt = [float(value) for value in watt_data[port - 1]]
            # Construct result
            result = {
                "cost": cost,
                "currency": currency,
                "type": STATISTICS_TIME_FRAME[stat_type],
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "watt": summed_watt  # List of wattage for the given port or all ports summed
            }

            return result

        except CommandError as e:
            raise CommandError("ERROR_COMMAND_EXECUTION", self.user_locale, detail=str(e))  # Handle command execution error
        except Exception as e:
            raise StateError("ERROR_UNEXPECTED", self.user_locale, detail=str(e))  # Handle unexpected errors

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
            FirmwareError: If the device firmware is not supported for this operation.
        """
        # Check firmware version
        if self.ver != SUPPORTED_FIRMWARE_VERSION:
            raise FirmwareError(self.device_ip, self.ver, self.user_locale)  # Raise firmware error

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
