# MaxSmart Python Module

The `maxsmart` module is designed to operate Revogi-based Max Hauri MaxSmart PowerStrips running on v1.x firmware. It enables local communication with the power strips without requiring any cloud connection or account.

**Note:** If you have upgraded your MaxSmart app to version 2, it may have pushed a new firmware to your devices, rendering this module incompatible.

## Introduction

The `maxsmart` module is developed to control Max Hauri MaxSmart devices, specifically, the MaxSmart Power Station and the MaxSmart Power Plug. These are smart home devices that provide remote control and automation capabilities. Please note that these products are no longer available on the Swiss market under the Max Hauri brand and are considered end-of-life.

## MaxSmart Overview

The MaxSmart Power Station and Power Plug are part of the MaxSmart product line, designed for smart home applications. These devices are based on the Revogi Smart Power Strip.

It's important to note that MaxSmart devices were designed to be controlled remotely over the internet using a Max Hauri cloud account. However, with the products reaching their end-of-life and the discontinuation of support for version 1.x of the cloud, there have been issues reported by users, including potential interruptions and disappearing cloud accounts. Upgrading to firmware version 2.x changes the API and removes the possibility of local control.

While the `maxsmart` module has been specifically developed for Revogi-based Max Hauri MaxSmart PowerStrips, there have been some reports of potential compatibility with other brands and models. These include:

- Max Hauri MaxSmart (v1.x)
- Revogi Smart Power Strip
- Extel Soky
- MCL DOM-PPS06I

However, compatibility with these brands and models may vary, and it's recommended to perform thorough testing to ensure proper functionality.

Please keep in mind that the `maxsmart` module is primarily designed for Revogi-based Max Hauri MaxSmart PowerStrips running on v1.x firmware, and compatibility with other devices or firmware versions is not guaranteed.

The [test script](#test-script) may allow you to test this easily. 

**Disclaimer**: I'm not responsible for any damage or loss of configuration of your device. Make this at your own risk.

## MaxSmart Control

MaxSmart devices can be controlled via the MaxSmart app, available on both Android and iOS, or through the MaxSmart website. However, due to potential issues with the Max Hauri cloud and the discontinuation of support for version 1.x devices, it is recommended to avoid using the cloud account and associated applications with version 1.x devices.

The communication with MaxSmart devices is done through HTTP GET requests over a local network. It's important to note that this communication is unsecured and in clear text. Therefore, it is advised to use the module in a trusted network environment.

## Test Script

The test script provided allows you to perform a series of tests on a MaxSmart power strip. It covers various functionalities such as powering on and off individual ports, retrieving real-time consumption data, and obtaining 24-hour consumption data.

### Prerequisites

Before running the test script, make sure you have the following prerequisites:

- Python 3.x installed on your system.
- The `maxsmart` Python module installed. You can install it by following the instructions in the [Installation](#installation) section.

### Running the Test Script

To run the test script, execute the following command in your terminal:

```bash
python test_scripts/test_script.py
```

The script will attempt to discover MaxSmart devices on the network. If no devices are found, it will display an error message. If devices are found, you will be presented with a menu to select a device for testing.

Follow the on-screen instructions and warnings to proceed with the test.

## Installation

To install the `maxsmart` module, you can use `pip`, the Python package installer. Open your terminal or command prompt and run the following command:

```bash
pip install maxsmart
```
This will install the `maxsmart` module and its dependencies.

## Usage

### Discovery 

Discovery will help you find your MaxSmart device details on the local network. You can use the `MaxSmartDiscovery` class. There are two ways of using this class: 

Without argument, MaxSmartDiscovery will send a broadcast to the local network and expect all available devices to send data in return.

```python
from maxsmart import MaxSmartDiscovery
devices = MaxSmartDiscovery.discover_maxsmart()
```

**Note:** If broadcast is blocked on your network, you will not get any result.

With an ip address as argument, MaxSmartDiscovery will send a unicast message to the specified IP address. In that case, only that specific device, if present, will return data. You'll have therefore to run discovery for each specific MaxSmart device.

```python
from maxsmart import MaxSmartDiscovery
devices = MaxSmartDiscovery.discover_maxsmart(192.168.0.25)
```

The `discover_maxsmart` method returns a list of dictionaries, each representing a discovered MaxSmart device on the network. Each dictionary contains information such as the device's IP address (ip), serial number (sn), name, port name dictonary (pname), firmware version (ver).

### Device Operations

When you have the ip addresses of your devices, you can operate using the MaxSmartDevice method:

The MaxSmart Power strip as 6 ports, and the Smart plug has 1 port. Operations are made against port numbers.

1. Import the module and create an instance of the `MaxSmartDevice` class, providing the IP address of the device. For example:

   ```python
   from maxsmart import MaxSmartDevice

   device = MaxSmartDevice(192.168.0.25)
   ```

2. Use the available methods to control the device. Note that port 0 is a master port affecting all ports on the device simultaneously:

   - Turn on a specific port/socket:
     ```python
     device.turn_on(1)  # Turns on port 1
     ```

   - Turn on all ports/sockets:
     ```python
     device.turn_on(0)  # Turns on all ports
     ```

   - Turn off a specific port/socket:
     ```python
     device.turn_off(2)  # Turns off port 2
     ```

   - Check the state of all ports/sockets:
     ```python
     state = device.check_state()  # Returns a list with the state of each port
     ```

   - Check the state of a specific port/socket:
     ```python
     port_state = device.check_port_state(3)  # Returns the state of port 3
     ```

   - Retrieve real-time power consumption data for a specific port/socket (watts):
     ```python
     power_data = device.get_power_data(3)   # Get the power data for the specified port
     ```

   - Retrieve 24-hour points of consumption data for a specific port/socket (kWh):
     ```python
     hourly_data = device.get_hourly_data(3)  # Get the last 24 points of hourly consumption data for the specified port
     ```

**DISCLAIMER:** Please note that the `MaxSmartDevice` class is specifically designed for Revogi-based Max Hauri MaxSmart PowerStrips running on v1.30 firmware. Compatibility with other devices or firmware versions is not guaranteed.

## Credits

The `maxsmart` module has been made possible by the reverse engineering and documentation work done by GitHub user `@altery`. They have provided valuable insights into the communication protocol of MaxSmart PowerStrips. You can find their documentation here: [GitHub - mh-maxsmart-powerstation](https://github.com/altery/mh-maxsmart-powerstation)

## License

[MIT](LICENSE)
