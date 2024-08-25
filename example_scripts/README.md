# MaxSmart Example Scripts

This folder contains example scripts designed to demonstrate how to use the `maxsmart` Python module to interact with MaxSmart devices. These scripts illustrate various functionalities, showing users how to integrate and control their devices in their own projects.

## Overview of Scripts

1. **`maxsmart_tests.py`**

   - **Use Case:** This script discovers available MaxSmart devices and allows users to select a device for testing control operations. It provides options to turn ports on and off while demonstrating how to retrieve power consumption data.
   - **Purpose:** Ideal for users wanting to understand how to perform basic control functions on specific ports of a MaxSmart device.
   - **Usage of `maxsmart` Module:** Utilizes the `MaxSmartDiscovery` class for discovering devices and the `MaxSmartDevice` class for controlling ports and retrieving power data.

2. **`get_port_names.py`**

   - **Use Case:** This script discovers MaxSmart devices on the network and fetches the names of their ports, allowing users to easily identify which devices and ports are available.
   - **Purpose:** Useful for users who need to understand the configuration of their MaxSmart devices before implementing actions in their scripts.
   - **Usage of `maxsmart` Module:** Leverages `MaxSmartDiscovery` for discovering devices and `MaxSmartDevice` to retrieve port names.

3. **`retrieve_states.py`**

   - **Use Case:** This script allows users to specify a strip name and retrieve the state of the ports for that device, showing whether they are on or off.
   - **Purpose:** Perfect for users needing to monitor the current state of their devices and ports programmatically.
   - **Usage of `maxsmart` Module:** Uses the `MaxSmartDiscovery` class to find devices and `MaxSmartDevice` to check the state of individual ports.

4. **`test_discovery.py`**

   - **Use Case:** This script demonstrates the device discovery feature of the `maxsmart` module by finding and printing a list of discovered devices on the network.
   - **Purpose:** Great for users who want to confirm the connectivity and availability of their MaxSmart devices.
   - **Usage of `maxsmart` Module:** Primarily utilizes the `MaxSmartDiscovery` class for device discovery.

5. **`test_socket.py`**

   - **Use Case:** This script sends a UDP broadcast message to discover MaxSmart devices, useful for scenarios where users want to implement custom networking solutions.
   - **Purpose:** Beneficial for advanced users wanting to dive into network-level interactions with their devices.
   - **Usage of `maxsmart` Module:** While it doesn't directly use high-level `maxsmart` module classes, it demonstrates how to discover devices via UDP broadcasting, complementing the functionalities provided by `MaxSmartDiscovery`.

6. **`rename_ports.py`**
   - **Use Case:** Allows users to rename the strip and individual port names while validating the input length. If the name exceeds 21 characters or is empty, the user is prompted to fix or ignore the change.
   - **Purpose:** Enables customization of port names, enhancing user interaction within the Home Assistant integration.
   - **Usage of `maxsmart` Module:** Uses the `MaxSmartDevice` class to change the port names after validation.

## Getting Started

1. **Install Requirements:** Ensure that the `maxsmart` module is installed in your Python environment along with any additional dependencies. Use the following command:

   ```
   pip install -r requirements.txt
   ```

2. **Running Scripts:** Make sure to give execute permissions to the scripts if running on a Unix-like OS:

   ```
   chmod +x script_name.py
   ```

   And run the scripts using:

   ```
   ./script_name.py
   ```

3. **Customizing Scripts:** Feel free to modify and extend these scripts based on your unique requirements. The provided examples serve as a foundation for building more complex interactions with your MaxSmart devices.

## Conclusion

These example scripts serve as a starting point for users interested in integrating MaxSmart devices into their automation projects or personal applications. Whether you're looking to control devices, monitor their states, or discover new hardware, these scripts illustrate practical use cases for the `maxsmart` module.
