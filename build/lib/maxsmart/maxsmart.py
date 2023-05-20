import requests
import json

class MaxSmart:
    def __init__(self, ip, sn):
        self.ip = ip
        self.sn = sn

    def _send_command(self, cmd, port=None, state=None):
        if port is None:
            cmd_json = json.dumps({"sn": self.sn})
        else:
            cmd_json = json.dumps({"sn": self.sn, "port": port, "state": state})

        try:
            response = requests.get(f'http://{self.ip}/', params={'cmd': cmd, 'json': cmd_json})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error sending command to power strip: {str(e)}")

        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing response from power strip: {str(e)}")

    def turn_on(self, port):
        return self._send_command(200, port, 1)

    def turn_off(self, port):
        return self._send_command(200, port, 0)

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

    def get_hourly_data(self, port):
        url = f"http://{self.ip}/?cmd=510&json=%7B%22sn%22:%22{self.sn}%22,%22type%22:0%7D"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            watt_data = data.get("data", {}).get("watt", [])
            if watt_data and len(watt_data) >= port:
                port_data = watt_data[port - 1]
                return port_data
        return None