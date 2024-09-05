    async def get_statistics(self, type, port=None):
        """
        Retrieve statistics data from the device based on the specified type.

        :param type: The type of data to retrieve (0 for hourly, 1 for daily, 2 for monthly).
        :param port: The port number (1-6) to retrieve data for, or 0 to sum all ports.
        :return: Wattage data for the specified port or the sum of wattage for all ports if port is 0.
        """
        # Validate the parameters
        if type not in {0, 1, 2}:
            raise CommandError("ERROR_INVALID_PARAMETERS", self.user_locale,
                            detail="Invalid type. Must be 0 (hourly), 1 (daily), or 2 (monthly).")

        print(f"Checking statistics for type: {type}, port: {port}")
        try:
            response = await self._send_get_command(CMD_GET_STATISTICS, {"type": type})
        except Exception as e:
            print(f"Error during command execution: {e}")  # Debugging line

        # Validate the response structure
        if not isinstance(response, dict) or 'data' not in response or 'watt' not in response['data']:
            raise CommandError("ERROR_MISSING_EXPECTED_DATA", self.user_locale)

        # Extract watt data
        watt_data = response['data']['watt']

        if port is not None:
            # If a specific port is requested, return its wattage data
            return watt_data[port - 1]  # Return wattage for the specified port

        # If port is 0, sum the watt data across all ports and return the results
        summed_watt_data = [str(sum(float(w) for w in port_values)) for port_values in zip(*watt_data)]
        
        return {
            "currency": CURRENCY_SYMBOLS[3],  # Assuming CHF
            "cost": response['data']['cost'],  # Include cost from the response
            "type": get_user_message(STATISTICS_TIME_FRAME, type, self.user_locale),  # Localized human-readable type
            "year": response['data'].get('date', '').split('-')[0],  # Extract year
            "month": response['data'].get('date', '').split('-')[1],  # Extract month
            "day": None,  # Keeping it as None if not relevant
            "hour": None,  # Keeping it as None if not relevant
            "port_sums": summed_watt_data  # Return summed watt data for all ports
        }
