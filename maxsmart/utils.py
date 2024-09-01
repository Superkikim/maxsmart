import locale

def get_user_locale():
    """
    Get the user's locale.
    
    Returns:
        str: The locale in the format 'language_country' (e.g., 'en_US').
              Defaults to 'en' if locale cannot be determined.
    """
    user_locale = locale.getdefaultlocale()[0]  # E.g., 'en_US'
    return user_locale if user_locale is not None else 'en'  # Fallback to 'en'

def get_localized_message(message_dict, error_key, user_locale, default_message="Unknown error."):
    """
    Retrieve a localized message from the provided dictionary.

    Parameters:
        message_dict (dict): A dictionary of localized messages.
        error_key (str): The key for the specific message.
        user_locale (str): The user's locale.
        default_message (str): The fallback message if key is not found.

    Returns:
        str: The localized message.
    """
    lang = user_locale.split('_')[0]  # Extract language code
    return message_dict.get(lang, message_dict["en"]).get(error_key, default_message)

import logging

def log_localized_message(message_dict, log_key, user_locale, *args, **kwargs):
    """
    Log a localized message based on the provided dictionary.

    Parameters:
        message_dict (dict): A dictionary holding localized logging messages.
        log_key (str): The key for the specific log message.
        user_locale (str): The user's locale.
    """
    lang = user_locale.split('_')[0]  # Extract language code
    log_message = message_dict.get(lang, message_dict["en"]).get(log_key, "Unknown log message.")
    formatted_message = log_message.format(*args, **kwargs)  # Format the message if needed
    logging.error(formatted_message)  # Log the formatted message
