import argparse
import time
from tabulate import tabulate
from maxsmart.maxsmart import MaxSmart

def display_table(header, data):
    print(tabulate(data, headers=header, tablefmt="grid"))

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", required=True, help="IP address of the powerstrip")
    parser.add_argument("--sn", required=True, help="SN (serial number) of the powerstrip")
    args = parser.parse_args()

    test_powerstrip(args.ip, args.sn)
