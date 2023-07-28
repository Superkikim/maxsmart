import requests
import json
import time
import socket
import datetime

class MaxSmartDiscovery:
    @staticmethod
    def discover_maxsmart(ip=None):
        maxsmart_devices = []

        message = f"00dv=all,{datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S')};"

        if ip is None:
            target_ip = '255.255.255.255'
        else:
            target_ip = ip

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(message.encode(), (target_ip, 8888))
            sock.settimeout(5)

            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    raw_result = data.decode()

                    json_data = json.loads(raw_result)
                    ip_address = addr[0]
                    device_data = json_data.get("data")

                    if device_data:
                        sn = device_data.get("sn")
                        name = device_data.get("name")
                        pname = device_data.get("pname")
                        ver = device_data.get("ver")

                        maxsmart_device = {
                            "sn": sn,
                            "name": name,
                            "pname": pname,
                            "ip": ip_address,
                            "ver": ver
                        }

                        maxsmart_devices.append(maxsmart_device)

                except socket.timeout:
                    break

#        MaxSmartDiscovery._validate_firmware_versions(maxsmart_devices)

        return maxsmart_devices

    @staticmethod
    def _validate_firmware_versions(devices):
        for device in devices:
            firmware_version = device.get('ver')
            if firmware_version != '1.30':
                raise ValueError(f"Device with IP {device['ip']} has firmware version {firmware_version}. This module has been tested with MaxSmart devices with firmware version 1.30.")

class MaxSmartDevice:
    def __init__(self, ip):
        self.ip = ip

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
