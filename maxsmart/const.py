# const.py

# -------------------------
# Discovery Constants
# -------------------------
DISCOVERY_MESSAGE = "00dv=all,{datetime};"  # UDP broadcast message template
DEFAULT_TARGET_IP = "255.255.255.255"  # Default IP for broadcasting
UDP_PORT = 8888  # Port for UDP communication

# Set to desired timeout to adjust at run time with export UDP_TIMEOUT=<seconds>
UDP_TIMEOUT = 2  # timeout in seconds for wating on UDP responses. Default to 2

# Error Messages for Discovery
DISCOVERY_ERROR_MESSAGES = {
    "en": {
        "ERROR_NO_DEVICES_FOUND": "No MaxSmart devices found.",
        "ERROR_INVALID_JSON": "Received invalid JSON data.",
        "ERROR_MISSING_EXPECTED_DATA": "Missing expected data in device response.",
        "ERROR_UDP_TIMEOUT": "Discovery process timed out while waiting for device responses.",
        "ERROR_DISCOVERY_FAILED": "Device discovery failed: {detail}",
        "ERROR_NETWORK_UNREACHABLE": "Network unreachable during discovery: {detail}",
        "ERROR_INVALID_IP_FORMAT": "Invalid IP address format: {ip} - {detail}",
    },
    "fr": {
        "ERROR_NO_DEVICES_FOUND": "Aucun appareil MaxSmart trouvé.",
        "ERROR_INVALID_JSON": "Données JSON invalides reçues.",
        "ERROR_MISSING_EXPECTED_DATA": "Données attendues manquantes dans la réponse de l'appareil.",
        "ERROR_UDP_TIMEOUT": "Le processus de découverte a expiré en attendant des réponses des appareils.",
        "ERROR_DISCOVERY_FAILED": "La découverte d'appareil a échoué: {detail}",
        "ERROR_NETWORK_UNREACHABLE": "Réseau inatteignable pendant la découverte: {detail}",
        "ERROR_INVALID_IP_FORMAT": "Format d'adresse IP invalide: {ip} - {detail}",
    },
    "de": {
        "ERROR_NO_DEVICES_FOUND": "Keine MaxSmart-Geräte gefunden.",
        "ERROR_INVALID_JSON": "Ungültige JSON-Daten empfangen.",
        "ERROR_MISSING_EXPECTED_DATA": "Erwartete Daten in der Geräteantwort fehlen.",
        "ERROR_UDP_TIMEOUT": "Der Entdeckungsprozess wurde abgebrochen, während auf die Antworten der Geräte gewartet wurde.",
        "ERROR_DISCOVERY_FAILED": "Geräteerkennung fehlgeschlagen: {detail}",
        "ERROR_NETWORK_UNREACHABLE": "Netzwerk während der Erkennung nicht erreichbar: {detail}",
        "ERROR_INVALID_IP_FORMAT": "Ungültiges IP-Adressformat: {ip} - {detail}",
    },
}

ERROR_STATISTICS_NOT_AVAILABLE = {
    "en": "Statistics are not available for this device version.",
    "fr": "Les statistiques ne sont pas disponibles pour cette version de l'appareil.",
    "es": "Las estadísticas no están disponibles para esta versión del dispositivo."
}

# Logging Messages for Discovery
DISCOVERY_LOGGING_MESSAGES = {
    "en": {
        "LOG_NO_DEVICES_FOUND": "No MaxSmart devices found during discovery.",
        "LOG_RETRY_DISCOVERY": "Retrying discovery...",
        "LOG_UDP_TIMEOUT": "Discovery process timed out while waiting for device responses.",
        "LOG_DISCOVERY_START": "Starting MaxSmart device discovery on network {network}",
        "LOG_DEVICE_FOUND": "Found MaxSmart device: {name} ({ip}) - FW: {firmware}",
        "LOG_HTTP_TIMEOUT": "HTTP request timeout after {timeout}s for device {ip} (attempt {attempt}/{max_attempts})",
        "LOG_CONNECTION_ERROR": "Connection error for device {ip}: {error}",
        "LOG_DISCOVERY_ERROR": "Discovery error for {ip}: {error}",
    },
    "fr": {
        "LOG_NO_DEVICES_FOUND": "Aucun appareil MaxSmart trouvé lors de la découverte.",
        "LOG_RETRY_DISCOVERY": "Nouvelle tentative de découverte...",
        "LOG_UDP_TIMEOUT": "Le processus de découverte a expiré en attendant des réponses des appareils.",
        "LOG_DISCOVERY_START": "Démarrage de la découverte d'appareils MaxSmart sur le réseau {network}",
        "LOG_DEVICE_FOUND": "Appareil MaxSmart trouvé: {name} ({ip}) - FW: {firmware}",
        "LOG_HTTP_TIMEOUT": "Timeout de requête HTTP après {timeout}s pour l'appareil {ip} (tentative {attempt}/{max_attempts})",
        "LOG_CONNECTION_ERROR": "Erreur de connexion pour l'appareil {ip}: {error}",
        "LOG_DISCOVERY_ERROR": "Erreur de découverte pour {ip}: {error}",
    },
    "de": {
        "LOG_NO_DEVICES_FOUND": "Keine MaxSmart-Geräte während der Entdeckung gefunden.",
        "LOG_RETRY_DISCOVERY": "Erneutes Versuchen der Entdeckung...",
        "LOG_UDP_TIMEOUT": "Der Entdeckungsprozess wurde abgebrochen, während auf die Antworten der Geräte gewartet wurde.",
        "LOG_DISCOVERY_START": "Starte MaxSmart-Geräteerkennung im Netzwerk {network}",
        "LOG_DEVICE_FOUND": "MaxSmart-Gerät gefunden: {name} ({ip}) - FW: {firmware}",
        "LOG_HTTP_TIMEOUT": "HTTP-Anfrage-Timeout nach {timeout}s für Gerät {ip} (Versuch {attempt}/{max_attempts})",
        "LOG_CONNECTION_ERROR": "Verbindungsfehler für Gerät {ip}: {error}",
        "LOG_DISCOVERY_ERROR": "Entdeckungsfehler für {ip}: {error}",
    },
}

# -------------------------
# Device Error Messages
# -------------------------
DEVICE_ERROR_MESSAGES = {
    "en": {
        "ERROR_INVALID_PORT": "Invalid port number: {port}. Must be between 0 and {max_port}.",
        "ERROR_PORT_NOT_FOUND": "Port number not found: {port}.",
        "ERROR_COMMAND_EXECUTION": "Command execution error for device {ip}: {detail}",
        "ERROR_UNEXPECTED_STATE": "Unexpected state for port {port} on device {ip}.",
        "ERROR_DEVICE_NOT_FOUND": "Device not found at IP {ip}.",
        "ERROR_DEVICE_TIMEOUT": "Device {ip} did not respond within {timeout}s.",
        "ERROR_INVALID_PARAMETERS": "Invalid parameters provided for the operation on device {ip}: {detail}",
        "ERROR_INVALID_TYPE": "Invalid type. Must be 0 (hourly), 1 (daily), or 2 (monthly).",
        "ERROR_UNEXPECTED": "Unexpected error occurred: {detail}",
        "ERROR_INVALID_JSON": "Received invalid JSON data from device {ip}: {detail}",
        "ERROR_MISSING_EXPECTED_DATA": "Missing expected data in device response from {ip}: {detail}",
        "ERROR_HTTP_ERROR": "HTTP error {status} from device {ip}: {detail}",
        "ERROR_RESPONSE_DECODE": "Failed to decode response from device {ip}: {detail}",
    },
    "fr": {
        "ERROR_INVALID_PORT": "Numéro de port invalide: {port}. Doit être entre 0 et {max_port}.",
        "ERROR_PORT_NOT_FOUND": "Numéro de port non trouvé: {port}.",
        "ERROR_COMMAND_EXECUTION": "Erreur lors de l'exécution de la commande pour l'appareil {ip}: {detail}",
        "ERROR_UNEXPECTED_STATE": "État inattendu pour le port {port} sur l'appareil {ip}.",
        "ERROR_DEVICE_NOT_FOUND": "Appareil non trouvé à l'IP {ip}.",
        "ERROR_DEVICE_TIMEOUT": "L'appareil {ip} n'a pas répondu dans les {timeout}s.",
        "ERROR_INVALID_PARAMETERS": "Paramètres invalides fournis pour l'opération sur l'appareil {ip}: {detail}",
        "ERROR_INVALID_TYPE": "Type invalide. Doit être 0 (horaire), 1 (journalier) ou 2 (mensuel).",
        "ERROR_UNEXPECTED": "Une erreur inattendue s'est produite: {detail}",
        "ERROR_INVALID_JSON": "Données JSON invalides reçues de l'appareil {ip}: {detail}",
        "ERROR_MISSING_EXPECTED_DATA": "Données attendues manquantes dans la réponse de l'appareil {ip}: {detail}",
        "ERROR_HTTP_ERROR": "Erreur HTTP {status} de l'appareil {ip}: {detail}",
        "ERROR_RESPONSE_DECODE": "Échec du décodage de la réponse de l'appareil {ip}: {detail}",
    },
    "de": {
        "ERROR_INVALID_PORT": "Ungültige Portnummer: {port}. Muss zwischen 0 und {max_port} liegen.",
        "ERROR_PORT_NOT_FOUND": "Portnummer nicht gefunden: {port}.",
        "ERROR_COMMAND_EXECUTION": "Fehler bei der Ausführung des Befehls für Gerät {ip}: {detail}",
        "ERROR_UNEXPECTED_STATE": "Unerwarteter Zustand für Port {port} auf Gerät {ip}.",
        "ERROR_DEVICE_NOT_FOUND": "Gerät nicht gefunden unter IP {ip}.",
        "ERROR_DEVICE_TIMEOUT": "Gerät {ip} hat nicht innerhalb von {timeout}s geantwortet.",
        "ERROR_INVALID_PARAMETERS": "Ungültige Parameter für die Operation auf Gerät {ip} bereitgestellt: {detail}",
        "ERROR_INVALID_TYPE": "Ungültiger Typ. Muss 0 (stündlich), 1 (täglich) oder 2 (monatlich) sein.",
        "ERROR_UNEXPECTED": "Unerwartete Fehler: {detail}",
        "ERROR_INVALID_JSON": "Ungültige JSON-Daten von Gerät {ip} empfangen: {detail}",
        "ERROR_MISSING_EXPECTED_DATA": "Erwartete Daten in der Geräteantwort von {ip} fehlen: {detail}",
        "ERROR_HTTP_ERROR": "HTTP-Fehler {status} von Gerät {ip}: {detail}",
        "ERROR_RESPONSE_DECODE": "Fehler beim Dekodieren der Antwort von Gerät {ip}: {detail}",
    },
}

# -------------------------
# Connection Error Messages
# -------------------------
CONNECTION_ERROR_MESSAGES = {
    "en": {
        "ERROR_NETWORK_ISSUE": "Network issue for device {ip}: {detail}",
        "ERROR_TIMEOUT_DETAIL": "Request timeout for device {ip}: {detail}",
        "ERROR_CONNECTION_REFUSED": "Connection refused by device {ip}: {detail}",
        "ERROR_DNS_RESOLUTION": "DNS resolution failed for {ip}: {detail}",
        "ERROR_SOCKET_ERROR": "Socket error for device {ip}: {detail}",
        "ERROR_SSL_ERROR": "SSL error for device {ip}: {detail}",
        "ERROR_CLIENT_ERROR": "Client error for device {ip}: {detail}",
    },
    "fr": {
        "ERROR_NETWORK_ISSUE": "Problème de réseau pour l'appareil {ip}: {detail}",
        "ERROR_TIMEOUT_DETAIL": "Timeout de requête pour l'appareil {ip}: {detail}",
        "ERROR_CONNECTION_REFUSED": "Connexion refusée par l'appareil {ip}: {detail}",
        "ERROR_DNS_RESOLUTION": "Résolution DNS échouée pour {ip}: {detail}",
        "ERROR_SOCKET_ERROR": "Erreur de socket pour l'appareil {ip}: {detail}",
        "ERROR_SSL_ERROR": "Erreur SSL pour l'appareil {ip}: {detail}",
        "ERROR_CLIENT_ERROR": "Erreur client pour l'appareil {ip}: {detail}",
    },
    "de": {
        "ERROR_NETWORK_ISSUE": "Netzwerkproblem für Gerät {ip}: {detail}",
        "ERROR_TIMEOUT_DETAIL": "Anfrage-Timeout für Gerät {ip}: {detail}",
        "ERROR_CONNECTION_REFUSED": "Verbindung von Gerät {ip} verweigert: {detail}",
        "ERROR_DNS_RESOLUTION": "DNS-Auflösung für {ip} fehlgeschlagen: {detail}",
        "ERROR_SOCKET_ERROR": "Socket-Fehler für Gerät {ip}: {detail}",
        "ERROR_SSL_ERROR": "SSL-Fehler für Gerät {ip}: {detail}",
        "ERROR_CLIENT_ERROR": "Client-Fehler für Gerät {ip}: {detail}",
    },
}

# -------------------------
# State Error Messages
# -------------------------
STATE_ERROR_MESSAGES = {
    "en": {
        "ERROR_STATE_INVALID": "Invalid state encountered for device {ip}: {detail}",
        "ERROR_STATE_MISMATCH": "State mismatch for port {port} on device {ip}: expected {expected}, got {actual}",
        "ERROR_STATE_VERIFICATION": "State verification failed for port {port} on device {ip} after {attempts} attempts",
    },
    "fr": {
        "ERROR_STATE_INVALID": "État invalide rencontré pour l'appareil {ip}: {detail}",
        "ERROR_STATE_MISMATCH": "Incohérence d'état pour le port {port} sur l'appareil {ip}: attendu {expected}, obtenu {actual}",
        "ERROR_STATE_VERIFICATION": "Vérification d'état échouée pour le port {port} sur l'appareil {ip} après {attempts} tentatives",
    },
    "de": {
        "ERROR_STATE_INVALID": "Ungültiger Zustand für Gerät {ip} aufgetreten: {detail}",
        "ERROR_STATE_MISMATCH": "Zustandskonflikt für Port {port} auf Gerät {ip}: erwartet {expected}, erhalten {actual}",
        "ERROR_STATE_VERIFICATION": "Zustandsüberprüfung für Port {port} auf Gerät {ip} nach {attempts} Versuchen fehlgeschlagen",
    },
}

# -------------------------
# Device State Logging Messages
# -------------------------
DEVICE_STATE_ERROR_MESSAGES = {
    "en": {
        "LOG_DEVICE_NOT_FOUND": "Device '{device_name}' was not found during discovery at IP {ip}.",
        "LOG_DEVICE_TIMEOUT": "The device '{device_name}' at {ip} did not respond in time (timeout: {timeout}s).",
        "LOG_COMMAND_SUCCESS": "Command executed successfully for device {ip}: {command}",
        "LOG_COMMAND_RETRY": "Retrying command for device {ip} (attempt {attempt}/{max_attempts}): {command}",
        "LOG_STATE_CHANGE": "State changed for port {port} on device {ip}: {old_state} -> {new_state}",
        "LOG_DEVICE_OPERATION": "Device operation for {ip}: {command} - {detail}",
    },
    "fr": {
        "LOG_DEVICE_NOT_FOUND": "L'appareil '{device_name}' n'a pas été trouvé lors de la découverte à l'IP {ip}.",
        "LOG_DEVICE_TIMEOUT": "L'appareil '{device_name}' à {ip} n'a pas répondu à temps (timeout: {timeout}s).",
        "LOG_COMMAND_SUCCESS": "Commande exécutée avec succès pour l'appareil {ip}: {command}",
        "LOG_COMMAND_RETRY": "Nouvelle tentative de commande pour l'appareil {ip} (tentative {attempt}/{max_attempts}): {command}",
        "LOG_STATE_CHANGE": "État changé pour le port {port} sur l'appareil {ip}: {old_state} -> {new_state}",
        "LOG_DEVICE_OPERATION": "Opération d'appareil pour {ip}: {command} - {detail}",
    },
    "de": {
        "LOG_DEVICE_NOT_FOUND": "Gerät '{device_name}' wurde während der Entdeckung unter IP {ip} nicht gefunden.",
        "LOG_DEVICE_TIMEOUT": "Das Gerät '{device_name}' unter {ip} hat nicht rechtzeitig geantwortet (Timeout: {timeout}s).",
        "LOG_COMMAND_SUCCESS": "Befehl erfolgreich für Gerät {ip} ausgeführt: {command}",
        "LOG_COMMAND_RETRY": "Wiederholung des Befehls für Gerät {ip} (Versuch {attempt}/{max_attempts}): {command}",
        "LOG_STATE_CHANGE": "Zustand geändert für Port {port} auf Gerät {ip}: {old_state} -> {new_state}",
        "LOG_DEVICE_OPERATION": "Geräteoperation für {ip}: {command} - {detail}",
    },
}

# -------------------------
# Firmware Error Messages
# -------------------------
FIRMWARE_ERROR_MESSAGES = {
    "en": {
        "ERROR_FIRMWARE_NOT_SUPPORTED": "Device {ip} has unsupported firmware version {firmware_version}. Required: {required_version}",
        "ERROR_FIRMWARE_TOO_OLD": "Device {ip} firmware {firmware_version} is too old. Minimum required: {min_version}",
        "ERROR_FIRMWARE_FEATURE_UNAVAILABLE": "Feature not available on device {ip} with firmware {firmware_version}. Requires: {required_version}",
    },
    "fr": {
        "ERROR_FIRMWARE_NOT_SUPPORTED": "L'appareil {ip} a une version de firmware non prise en charge {firmware_version}. Requis: {required_version}",
        "ERROR_FIRMWARE_TOO_OLD": "Le firmware {firmware_version} de l'appareil {ip} est trop ancien. Minimum requis: {min_version}",
        "ERROR_FIRMWARE_FEATURE_UNAVAILABLE": "Fonctionnalité non disponible sur l'appareil {ip} avec le firmware {firmware_version}. Requis: {required_version}",
    },
    "de": {
        "ERROR_FIRMWARE_NOT_SUPPORTED": "Gerät {ip} hat eine nicht unterstützte Firmware-Version {firmware_version}. Erforderlich: {required_version}",
        "ERROR_FIRMWARE_TOO_OLD": "Firmware {firmware_version} des Geräts {ip} ist zu alt. Mindestens erforderlich: {min_version}",
        "ERROR_FIRMWARE_FEATURE_UNAVAILABLE": "Funktion nicht verfügbar auf Gerät {ip} mit Firmware {firmware_version}. Benötigt: {required_version}",
    },
}

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

# Firmware versions supported by the module
SUPPORTED_FIRMWARE_VERSION = "1.30"  # Only this version is supported
LIMITED_SUPPORT_FIRMWARE = "2.11"  # 2.11 firmware supports local basic commands, but no name management

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