# maxsmart/device/hardware.py

from ..exceptions import CommandError, StateError
from ..const import CMD_GET_DEVICE_IDS
from ..utils import get_mac_address_from_ip


class HardwareMixin:
    """Mixin class providing hardware identification functionality."""

    async def get_device_identifiers(self):
        """
        Retrieve essential hardware identifiers from the device.
        
        Returns:
            dict: Dictionary containing essential identifiers
                  Format: {
                      "cpuid": "XXXXXXXXXXXXXXXX",       # CPU unique identifier
                      "server": "server.domain"          # Cloud server address
                  }
        
        Raises:
            CommandError: If the command fails to execute
            StateError: If device response is invalid
        """
        try:
            response = await self._send_command(CMD_GET_DEVICE_IDS)
            
            # Validate response structure
            if not isinstance(response, dict) or "data" not in response:
                raise CommandError(
                    "ERROR_INVALID_JSON",
                    self.user_locale,
                    ip=self.ip,
                    detail="Received invalid data structure from device for command 124.",
                )

            # Extract hardware identifiers
            data = response["data"]
            
            # Only get essential fields from command 124
            identifiers = {
                "cpuid": data.get("cpuid", ""), 
                "server": data.get("server", "")
            }
            
            # Validate that we got at least CPU ID
            if not identifiers["cpuid"]:
                raise CommandError(
                    "ERROR_MISSING_EXPECTED_DATA", 
                    self.user_locale,
                    ip=self.ip,
                    detail="No CPU ID returned by device"
                )

            return identifiers

        except CommandError:
            raise  # Re-raise command errors as-is
        except Exception as e:
            raise StateError(
                "ERROR_UNEXPECTED", 
                self.user_locale, 
                ip=self.ip,
                detail=f"Unexpected error getting hardware identifiers: {str(e)}"
            )

    async def get_mac_address_via_arp(self):
        """
        Get MAC address from system ARP table.
        
        Returns:
            str or None: MAC address or None if not found
        """
        return get_mac_address_from_ip(self.ip)