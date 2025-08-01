# device/configuration.py

from ..exceptions import (
    StateError,
    CommandError,
    FirmwareError,
    DeviceOperationError,
    DiscoveryError,
    ConnectionError,
)
from ..const import (
    CMD_SET_PORT_NAME,
    MAX_PORT_NUMBER,
    MAX_PORT_NAME_LENGTH,
    IN_DEVICE_NAME_VERSION,
    RESPONSE_CODE_SUCCESS,
)


class ConfigurationMixin:
    """Mixin class providing device configuration functionality (port names, etc.)."""

    async def retrieve_port_names(self):
        """Retrieve current port names by sending a discovery request."""
        if not self.ip:
            raise StateError(
                "ERROR_MISSING_EXPECTED_DATA", self.user_locale
            )  # Change to the error key for missing IP

        from ..discovery import MaxSmartDiscovery

        try:
            discovery = MaxSmartDiscovery()
            devices = await discovery.discover_maxsmart(ip=self.ip)

            if not devices:
                raise DiscoveryError(
                    "ERROR_NO_DEVICES_FOUND", self.user_locale
                )  # Use the error key for no devices found

            device = devices[0]  # Access the first (and only) device
            self.strip_name = device.get("name", self.strip_name)  # Name for port 0
            self.port_names = device.get(
                "pname", self.port_names
            )  # Names for ports 1 to 6

            # Combine in a dictionary
            port_mapping = {
                "Port 0": self.strip_name,
            }
            for i in range(1, 7):
                port_mapping[f"Port {i}"] = (
                    self.port_names[i - 1]
                    if i - 1 < len(self.port_names)
                    else f"Port {i}"
                )

            return port_mapping  # Return the dictionary

        except ConnectionError:
            raise ConnectionError(
                "ERROR_NETWORK_ISSUE", self.user_locale
            )  # Raise with network error key
        except DiscoveryError:
            raise DiscoveryError(
                "ERROR_NO_DEVICES_FOUND", self.user_locale
            )  # Raise with standardized message
        except Exception as e:
            raise StateError(
                "ERROR_UNEXPECTED", self.user_locale, detail=str(e)
            )  # Use the unexpected error key

    async def change_port_name(self, port, new_name):
        """
        Change the name of a specific port asynchronously.

        Args:
            port (int): The port number (0-6) to change the name for.
            new_name (str): The new name for the port (max 21 characters).

        Raises:
            StateError: If the port number is invalid, the new name is empty, or the new name is too long.
            CommandError: If there's an error sending the command to the device.
            FirmwareError: If the device firmware does not support in-device port renaming.
        """
        # Check firmware version for in-device renaming support
        if self.version != IN_DEVICE_NAME_VERSION:
            raise FirmwareError(
                self.ip, self.version, self.user_locale, IN_DEVICE_NAME_VERSION
            )

        if not 0 <= port <= MAX_PORT_NUMBER:
            raise DeviceOperationError(
                self.user_locale
            )  # Raise with invalid parameters error

        if not new_name or new_name.strip() == "":
            raise StateError(
                "ERROR_INVALID_PARAMETERS", self.user_locale
            )  # Invalid parameters error

        if len(new_name) > MAX_PORT_NAME_LENGTH:
            raise StateError("ERROR_UNEXPECTED_STATE", self.user_locale)  # Length error

        try:
            params = {"port": port, "name": new_name}
            # Correctly call the send command method
            response = await self._send_command(
                CMD_SET_PORT_NAME, params
            )  # Updated method call

            # Check if the command was successful
            if response.get("code") == RESPONSE_CODE_SUCCESS:
                if port == 0:
                    self.strip_name = new_name  # Update the strip name
                else:
                    self.port_names[port - 1] = new_name  # Update the port name

                return True  # Successfully changed the name
            else:
                raise CommandError(
                    "ERROR_COMMAND_EXECUTION", self.user_locale
                )  # Handle command execution error

        except CommandError as e:
            raise CommandError(
                "ERROR_COMMAND_EXECUTION", self.user_locale
            )  # Handle command execution error
        except Exception as e:
            raise StateError(self.user_locale)  # Provide a more generalized state error