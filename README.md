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
python test_script.py --ip <power_strip_ip> --sn <power_strip_sn>
```

Replace `<power_strip_ip>` with the IP address of your MaxSmart power strip and `<power_strip_sn>` with the serial number (SN) of your power strip. This information can usually be found on the power strip itself or in its documentation.

**NOTE:** The test script will power down all devices plugged into the power strip during the test. Make sure you are aware of the potential consequences before proceeding.

### Output and Example

The test script provides detailed output during the test execution. It displays the status of each action, countdown during the waiting periods, and the retrieved consumption data in tabular format.

Here is an example command to run the test script:

```
python test_script.py --ip 192.168.0.123 --sn ABC123456789
```

This command will run the test script on a MaxSmart power strip with the specified IP address and serial number. Follow the on-screen instructions and warnings to proceed with the test.

## Getting started

### Prerequisites

- Python 3.x installed on your system.
- The `maxsmart` Python module installed. You can install it by following the instructions in the [Installation](#installation) section.

### Installation {#installation}

To install the `maxsmart` module, you can use `pip`, the Python package installer. Open your terminal or command prompt and run the following command:

```bash
pip install maxsmart
```
This will install the `maxsmart` module and its dependencies.

### Usage

To use the `maxsmart` module, follow these steps:

1. Import the module: `from maxsmart import MaxSmart`
2. Create an instance of the `MaxSmart` class, providing the IP address and serial number of your PowerStrip:

   ```python
   maxsmart = MaxSmart('192.168.1.1', 'test_sn')
   ```

3. Use the available methods to control the PowerStrip:

   - Turn on a specific port/socket:
     ```python
     maxsmart.turn_on(1)  # Turns on port 1
     ```

   - Turn off a specific port/socket:
     ```python
     maxsmart.turn_off(2)  # Turns off port 2
     ```

   - Check the state of all ports/sockets:
     ```python
     state = maxsmart.check_state()  # Returns a list with the state of each port
     ```

   - Check the state of a specific port/socket:
     ```python


     port_state = maxsmart.check_port_state(3)  # Returns the state of port 3
     ```

   - Retrieve 24 data points of the last 24 hourly power consumption (in watt) for a specific port/socket:
     ```python
     port = 3  # Specify the port/socket for which to retrieve data
     data = maxsmart.get_hourly_data(port)  # Retrieves the hourly power consumption data for the specified port
     print(data)  # Prints the retrieved data points
     ```

**Important:** Please note that the `maxsmart` module is specifically designed for Revogi-based Max Hauri MaxSmart PowerStrips running on v1.x firmware. Compatibility with other devices or firmware versions is not guaranteed.


## Credits

The `maxsmart` module has been made possible by the reverse engineering and documentation work done by GitHub user `@altery`. They have provided valuable insights into the communication protocol of MaxSmart PowerStrips. You can find their documentation here: [GitHub - mh-maxsmart-powerstation](https://github.com/altery/mh-maxsmart-powerstation)

## License

[MIT](LICENSE)
