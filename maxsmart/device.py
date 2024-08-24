# device.py

import requests
import json
import time
from .exceptions import DiscoveryError, ConnectionError, StateError, CommandError

class MaxSmartDevice:
    def __init__(self, ip):
        self.ip = ip
        self.strip_name = "Strip"  # Default strip name
        self.port_names = [f"Port {i}" for i in range(1, 7)]  # Default port names

    def _send_command(self, cmd, params=None):
        url = f"http://{self.ip}/?cmd={cmd}"
        if params:
            cmd_json = json.dumps(params)
        else:
            cmd_json = None

        retries = 3
        delay = 1  # seconds

        for attempt in range(retries):
            try:
                response = requests.get(url, params={'json': cmd_json})
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as e:
                if attempt == retries - 1:  # Last attempt
                    raise ConnectionError(f"Failed to connect to power strip at {self.ip}: {str(e)}")
            except requests.exceptions.Timeout as e:
                if attempt == retries - 1:  # Last attempt
                    raise ConnectionError(f"Connection to power strip at {self.ip} timed out: {str(e)}")
            except requests.exceptions.HTTPError as e:
                raise CommandError(f"HTTP error occurred while sending command to power strip: {str(e)}")
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:  # Last attempt
                    raise CommandError(f"Error sending command to power strip: {str(e)}")
            except json.JSONDecodeError as e:
                raise CommandError(f"Failed to parse JSON response from power strip: {str(e)}")
            
            time.sleep(delay)

        raise CommandError("Failed to send command to power strip after multiple retries")

    def turn_on(self, port):
        try:
            params = {"port": port, "state": 1}
            self._send_command(200, params)
            time.sleep(1)  # Wait for command to take effect

            if port == 0:
                self._verify_ports_state([1] * 6)
            else:
                self._verify_port_state(port, 1)
        except CommandError as e:
            raise CommandError(f"Failed to turn on port {port}: {str(e)}")
        except StateError as e:
            raise StateError(f"Port {port} did not turn on as expected: {str(e)}")

    def turn_off(self, port):
        try:
            params = {"port": port, "state": 0}
            self._send_command(200, params)
            time.sleep(1)  # Wait for command to take effect

            if port == 0:
                self._verify_ports_state([0] * 6)
            else:
                self._verify_port_state(port, 0)
        except CommandError as e:
            raise CommandError(f"Failed to turn off port {port}: {str(e)}")
        except StateError as e:
            raise StateError(f"Port {port} did not turn off as expected: {str(e)}")

    def get_data(self):
        try:
            response = self._send_command(511)
            state = response.get('data', {}).get('switch')
            wattage = response.get('data', {}).get('watt')
            
            if state is None or wattage is None:
                raise StateError("'switch' or 'watt' data not found in response from power strip")
            
            return {"switch": state, "watt": wattage}
        except CommandError as e:
            raise CommandError(f"Failed to get data from power strip: {str(e)}")

    def check_state(self):
        try:
            response = self._send_command(511)
            state = response.get('data', {}).get('switch')
            if state is None:
                raise StateError("'switch' data not found in response from power strip")
            return state
        except CommandError as e:
            raise CommandError(f"Failed to check state of power strip: {str(e)}")


    def check_port_state(self, port):
        if not 1 <= port <= 6:  # valid port numbers are 1 to 6
            raise StateError(f"Invalid port number: {port}. Port number must be between 1 and 6")
        try:
            state = self.check_state()
            return state[port - 1]  # subtract 1 because lists are 0-indexed
        except CommandError as e:
            raise CommandError(f"Failed to check state of port {port}: {str(e)}")
        except StateError as e:
            raise StateError(f"Failed to retrieve state for port {port}: {str(e)}")
        except IndexError:
            raise StateError(f"Invalid state data received: not enough elements for port {port}")

    def _verify_ports_state(self, expected_state):
        try:
            for port in range(1, 7):
                if self.check_port_state(port) != expected_state[port - 1]:
                    raise StateError(f"Port {port} is not in the expected state")
        except CommandError as e:
            raise CommandError(f"Failed to verify ports state: {str(e)}")
        except StateError as e:
            raise StateError(f"Failed to verify all ports state: {str(e)}")

    def _verify_port_state(self, port, expected_state):
        try:
            if self.check_port_state(port) != expected_state:
                raise StateError(f"Port {port} is not in the expected state")
        except CommandError as e:
            raise CommandError(f"Failed to verify state of port {port}: {str(e)}")
        except StateError as e:
            raise StateError(f"Failed to verify state of port {port}: {str(e)}")

    def get_hourly_data(self, port):
        try:
            params = {"type": 0}
            response = self._send_command(510, params)
            data = response.get("data", {}).get("watt", [])
            if not data:
                raise StateError("No watt data received from the device")
            if len(data) < port:
                raise StateError(f"Not enough data for port {port}")
            return data[port - 1]
        except CommandError as e:
            raise CommandError(f"Failed to get hourly data for port {port}: {str(e)}")
        except IndexError:
            raise StateError(f"Invalid port number: {port}")

    def get_power_data(self, port):
        try:
            response = self._send_command(511)
            data = response.get("data", {})
            watt = data.get("watt", [])
            if not watt:
                raise StateError("No watt data received from the device")
            if port < 1 or port > len(watt):
                raise StateError(f"Invalid port number: {port}")
            return {"watt": watt[port - 1]}
        except CommandError as e:
            raise CommandError(f"Failed to get power data for port {port}: {str(e)}")
            
    def retrieve_port_names(self):
        """Retrieve current port names by sending a discovery request."""
        if not self.ip:
            raise StateError("IP address must be set before retrieving port names.")

        from maxsmart import MaxSmartDiscovery

        try:
            discovery = MaxSmartDiscovery()
            devices = discovery.discover_maxsmart(ip=self.ip)

            # If no devices were found, raise an exception
            if not devices:
                raise DiscoveryError(f"No devices found with IP: {self.ip}")

            # Assuming there is only one device returned for the given IP
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

    def change_port_name(self, port, new_name):
        """
        Change the name of a specific port.

        Args:
        port (int): The port number (0-6) to change the name for.
        new_name (str): The new name for the port (max 21 characters).

        Raises:
        StateError: If the port number is invalid, the new name is empty, or the new name is too long.
        CommandError: If there's an error sending the command to the device.
        """
        if not 0 <= port <= 6:
            raise StateError(f"Invalid port number: {port}. Must be between 0 and 6.")
        
        if not new_name or new_name.strip() == "":
            raise StateError("Port name cannot be empty.")

        if len(new_name) > 21:
            raise StateError(f"Port name '{new_name}' is too long. Maximum length is 21 characters.")

        try:
            params = {
                "port": port,
                "name": new_name
            }
            response = self._send_command(201, params)
            
            # Check if the command was successful
            if response.get('code') == 200:
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
