# const.py

# Discovery constants
DISCOVERY_MESSAGE = "00dv=all,{datetime};"  # UDP broadcast message template
DEFAULT_TARGET_IP = "255.255.255.255"  # Default IP for broadcasting
UDP_PORT = 8888  # Port for UDP communication
UDP_TIMEOUT = 2  # Timeout in seconds for waiting on UDP responses

# Error messages for discovery
DISCOVERY_ERROR_MESSAGES = {
    "en": {
        "ERROR_NO_DEVICES_FOUND": "No MaxSmart devices found.",
        "ERROR_INVALID_JSON": "Received invalid JSON data.",
        "ERROR_MISSING_EXPECTED_DATA": "Missing expected data in device response.",
        "ERROR_UDP_TIMEOUT": "Discovery process timed out while waiting for device responses.",  # New message
    },
    "fr": {
        "ERROR_NO_DEVICES_FOUND": "Aucun appareil MaxSmart trouvé.",
        "ERROR_INVALID_JSON": "Données JSON invalides reçues.",
        "ERROR_MISSING_EXPECTED_DATA": "Données attendues manquantes dans la réponse de l'appareil.",
        "ERROR_UDP_TIMEOUT": "Le processus de découverte a expiré en attendant des réponses des appareils.",  # New message
    },
    "de": {
        "ERROR_NO_DEVICES_FOUND": "Keine MaxSmart-Geräte gefunden.",
        "ERROR_INVALID_JSON": "Ungültige JSON-Daten empfangen.",
        "ERROR_MISSING_EXPECTED_DATA": "Erwartete Daten in der Geräteantwort fehlen.",
        "ERROR_UDP_TIMEOUT": "Der Entdeckungsprozess wurde abgebrochen, während auf die Antworten der Geräte gewartet wurde.",  # New message
    },
}

# Additional logging messages for discovery
DISCOVERY_LOGGING_MESSAGES = {
    "en": {
        "LOG_NO_DEVICES_FOUND": "No MaxSmart devices found during discovery.",
        "LOG_RETRY_DISCOVERY": "Retrying discovery...",
        "LOG_UDP_TIMEOUT": "Discovery process timed out while waiting for device responses.",  # New log
    },
    "fr": {
        "LOG_NO_DEVICES_FOUND": "Aucun appareil MaxSmart trouvé lors de la découverte.",
        "LOG_RETRY_DISCOVERY": "Nouvelle tentative de découverte...",
        "LOG_UDP_TIMEOUT": "Le processus de découverte a expiré en attendant des réponses des appareils.",  # New log
    },
    "de": {
        "LOG_NO_DEVICES_FOUND": "Keine MaxSmart-Geräte während der Entdeckung gefunden.",
        "LOG_RETRY_DISCOVERY": "Erneutes Versuchen der Entdeckung...",
        "LOG_UDP_TIMEOUT": "Der Entdeckungsprozess wurde abgebrochen, während auf die Antworten der Geräte gewartet wurde.",  # New log
    },
}

# Multilingual error messages for device-related errors
# const.py

# Multilingual error messages for device-related errors
DEVICE_ERROR_MESSAGES = {
    "en": {
        "ERROR_INVALID_PORT": "Invalid port number.",
        "ERROR_PORT_NOT_FOUND": "Port number not found.",
        "ERROR_COMMAND_EXECUTION": "Command execution error.",
        "ERROR_UNEXPECTED_STATE": "Unexpected state for the port.",
        "ERROR_DEVICE_NOT_FOUND": "Device not found.",
        "ERROR_DEVICE_TIMEOUT": "Device did not respond in time.",
        "ERROR_INVALID_PARAMETERS": "Invalid parameters provided for the operation.",
        "ERROR_INVALID_TYPE": "Invalid type. Must be 0 (hourly), 1 (daily), or 2 (monthly).",  # New message for type error
        "ERROR_UNEXPECTED": "Unexpected error occurred: {detail}",
    },
    "fr": {
        "ERROR_INVALID_PORT": "Numéro de port invalide.",
        "ERROR_PORT_NOT_FOUND": "Numéro de port non trouvé.",
        "ERROR_COMMAND_EXECUTION": "Erreur lors de l'exécution de la commande.",
        "ERROR_UNEXPECTED_STATE": "État inattendu pour le port.",
        "ERROR_DEVICE_NOT_FOUND": "Appareil non trouvé.",
        "ERROR_DEVICE_TIMEOUT": "L'appareil n'a pas répondu à temps.",
        "ERROR_INVALID_PARAMETERS": "Paramètres invalides fournis pour l'opération.",
        "ERROR_INVALID_TYPE": "Type invalide. Doit être 0 (horaire), 1 (journalier) ou 2 (mensuel).",  # New message in French
        "ERROR_UNEXPECTED": "Une erreur inattendue s'est produite : {detail}",  # New message for unexpected errors
    },
    "de": {
        "ERROR_INVALID_PORT": "Ungültige Portnummer.",
        "ERROR_PORT_NOT_FOUND": "Portnummer nicht gefunden.",
        "ERROR_COMMAND_EXECUTION": "Fehler bei der Ausführung des Befehls.",
        "ERROR_UNEXPECTED_STATE": "Unerwarteter Zustand für den Port.",
        "ERROR_DEVICE_NOT_FOUND": "Gerät nicht gefunden.",
        "ERROR_DEVICE_TIMEOUT": "Das Gerät hat nicht geantwortet.",
        "ERROR_INVALID_PARAMETERS": "Ungültige Parameter für die Operation bereitgestellt.",
        "ERROR_INVALID_TYPE": "Ungültiger Typ. Muss 0 (stündlich), 1 (täglich) oder 2 (monatlich) sein.",  # New message in German
        "ERROR_UNEXPECTED": "Unerwartete Fehler: {detail}",  # New message for unexpected errors
    },
}




# Error messages for connection-related issues
CONNECTION_ERROR_MESSAGES = {
    "en": {
        "ERROR_NETWORK_ISSUE": "Network issue encountered: {detail}",
    },
    "fr": {
        "ERROR_NETWORK_ISSUE": "Problème de réseau rencontré: {detail}",
    },
    "de": {
        "ERROR_NETWORK_ISSUE": "Netzwerkproblem aufgetreten: {detail}",
    },
}

# Additional logging messages for state errors
STATE_ERROR_MESSAGES = {
    "en": {
        "ERROR_STATE_INVALID": "Invalid state encountered.",
    },
    "fr": {
        "ERROR_STATE_INVALID": "État invalide rencontré.",
    },
    "de": {
        "ERROR_STATE_INVALID": "Ungültiger Zustand aufgetreten.",
    },
}

# Additional logging messages for device states
DEVICE_STATE_ERROR_MESSAGES = {
    "en": {
        "LOG_DEVICE_NOT_FOUND": "Device '{device_name}' was not found during discovery.",
        "LOG_DEVICE_TIMEOUT": "The device '{device_name}' did not respond in time.",
    },
    "fr": {
        "LOG_DEVICE_NOT_FOUND": "L'appareil '{device_name}' n'a pas été trouvé lors de la découverte.",
        "LOG_DEVICE_TIMEOUT": "L'appareil '{device_name}' n'a pas répondu à temps.",
    },
    "de": {
        "LOG_DEVICE_NOT_FOUND": "Gerät '{device_name}' wurde während der Entdeckung nicht gefunden.",
        "LOG_DEVICE_TIMEOUT": "Das Gerät '{device_name}' hat nicht rechtzeitig geantwortet.",
    },
}

# Multilingual error messages for device-related firmware issues
FIRMWARE_ERROR_MESSAGES = {
    "en": {
        "ERROR_FIRMWARE_NOT_SUPPORTED": "Device with IP {device_ip} has an unsupported firmware version: {firmware_version}.",
    },
    "fr": {
        "ERROR_FIRMWARE_NOT_SUPPORTED": "L'appareil avec l'IP {device_ip} a une version de firmware non prise en charge : {firmware_version}.",
    },
    "de": {
        "ERROR_FIRMWARE_NOT_SUPPORTED": "Gerät mit der IP {device_ip} hat eine nicht unterstützte Firmware-Version: {firmware_version}.",
    },
}

# const.py

# Currency symbols mapped to identifiers
CURRENCY_SYMBOLS = {
    0: "€",  # Euro
    1: "$",  # Dollar
    2: "¥",  # Yen
    3: "CHF"  # Swiss Francs
}

STATISTICS_TIME_FRAME = {
    0: "Hourly",
    1: "Daily",
    2: "Monthly"
}


# Response codes
RESPONSE_CODE_SUCCESS = 200  # Successful request
RESPONSE_CODE_ERROR = 400     # Client error (bad request)
RESPONSE_CODE_NOT_FOUND = 404  # Resource not found
RESPONSE_CODE_SERVER_ERROR = 500  # Internal server error

# Command constants
CMD_RESPONSE_TIMEOUT = 1
CMD_RETRIES = 3

# Firmware version supported by the module
SUPPORTED_FIRMWARE_VERSION = "1.30"  # Only this version is supported
LIMITED_SUPPORT_FIRMWARE = "2.11"  # 2.11 firmware supports local basic commands, but no name management

# Device command identifiers
CMD_SET_PORT_STATE = 200  # Command to set the state (on/off) of a specific port
CMD_GET_DEVICE_DATA = 511  # Command to get various data from the device (wattage, amperage, switch states)
CMD_GET_STATISTICS = 510  # Command to get hourly data
CMD_SET_PORT_NAME = 201  # Command to set or change the name of a specific port

# Default values for ports and strip
DEFAULT_PORT_NAMES = [f"Port {i}" for i in range(1, 7)]  # Default port names: Port 1 to Port 6
DEFAULT_STRIP_NAME = "Strip"  # Default name for the power strip

# Additional configurations
MAX_PORT_NUMBER = 6  # Maximum valid port number
MAX_PORT_NAME_LENGTH = 21  # Maximum length for port names

# State values for ports
STATE_ON = 1  # State value for "on"
STATE_OFF = 0  # State value for "off"
