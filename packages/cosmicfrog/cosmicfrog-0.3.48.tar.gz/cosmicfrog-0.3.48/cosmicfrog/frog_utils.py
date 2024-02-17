"""
    Utility functions for Cosmic Frog
"""

from pandas import DataFrame


class FrogUtils:
    """
    Container class for Cosmic Frog utilities
    """

    def geocode_data(self, data: DataFrame):
        """
        Geocode arbitrary data and return result
        """

        HYPNO_URL = ""  # Pending new Api in Production
        print(data, HYPNO_URL)
