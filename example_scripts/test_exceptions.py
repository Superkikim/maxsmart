#!/usr/bin/env python3
# test_exceptions.py

import logging
from maxsmart.utils import get_user_locale  # Import for retrieving user locale
from maxsmart.exceptions import (
    DiscoveryError, 
    ConnectionError, 
    DeviceError, 
    CommandError, 
    DeviceNotFoundError, 
    DeviceTimeoutError, 
    FirmwareError, 
    StateError
)

# Configure logging to output to both console and log file
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_exceptions.log"),  # Log messages to test_exceptions.log file
        logging.StreamHandler()  # Log messages to console
    ]
)

def test_get_user_locale():
    user_locale = get_user_locale()
    print(f"Detected User Locale: {user_locale}")

def test_exception_classes(language):
    # Simulate setting the locale
    print(f"Simulating language setting for: {language}")
    
    # Create instances of exception classes to test them
    try:
        # Test DiscoveryError
        discovery_error = DiscoveryError("ERROR_NO_DEVICES_FOUND", language)
    except DiscoveryError as e:
        print(f"DiscoveryError: {str(e)}")
    
    try:
        # Test ConnectionError
        connection_error = ConnectionError(language, "ERROR_NETWORK_ISSUE", "Some network details")
    except ConnectionError as e:
        print(f"ConnectionError: {str(e)}")
    
    try:
        # Test DeviceError
        device_error = DeviceError("ERROR_DEVICE_NOT_FOUND", language)
    except DeviceError as e:
        print(f"DeviceError: {str(e)}")
    
    try:
        # Test CommandError
        command_error = CommandError(language, "ERROR_COMMAND_EXECUTION")
    except CommandError as e:
        print(f"CommandError: {str(e)}")

    try:
        # Test DeviceNotFoundError
        device_not_found_error = DeviceNotFoundError("DeviceX", language)
    except DeviceNotFoundError as e:
        print(f"DeviceNotFoundError: {str(e)}")

    try:
        # Test DeviceTimeoutError
        device_timeout_error = DeviceTimeoutError("DeviceX", language)
    except DeviceTimeoutError as e:
        print(f"DeviceTimeoutError: {str(e)}")
    
    try:
        # Test FirmwareError
        firmware_error = FirmwareError("192.168.1.100", "2.0", language)
    except FirmwareError as e:
        print(f"FirmwareError: {str(e)}")
    
    try:
        # Test StateError
        state_error = StateError("Some state error occurred", language)
    except StateError as e:
        print(f"StateError: {str(e)}")

# Main script
if __name__ == "__main__":
    # Step 1: Test locale detection
    test_get_user_locale()

    # Step 2: Ask for language input
    language = input("Enter the language to test (en, fr, de): ").strip().lower()

    # Validate input
    if language not in ['en', 'fr', 'de']:
        print("Invalid language. Please enter 'en', 'fr', or 'de'.")
    else:
        # Step 3: Test exception classes with the selected language
        test_exception_classes(language)
