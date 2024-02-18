"""
Contains helpers for interacting with Skyramp service.
"""

class _Service:
    def __init__(
            self,
            name,
            addr,
            alias,
            secure,
            protocol,
            credentails
            ) -> None:
        self.name = name
        self.addr = addr
        self.alias = alias
        self.secure = secure
        self.protocol = protocol
        self.credential = credentails

    def to_json(self):
        """
        Convert the object to a dictionary
        """
        return {
            "name": self.name,
            "addr": self.addr,
            "alias": self.alias,
            "secure": self.secure,
            "protocol": self.protocol,
            "credential": self.credential, 
        }
