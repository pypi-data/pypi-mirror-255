"""
    Helpers for manipulating Cosmic Frog scenarios
"""

from typing import List


class FrogScenarioItem:
    """
    Helper class for manipulating Cosmic Frog Scenario Items
    """


class FrogScenarioRule:
    """
    Helper class for manipulating Cosmic Frog Scenario Rules
    """

    def __init__(self) -> None:
        self.contents: List[FrogScenarioItem] = []


class FrogScenario:
    """
    Helper class for manipulating Cosmic Frog Scenarios
    """

    def __init__(self) -> None:
        self.contents: List[FrogScenarioItem | FrogScenarioRule] = []

    def add_item(self, item: FrogScenarioItem):
        """
        Add a scenario item to this scenario
        """
        self.contents.append(item)
        pass

    def remove_item(self, item: FrogScenarioItem):
        """
        Remove a scenario item from this scenario
        """
        pass
