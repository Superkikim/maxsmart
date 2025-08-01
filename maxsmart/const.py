# maxsmart/const.py

# Import all translation messages
from .messages import *

# -------------------------
# Discovery Constants
# -------------------------
DISCOVERY_MESSAGE = "00dv=all,{datetime};"  # UDP broadcast message template
DEFAULT_TARGET_IP = "255.255.255.255"  # Default IP for broadcasting
UDP_PORT = 8888  # Port for UDP communication

# Set to desired timeout to adjust at run time with export UDP_TIMEOUT=<seconds>
UDP_TIMEOUT = 2  # timeout in seconds for wating on UDP responses. Default to 2

# -------------------------
# Currency Constants
# -------------------------
CURRENCY_SYMBOLS = {
    0: "€",  # Euro
    1: "$",  # Dollar
    2: "¥",  # Yen
    3: "CHF"  # Swiss Francs
}

# -------------------------
# Statistics Constants
# -------------------------
STATISTICS_TIME_FRAME = {
    0: "Hourly",
    1: "Daily",
    2: "Monthly"
}

# -------------------------
# Response Codes
# -------------------------
RESPONSE_CODE_SUCCESS = 200  # Successful request
RESPONSE_CODE_ERROR = 400     # Client error (bad request)
RESPONSE_CODE_NOT_FOUND = 404  # Resource not found
RESPONSE_CODE_SERVER_ERROR = 500  # Internal server error

# -------------------------
# Command Constants
# -------------------------
CMD_RESPONSE_TIMEOUT = 1
CMD_RETRIES = 3

# Firmware versions and feature support
IN_DEVICE_NAME_VERSION = "1.30"  # Only this version supports in-device port renaming

# -------------------------
# Device Command Identifiers
# -------------------------
CMD_SET_PORT_STATE = 200  # Command to set the state (on/off) of a specific port
CMD_GET_DEVICE_DATA = 511  # Command to get various data from the device (wattage, amperage, switch states)
CMD_GET_STATISTICS = 510  # Command to get statistics
CMD_SET_PORT_NAME = 201  # Command to set or change the name of a specific port
CMD_GET_DEVICE_TIME = 502  # Command to query device date and time
CMD_GET_DEVICE_IDS = 124  # Command to get hardware identifiers (MAC, DAK, CPUid, cloud server)

# -------------------------
# Default Values
# -------------------------
DEFAULT_PORT_NAMES = [f"Port {i}" for i in range(1, 7)]  # Default port names: Port 1 to Port 6
DEFAULT_STRIP_NAME = "Strip"  # Default name for the power strip

# -------------------------
# Additional Configurations
# -------------------------
MAX_PORT_NUMBER = 6  # Maximum valid port number
MAX_PORT_NAME_LENGTH = 21  # Maximum length for port names

# -------------------------
# State Values for Ports
# -------------------------
STATE_ON = 1  # State value for "on"
STATE_OFF = 0  # State value for "off"

# -------------------------
# Type of Statistics
# -------------------------
HOURLY_STATS = 0
DAILY_STATS = 1
MONTHLY_STATS = 2 

# -------------------------
# Additional Configuration Constants 
# -------------------------
MAX_DEVICE_COUNT = 10  # Maximum number of devices allowed in discovery (optional configuration)
RETRY_INTERVAL = 2  # Interval in seconds for retrying commands (optional configuration)

# -------------------------
# End of constants file
# -------------------------

__all__ = [name for name in globals() if not name.startswith('_')]
