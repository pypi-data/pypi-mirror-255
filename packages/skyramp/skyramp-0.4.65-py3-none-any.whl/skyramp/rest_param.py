"""
Contains helpers for interacting with Skyramp rest param.
"""
class _RestParam:
    def __init__(self, name: str, in_: str, value: str, type_=None):
        self.name = name
        self.in_ = in_
        self.type_ = type_
        self.value = value

    def to_json(self):
        """
        Convert the object to a JSON string.
        """
        return {
            "name": self.name,
            "in": self.in_,
            "value": self.value,
        }
