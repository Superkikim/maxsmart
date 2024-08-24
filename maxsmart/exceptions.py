# exceptions.py

class MaxSmartError(Exception):
    """Base class for all MaxSmart exceptions."""
    def __init__(self, message):
        super().__init__(message)

class CommandError(MaxSmartError):
    """Exception raised for errors in command execution."""
    def __init__(self, message):
        super().__init__(f"Command execution error: {message}")

class DeviceNotFoundError(MaxSmartError):
    """Exception raised when a specific device is not found during discovery."""
    def __init__(self, device_name):
        super().__init__(f"Device '{device_name}' was not found.")


class DeviceTimeoutError(MaxSmartError):
    """Exception raised when a device does not respond in time."""
    def __init__(self, device_name):
        super().__init__(f"The device '{device_name}' did not respond in time.")


class ConnectionError(MaxSmartError):
    """Exception raised for errors related to network connections."""
    def __init__(self, message):
        super().__init__(f"Network issue encountered: {message}")


class DiscoveryError(MaxSmartError):
    """Exception raised when device discovery fails."""
    def __init__(self, message):
        super().__init__(f"Discovery error: {message}")


class FirmwareError(MaxSmartError):
    """Exception raised for issues related to firmware version."""
    def __init__(self, device_ip, firmware_version):
        super().__init__(f"Device with IP {device_ip} has firmware version {firmware_version}. This module has been tested with MaxSmart devices with firmware version 1.30.")

class StateError(MaxSmartError):
    """Exception raised for errors related to device states."""
    def __init__(self, message):
        super().__init__(f"State error: {message}")
