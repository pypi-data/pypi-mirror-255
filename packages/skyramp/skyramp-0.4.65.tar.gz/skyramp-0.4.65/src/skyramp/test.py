"""
Contains helpers for interacting with Skyramp test object.
"""
from skyramp.test_pattern import _TestPattern as TestPattern
class _Test:
    def __init__(self, name: str, test_pattern: TestPattern) -> None:
        self.name = name
        self.test_pattern = test_pattern

    def to_json(self):
        """
        Convert the object to a JSON string.
        """
        return {
            "name": self.name,
            "testPattern": TestPattern.to_json(self.test_pattern),
        }
    