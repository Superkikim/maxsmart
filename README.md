# MaxSmart Python Module

**Version:** 2.0.0-beta1

The `maxsmart` module is designed to operate Revogi-based Max Hauri MaxSmart PowerStrips running on v1.x firmware. It enables local communication with the power strips without requiring any cloud connection or account.

**Note:** If you have upgraded your MaxSmart app to version 2, it may have pushed a new firmware to your devices, rendering this module incompatible.

## Introduction

The `maxsmart` module is developed to control Max Hauri MaxSmart devices, specifically, the MaxSmart Power Station and the MaxSmart Power Plug. These are smart home devices that provide remote control and automation capabilities. Please note that these products are no longer available on the Swiss market under the Max Hauri brand and are considered end-of-life.

## MaxSmart Overview

The MaxSmart Power Station and Power Plug are part of the MaxSmart product line, designed for smart home applications. These devices communicate over a local network using HTTP requests.

The `maxsmart` module consists of two main classes:

### 1. `MaxSmartDevice`

This class is used to interact with a specific MaxSmart device. It allows you to perform various operations like turning ports on and off, checking their states, and retrieving power consumption data.

#### Key Methods:

- **`turn_on(port)`**: Turns on the specified port or all ports if `port` is set to 0.
- **`turn_off(port)`**: Turns off the specified port or all ports if `port` is set to 0.
- **`check_state()`**: Returns the current state of all ports.
- **`check_port_state(port)`**: Returns the state of a specified port.
- **`get_power_data(port)`**: Retrieves real-time power consumption data for a specific port.
- **`get_hourly_data(port)`**: Retrieves 24-hour consumption data for a specific port.
- **`retrieve_port_names()`**: Retrieves and returns the names of the ports on the device.

### 2. `MaxSmartDiscovery`

This class is used to discover MaxSmart devices on the local network.

#### Key Method:

- **`discover_maxsmart(ip=None)`**: Discovers MaxSmart devices. If `ip` is not provided, it sends a broadcast to the local network. If an IP address is provided, it sends a unicast message to that specific device.

## Communication

The communication with MaxSmart devices is done through HTTP GET requests over a local network. It's important to note that this communication is unsecured and in clear text. Therefore, it is advised to use the module in a trusted network environment.

## Prerequisites

Before using the `maxsmart` module, make sure you have the following prerequisites:

- Python 3.x installed on your system.

## Installation

### Install from Source (Local)

Since the `maxsmart` module is not yet published on PyPI, you can install it locally from the source code. Follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your_username/maxsmart.git
   cd maxsmart
   ```

2. **Install with pip:**
   You can install the module along with its dependencies using:
   ```bash
   pip install .
   ```

This will install the `maxsmart` module and its dependencies from the local source.

## Usage

### Discovering Devices

To discover MaxSmart devices, use the `MaxSmartDiscovery` class as follows:

```python
from maxsmart import MaxSmartDiscovery

# Discover all MaxSmart devices on the network
devices = MaxSmartDiscovery.discover_maxsmart()
print(devices)  # Outputs a list of discovered devices
```

### Controlling a Device

Once you have the IP address of your MaxSmart device, you can create an instance of the `MaxSmartDevice` class and control the device:

```python
from maxsmart import MaxSmartDevice

# Create an instance of the MaxSmartDevice with the device's IP address
device = MaxSmartDevice('192.168.0.25')

# Turn on port 1
device.turn_on(1)

# Check state of all ports
state = device.check_state()
print(state)
```

### Full Example

Here's a quick example demonstrating the discovery and control of MaxSmart devices:

```python
from maxsmart import MaxSmartDiscovery, MaxSmartDevice

# Discover devices
devices = MaxSmartDiscovery.discover_maxsmart()
if devices:
    selected_device = devices[0]  # Select the first discovered device
    device = MaxSmartDevice(selected_device['ip'])

    # Retrieve port names
    port_names = device.retrieve_port_names()
    print("Port Names:", port_names)

       # Turn on port 1 and display current state
    device.turn_on(1)
    print("Current State:", device.check_state())
else:
    print("No MaxSmart devices found.")
```

## Example Scripts

The [Example Scripts](example_scripts/) directory provided allows you to perform a series of tests on a MaxSmart power strip. They are also meant as a guideline for you to create your own scripts or integration.

They cover various functionalities such as powering on and off individual ports, retrieving real-time consumption data, and obtaining 24-hour consumption data, etc...

### Running the example Scripts

Refer to the [example Scripts Readme](example_scripts/README.md) for instructions on how to run the scripts.

## Credits

The `maxsmart` module has been made possible by the reverse engineering and documentation work done by GitHub user `@altery`. They have provided valuable insights into the communication protocol of MaxSmart PowerStrips. You can find their documentation here: [GitHub - mh-maxsmart-powerstation](https://github.com/altery/mh-maxsmart-powerstation)

## License

[MIT](LICENSE)
