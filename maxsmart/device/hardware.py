# maxsmart/device/hardware.py

from ..exceptions import CommandError, StateError
from ..const import CMD_GET_DEVICE_IDS


class HardwareMixin:
    """Mixin class providing hardware identification functionality."""

    async def get_device_identifiers(self):
        """
        Retrieve hardware identifiers from the device.
        
        Returns:
            dict: Dictionary containing hardware identifiers
                  Format: {
                      "pclmac": "XX:XX:XX:XX:XX:XX",     # PowerLAN MAC address
                      "pcldak": "XXXXXXXXXXXXXXXX",      # Device Access Key
                      "cpuid": "XXXXXXXXXXXXXXXX",       # CPU unique identifier
                      "cloud_server": "server.domain"    # Cloud server address
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
            
            # Expected fields from command 124
            identifiers = {
                "pclmac": data.get("pclmac", ""),
                "pcldak": data.get("pcldak", ""),
                "cpuid": data.get("cpuid", ""), 
                "cloud_server": data.get("cloud", "")
            }
            
            # Validate that we got at least some identifiers
            if not any(identifiers.values()):
                raise CommandError(
                    "ERROR_MISSING_EXPECTED_DATA", 
                    self.user_locale,
                    ip=self.ip,
                    detail="No hardware identifiers returned by device"
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

    async def get_unique_identifier(self):
        """
        Get the best available unique identifier for this device.
        
        Priority order:
        1. CPUid (most unique)
        2. PCLMAC (MAC address)
        3. PCLDAK (Device Access Key)
        4. IP address (fallback)
        
        Returns:
            str: Best available unique identifier
        """
        try:
            identifiers = await self.get_device_identifiers()
            
            # Priority order for unique identification
            if identifiers.get("cpuid") and identifiers["cpuid"].strip():
                return f"cpu_{identifiers['cpuid']}"
            elif identifiers.get("pclmac") and identifiers["pclmac"].strip():
                return f"mac_{identifiers['pclmac'].replace(':', '').lower()}"
            elif identifiers.get("pcldak") and identifiers["pcldak"].strip():
                return f"dak_{identifiers['pcldak']}"
            else:
                # Fallback to IP if no hardware IDs available
                return f"ip_{self.ip.replace('.', '_')}"
                
        except Exception as e:
            # If command 124 fails entirely, fallback to IP
            return f"ip_{self.ip.replace('.', '_')}"

    def format_identifiers_for_display(self, identifiers):
        """
        Format hardware identifiers for human-readable display.
        
        Args:
            identifiers (dict): Raw identifiers from get_device_identifiers()
            
        Returns:
            dict: Formatted identifiers for display
        """
        formatted = {}
        
        # Format MAC address
        mac = identifiers.get("pclmac", "")
        if mac:
            formatted["MAC Address"] = mac.upper()
        else:
            formatted["MAC Address"] = "Not available"
            
        # Format DAK
        dak = identifiers.get("pcldak", "")
        if dak:
            formatted["Device Access Key"] = dak
        else:
            formatted["Device Access Key"] = "Not available"
            
        # Format CPU ID
        cpu = identifiers.get("cpuid", "")
        if cpu:
            formatted["CPU ID"] = cpu
        else:
            formatted["CPU ID"] = "Not available"
            
        # Format cloud server
        cloud = identifiers.get("cloud_server", "")
        if cloud:
            formatted["Cloud Server"] = cloud
        else:
            formatted["Cloud Server"] = "Not configured"
            
        return formatted