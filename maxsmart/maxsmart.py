import requests
import json
import time
import socket
import datetime


class MaxSmart:
    def __init__(self, ip, sn):
        self.ip = ip
        self.sn = sn

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
            params = {"sn": self.sn, "port": 0, "state": 1}
        else:
            params = {"sn": self.sn, "port": port, "state": 1}
        
        self._send_command(200, params)
        time.sleep(1)  # Wait for command to take effect
        
        if port == 0:
            self._verify_ports_state([1] * 6)
        else:
            self._verify_port_state(port, 1)

    def turn_off(self, port):
        if port == 0:
            params = {"sn": self.sn, "port": 0, "state": 0}
        else:
            params = {"sn": self.sn, "port": port, "state": 0}
        
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
        params = {"sn": self.sn, "type": 0}
        response = self._send_command(510, params)
        data = response.get("data", {}).get("watt", [])
        if data and len(data) >= port:
            return data[port - 1]
        return None
    
    def get_power_data(self, port):
        response = self._send_command(511, {"sn": self.sn})
        data = response.get("data", {})
        watt = data.get("watt", [])
        amp = data.get("amp", [])
        if port >= 1 and port <= len(watt):
            return {"watt": watt[port - 1], "amp": amp[port - 1]}
        else:
            return None

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

                    preprocessed_result = MaxSmart._preprocess_json_string(raw_result)
                    json_data = json.loads(preprocessed_result)
                    ip_address = addr[0]
                    device_data = json_data.get("data")

                    if device_data:
                        sn = device_data.get("sn")
                        name = device_data.get("name")
                        pname = device_data.get("pname")

                        maxsmart_device = {
                            "sn": sn,
                            "name": name,
                            "pname": pname,
                            "ip": ip_address
                        }

                        maxsmart_devices.append(maxsmart_device)

                except socket.timeout:
                    break

        return maxsmart_devices

    @staticmethod
    def _preprocess_json_string(json_str):
        json_str = json_str.strip()
        json_str = json_str.replace("'", '"')
        json_str = json_str.replace("False", '"False"')
        json_str = json_str.replace("True", '"True"')
        return json_str


def display_table(header, data):
    print(f"{' | '.join(header)}")
    print("-" * (len(header) * 10))
    for row in data:
        print(f"{' | '.join(str(item) for item in row)}")


def select_device(devices):
    print("Available MaxSmart devices:")
    device_menu = {}
    for i, device in enumerate(devices, start=1):
        sn = device["sn"]
        name = device["name"]
        ip = device["ip"]
        device_menu[i] = device
        print(f"{i}. SN: {sn}, Name: {name}, IP: {ip}")

    while True:
        choice = input("Select a device (number): ")
        try:
            choice = int(choice)
            if choice in device_menu:
                selected_device = device_menu[choice]
                return selected_device
            else:
                print("Invalid choice. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def test_powerstrip(ip, sn):
    print("WARNING: This test will power down all devices plugged into the power strip.")
    print(f"IP: {ip}, SN: {sn}")
    proceed = input("Do you want to proceed? (Y/N): ")
    if proceed.lower() != "y":
        print("Test aborted.")
        return

    maxsmart = MaxSmart(ip, sn)

    print("Powering ON port 3...")
    maxsmart.turn_on(3)
    print("Waiting 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Countdown: {i} seconds")
        time.sleep(1)
    print("Powering OFF port 3...")
    maxsmart.turn_off(3)
    print("Waiting 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Countdown: {i} seconds")
        time.sleep(1)
    print("Powering OFF all ports...")
    maxsmart.turn_off(0)
    print("Waiting 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Countdown: {i} seconds")
        time.sleep(1)
    print("Powering ON all ports...")
    maxsmart.turn_on(0)
    print("Waiting 15 seconds...")
    for i in range(15, 0, -1):
        print(f"Countdown: {i} seconds")
        time.sleep(1)
    print("Powering OFF ports 3 to 6...")
    for port in range(3, 7):
        maxsmart.turn_off(port)
    print("Retrieving real-time consumption data...")
    consumption_data = []
    for port in range(1, 7):
        power_data = maxsmart.get_power_data(port)
        consumption_data.append([f"Port {port}", power_data["watt"], power_data["amp"]])
    display_table(["Port", "Watt", "Amp"], consumption_data)
    print("Retrieving 24-hour consumption data...")
    hourly_data = []
    for port in range(1, 7):
        hourly_data.append([f"Port {port}", maxsmart.get_hourly_data(port)])
    display_table(["Port", "Hourly Data"], hourly_data)


if __name__ == "__main__":
    devices = MaxSmart.discover_maxsmart()
    if devices:
        selected_device = select_device(devices)
        ip = selected_device["ip"]
        sn = selected_device["sn"]
        test_powerstrip(ip, sn)
    else:
        print("No MaxSmart devices found.")
