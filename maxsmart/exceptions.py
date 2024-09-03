# exceptions.py
import logging

from .const import (
    DISCOVERY_ERROR_MESSAGES, 
    DISCOVERY_LOGGING_MESSAGES, 
    DEVICE_ERROR_MESSAGES, 
    CONNECTION_ERROR_MESSAGES, 
    DEVICE_STATE_ERROR_MESSAGES,
    FIRMWARE_ERROR_MESSAGES,
    STATE_ERROR_MESSAGES,  # Add this line
)

from .utils import (
    get_user_message,
    log_message,  # Ensure proper imports for localization and logging
)

class MaxSmartError(Exception):
    """Base class for all MaxSmart exceptions."""
    
    def __init__(self, message, user_locale=None):
        self.user_locale = user_locale
        super().__init__(message)
        
    def log_error(self, log_message_key, logging_messages_dict):
        """Logs the error message using the provided log message key."""
        if self.user_locale:
            log_message(logging_messages_dict, log_message_key, self.user_locale)

class DiscoveryError(MaxSmartError):
    """Exception raised when device discovery fails."""

    def __init__(self, error_key, user_locale):
        self.error_key = error_key
        self.user_locale = user_locale
        
        # Step 1: Get the localized error message
        message = get_user_message(DISCOVERY_ERROR_MESSAGES, self.error_key, self.user_locale)
        
        # Step 2: Log the localized message
        log_message(DISCOVERY_LOGGING_MESSAGES, "LOG_NO_DEVICES_FOUND", user_locale, level=logging.ERROR)

        # Step 3: Raise the error with the localized message
        super().__init__(f"Discovery error: {message}")

class UdpTimeoutInfo(MaxSmartError):
    """Exception raised when a UDP timeout occurs."""

    def __init__(self, user_locale):
        self.user_locale = user_locale

        # Get the localized message for the timeout
        message = get_user_message(DISCOVERY_ERROR_MESSAGES, "ERROR_UDP_TIMEOUT", self.user_locale)
        
        # Log the localized message
        log_message(DISCOVERY_LOGGING_MESSAGES, "LOG_UDP_TIMEOUT", self.user_locale, level=logging.INFO)

        # Instead of raising an error, initialize with the message for further usage if needed
        super().__init__(message)
        
class ConnectionError(MaxSmartError):
    """Exception raised for errors related to network connections."""
    
    def __init__(self, user_locale, error_key="ERROR_NETWORK_ISSUE", *args, **kwargs):
        self.user_locale = user_locale
        self.error_key = error_key

        # Use the utility function to get the localized error message
        message = get_user_message(CONNECTION_ERROR_MESSAGES, self.error_key, self.user_locale)
        
        # Log the localized message using the utility function
        log_message(CONNECTION_ERROR_MESSAGES, self.error_key, self.user_locale, detail=", ".join(args), level=logging.ERROR)

        super().__init__(message)

class DeviceError(MaxSmartError):
    """Exception raised for errors related to device operations."""

    def __init__(self, error_key, user_locale):
        self.error_key = error_key
        self.user_locale = user_locale
        
        # Use the utility function to get the localized error message
        message = get_user_message(DEVICE_ERROR_MESSAGES, self.error_key, self.user_locale)
        
        # Log the localized message using the utility function (if applicable)
        log_message(DEVICE_ERROR_MESSAGES, self.error_key, self.user_locale, level=logging.ERROR)

        super().__init__(f"Device error: {message}")

class CommandError(MaxSmartError):
    """Exception raised for errors in command execution."""
    
    def __init__(self, user_locale, error_key="ERROR_COMMAND_EXECUTION", *args, **kwargs):
        self.user_locale = user_locale
        self.error_key = error_key
        
        # Use the utility function to get the localized error message
        message = get_user_message(DEVICE_ERROR_MESSAGES, self.error_key, self.user_locale)

        # Log the localized message using the utility function
        log_message(DEVICE_ERROR_MESSAGES, self.error_key, self.user_locale, level=logging.ERROR)

        super().__init__(message)

    @staticmethod
    def get_error_message(error_key, user_locale, **kwargs):
        lang = user_locale.split('_')[0]  # Extracting language code
        message_template = DEVICE_ERROR_MESSAGES.get(lang, DEVICE_ERROR_MESSAGES["en"]).get(error_key, "Unknown command error.")
        return message_template.format(**kwargs)  # Format the message with any additional details

class DeviceNotFoundError(MaxSmartError):
    """Exception raised when a specific device is not found during discovery."""

    def __init__(self, device_name, user_locale):
        self.device_name = device_name
        self.user_locale = user_locale
        
        # Step 1: Get the localized error message
        error_key = "ERROR_NO_DEVICES_FOUND"
        message = get_user_message(DISCOVERY_ERROR_MESSAGES, error_key, self.user_locale)
        
        # Step 2: Log the localized message
        log_key = "LOG_DEVICE_NOT_FOUND"
        log_message(DEVICE_STATE_ERROR_MESSAGES, log_key, self.user_locale, device_name=self.device_name, level=logging.ERROR)

        # Step 3: Raise the error with the localized message
        super().__init__(message)

class DeviceTimeoutError(MaxSmartError):
    """Exception raised when a device does not respond in time."""

    def __init__(self, device_name, user_locale):
        self.device_name = device_name
        self.user_locale = user_locale

        # Step 1: Get the localized error message
        error_key = "ERROR_DEVICE_TIMEOUT"
        message = get_user_message(DISCOVERY_ERROR_MESSAGES, error_key, self.user_locale)

        # Step 2: Log the localized message
        log_key = "LOG_DEVICE_TIMEOUT"
        log_message(DEVICE_STATE_ERROR_MESSAGES, log_key, self.user_locale, device_name=self.device_name, level=logging.ERROR)

        # Step 3: Raise the error with the localized message
        super().__init__(message)
            
class DeviceOperationError(MaxSmartError):
    """Exception raised for invalid parameters during device operations."""

    def __init__(self, user_locale):
        self.user_locale = user_locale

        # Get the localized error message for invalid parameters
        error_key = "ERROR_INVALID_PARAMETERS"
        message = get_user_message(DEVICE_ERROR_MESSAGES, error_key, self.user_locale)

        # Log the localized message
        log_message(DEVICE_ERROR_MESSAGES, error_key, self.user_locale, level=logging.ERROR)

        # Raise the error with the localized message
        super().__init__(message)

class FirmwareError(MaxSmartError):
    """Exception raised for issues related to firmware version."""
    
    def __init__(self, device_ip, firmware_version, user_locale):
        self.device_ip = device_ip
        self.firmware_version = firmware_version
        self.user_locale = user_locale
        
        # Use the utility function to get the localized error message
        error_key = "ERROR_FIRMWARE_NOT_SUPPORTED"
        message = get_user_message(FIRMWARE_ERROR_MESSAGES, error_key, self.user_locale)
        
        # Log the localized message using the utility function
        log_message(FIRMWARE_ERROR_MESSAGES, error_key, self.user_locale, device_ip=self.device_ip, firmware_version=self.firmware_version, level=logging.WARNING)

        super().__init__(message)

class StateError(MaxSmartError):
    """Exception raised for errors related to device states."""
    
    def __init__(self, message, user_locale=None):
        # Store the user locale for possible future use
        self.user_locale = user_locale
        
        # Step 1: Get the localized error message
        # Default to a generic message if user_locale is not provided
        error_key = "ERROR_STATE_INVALID"
        localized_message = get_user_message(STATE_ERROR_MESSAGES, error_key, user_locale)

        # Step 2: Log the localized message
        log_message(STATE_ERROR_MESSAGES, error_key, user_locale, level=logging.ERROR)

        # Step 3: Raise the error with the localized message
        # Initialize the base class with a more useful message
        super().__init__(localized_message)  # Pass in the localized message to the base class

