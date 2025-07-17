# device/time.py

from ..exceptions import CommandError, StateError
from ..const import CMD_GET_DEVICE_TIME


class TimeMixin:
    """Mixin class providing device time management functionality."""

    async def get_device_time(self):
        """
        Retrieve the current date and time from the device's real-time clock.
        
        Returns:
            dict: Dictionary containing device time information
                  Format: {"time": "YYYY-MM-DD,HH:MM:SS"}
        
        Raises:
            CommandError: If the command fails to execute
            StateError: If device response is invalid
        """
        try:
            response = await self._send_command(CMD_GET_DEVICE_TIME)
            
            # Validate response structure
            if not isinstance(response, dict) or "data" not in response:
                raise CommandError(
                    "ERROR_INVALID_JSON",
                    self.user_locale,
                    detail="Received invalid data structure from device.",
                )

            # Extract time information
            data = response["data"]
            device_time = data.get("time")

            if device_time is None:
                raise CommandError("ERROR_MISSING_EXPECTED_DATA", self.user_locale)

            # Return the structured data
            return {"time": device_time}

        except CommandError:
            raise CommandError(
                "ERROR_COMMAND_EXECUTION", self.user_locale
            )  # Use standardized error message
        except Exception as e:
            raise StateError(
                "ERROR_UNEXPECTED", self.user_locale, detail=str(e)
            )  # Handle unexpected errors