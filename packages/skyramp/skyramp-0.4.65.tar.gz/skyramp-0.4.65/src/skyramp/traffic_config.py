"""
Contains helpers for interacting with Skyramp loss percentage traffic config.
"""
class _DelayConfig:
    def __init__(self, min_delay: int, max_delay) -> None:
        self.min_delay = min_delay
        self.max_delay = max_delay

    def to_json(self):
        """
        Convert the object to a JSON string.
        """
        return {
            "minDelay": self.min_delay,
            "maxDelay": self.max_delay,
        }

class _TrafficConfig:
    def __init__(
            self,
            loss_percentage: int,
            delay_config: _DelayConfig) -> None:
        self.loss_percentage = loss_percentage
        self.delay_config = delay_config

    def to_json(self):
        """
        Convert the object to a JSON string.
        """
        return {
            "lossPercentage": self.loss_percentage,
            "delayConfig": self.delay_config.to_json(),
        }
    