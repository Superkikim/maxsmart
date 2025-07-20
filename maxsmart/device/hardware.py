# maxsmart/device/hardware.py

from ..exceptions import CommandError, StateError
from ..const import CMD_GET_DEVICE_IDS
from ..utils import get_mac_address_from_ip


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

    async def get_mac_address_via_arp(self):
        """
        Get MAC address from system ARP table.
        
        Returns:
            str or None: MAC address or None if not found
        """
        return get_mac_address_from_ip(self.ip)

    async def get_best_unique_identifier(self):
        """
        Get the best available unique identifier for this device.
        
        Priority order:
        1. CPU ID (via command 124) - Most reliable hardware identifier
        2. MAC Address (via ARP) - Network-based hardware identifier
        3. UDP Serial - Legacy identifier (if reliable)
        4. IP address - Fallback identifier
        
        Returns:
            dict: Best identifier with metadata
                  Format: {
                      "identifier": "cpu_XXXXXXXX",
                      "type": "cpuid",
                      "source": "hardware",
                      "reliable": True
                  }
        """
        # 1. Try CPU ID from hardware identifiers
        try:
            hw_identifiers = await self.get_device_identifiers()
            cpuid = hw_identifiers.get("cpuid", "").strip()
            
            if cpuid and len(cpuid) > 8:  # Reasonable length check
                return {
                    "identifier": f"cpu_{cpuid}",
                    "type": "cpuid",
                    "source": "hardware_cmd124",
                    "reliable": True,
                    "raw_value": cpuid
                }
        except Exception as e:
            import logging
            logging.debug(f"CPU ID retrieval failed for {self.ip}: {e}")
        
        # 2. Try MAC Address via ARP
        try:
            mac_address = await self.get_mac_address_via_arp()
            
            if mac_address:
                mac_clean = mac_address.replace(':', '').lower()
                return {
                    "identifier": f"mac_{mac_clean}",
                    "type": "mac_address",
                    "source": "network_arp",
                    "reliable": True,
                    "raw_value": mac_address
                }
        except Exception as e:
            import logging
            logging.debug(f"MAC address retrieval failed for {self.ip}: {e}")
        
        # 3. Try UDP Serial (if available and reliable)
        udp_serial = getattr(self, 'udp_serial', None)
        if udp_serial and self._is_udp_serial_reliable(udp_serial):
            return {
                "identifier": f"sn_{udp_serial}",
                "type": "udp_serial",
                "source": "udp_discovery",
                "reliable": True,
                "raw_value": udp_serial
            }
        
        # 4. Fallback to IP address
        ip_clean = self.ip.replace('.', '_')
        return {
            "identifier": f"ip_{ip_clean}",
            "type": "ip_address",
            "source": "network_fallback",
            "reliable": False,
            "raw_value": self.ip
        }

    async def get_unique_identifier(self):
        """
        Get the best available unique identifier for this device (simplified).
        
        Returns:
            str: Best available unique identifier
        """
        result = await self.get_best_unique_identifier()
        return result["identifier"]

    def _is_udp_serial_reliable(self, sn):
        """
        Check if a UDP serial number is reliable/usable.
        
        Args:
            sn: Serial number from UDP discovery
            
        Returns:
            bool: True if serial is reliable, False if corrupted/empty
        """
        return (
            sn and 
            isinstance(sn, str) and 
            sn.strip() and 
            len(sn) > 3 and  # Minimum reasonable length
            all(ord(c) < 128 for c in sn) and  # ASCII only
            sn.isprintable() and  # Printable characters
            not any(c in sn for c in ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06'])  # No control chars
        )

    async def get_all_identifiers(self):
        """
        Get all available identifiers for this device.
        
        Returns:
            dict: All available identifiers with their status
        """
        identifiers = {
            "cpuid": {"value": None, "available": False, "source": "hardware_cmd124"},
            "pclmac": {"value": None, "available": False, "source": "hardware_cmd124"},
            "pcldak": {"value": None, "available": False, "source": "hardware_cmd124"},
            "mac_arp": {"value": None, "available": False, "source": "network_arp"},
            "udp_serial": {"value": None, "available": False, "source": "udp_discovery"},
            "ip_address": {"value": self.ip, "available": True, "source": "network_fallback"}
        }
        
        # Try hardware identifiers (command 124)
        try:
            hw_ids = await self.get_device_identifiers()
            
            if hw_ids.get("cpuid"):
                identifiers["cpuid"]["value"] = hw_ids["cpuid"]
                identifiers["cpuid"]["available"] = True
                
            if hw_ids.get("pclmac"):
                identifiers["pclmac"]["value"] = hw_ids["pclmac"]
                identifiers["pclmac"]["available"] = True
                
            if hw_ids.get("pcldak"):
                identifiers["pcldak"]["value"] = hw_ids["pcldak"]
                identifiers["pcldak"]["available"] = True
                
        except Exception as e:
            identifiers["hardware_error"] = str(e)
        
        # Try MAC via ARP
        try:
            mac_arp = await self.get_mac_address_via_arp()
            if mac_arp:
                identifiers["mac_arp"]["value"] = mac_arp
                identifiers["mac_arp"]["available"] = True
        except Exception as e:
            identifiers["arp_error"] = str(e)
        
        # UDP Serial
        udp_serial = getattr(self, 'udp_serial', None)
        if udp_serial:
            identifiers["udp_serial"]["value"] = udp_serial
            identifiers["udp_serial"]["available"] = self._is_udp_serial_reliable(udp_serial)
        
        return identifiers

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