"""
    Utility functions for Cosmic Frog
"""

import os
from pandas import DataFrame
from httpx import Client

# Note: Geocoding is via PROD service unless overidden
HYPNOTOAD_URL = (
    os.getenv("HYPNOTOAD_URL") or "https://api.cosmicfrog.optilogic.app/hypnotoad/cosmicfrog/v0.2"
)


class FrogUtils:
    """
    Container class for Cosmic Frog utilities
    """

    @staticmethod
    def geocode_table(
        model_name: str,
        table_name: str,
        app_key: str,
        geoprovider: str = "MapBox",
        geoapikey: str = None,
        ignore_low_confidence: bool = True,
    ):
        """
        Wrapper function for geocoding an Cosmic Frog table (in place)
        """
        table_name = table_name.lower().strip()

        if table_name not in ["customers", "facilities", "suppliers"]:
            raise ValueError("Table must be customers, facilities or suppliers")

        if not app_key:
            raise ValueError("Must supply a valid OL app key")

        headers = {"X-App-Key": app_key}

        params = {
            "model_name": model_name,
            "table_name": table_name,
            "geoprovider": geoprovider,
            "ignore_low_confidence": ignore_low_confidence,
        }

        if geoapikey:
            params["geoapikey"] = geoapikey

        with Client() as client:
            response = client.post(
                f"{HYPNOTOAD_URL}/geocoding/geocode/table", headers=headers, params=params
            )
            response.raise_for_status()

    @staticmethod
    def geocode_data(data: DataFrame):
        """
        Wrapper function to geocode arbitrary location data and return result
        """

        print(data, HYPNOTOAD_URL)
