# device.py

import requests
import json
import time
import logging

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

        for _ in range(retries):
            try:
                response = requests.get(url, params={'json': cmd_json})
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error sending command to power strip: {str(e)}")
            time.sleep(delay)

        raise Exception("Failed to send command to power strip after multiple retries")

    def turn_on(self, port):
        if port == 0:
            params = {"port": 0, "state": 1}
        else:
            params = {"port": port, "state": 1}

        self._send_command(200, params)
        time.sleep(1)  # Wait for command to take effect

        if port == 0:
            self._verify_ports_state([1] * 6)
        else:
            self._verify_port_state(port, 1)

    def turn_off(self, port):
        if port == 0:
            params = {"port": 0, "state": 0}
        else:
            params = {"port": port, "state": 0}

        self._send_command(200, params)
        time.sleep(1)  # Wait for command to take effect

        if port == 0:
            self._verify_ports_state([0] * 6)
        else:
            self._verify_port_state(port, 0)

    def get_data(self):
        response = self._send_command(511)
        state = response.get('data', {}).get('switch', [])
        wattage = response.get('data', {}).get('watt', [])
        
        if state is None or wattage is None:
            raise Exception(f"Error: 'switch' or 'watt' data not found in response from power strip")
        
        return {"switch": state, "watt": wattage}


    def check_state(self):
        response = self._send_command(511)
        state = response.get('data', {}).get('switch', [])
        if state is None:
            raise Exception(f"Error: 'switch' data not found in response from power strip")
        return state

    def check_port_state(self, port):
        state = self.check_state()
        if not 1 <= port <= 6:  # valid port numbers are 1 to 6
            raise ValueError('Port number must be between 1 and 6')
        return state[port - 1]  # subtract 1 because lists are 0-indexed

    def _verify_ports_state(self, expected_state):
        for port in range(1, 7):
            if self.check_port_state(port) != expected_state[port - 1]:
                raise Exception(f"Failed to set all ports to the expected state")

    def _verify_port_state(self, port, expected_state):
        if self.check_port_state(port) != expected_state:
            raise Exception(f"Failed to set port {port} to the expected state")

    def get_hourly_data(self, port):
        params = {"type": 0}
        response = self._send_command(510, params)
        data = response.get("data", {}).get("watt", [])
        if data and len(data) >= port:
            return data[port - 1]
        return None

    def get_power_data(self, port):
        response = self._send_command(511)
        data = response.get("data", {})
        watt = data.get("watt", [])
        if port >= 1 and port <= len(watt):
            return {"watt": watt[port - 1]}
        else:
            return None
        
    def retrieve_port_names(self):
        """Retrieve current port names by sending a discovery request."""
        if not self.ip:
            raise ValueError("IP address must be set before retrieving port names.")

        from maxsmart import MaxSmartDiscovery

        discovery = MaxSmartDiscovery()
        devices = discovery.discover_maxsmart(ip=self.ip)

        # If no devices were found, raise an exception
        if not devices:
            raise Exception(f"No devices found with IP: {self.ip}")

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
