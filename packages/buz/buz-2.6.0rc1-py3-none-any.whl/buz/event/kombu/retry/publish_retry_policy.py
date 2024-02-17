from abc import abstractmethod, ABC
from typing import Dict

from buz.event import Event


class PublishRetryPolicy(ABC):
    @abstractmethod
    def max_retries(self, event: Event) -> int:
        pass

    @abstractmethod
    def interval_start(self, event: Event) -> float:
        pass

    @abstractmethod
    def interval_step(self, event: Event) -> float:
        pass

    @abstractmethod
    def interval_max(self, event: Event) -> float:
        pass

    @abstractmethod
    def error_callback(self, event: Event, exc: Exception, interval_range: range) -> None:
        pass

    def to_kombu_retry_policy(self, event: Event) -> Dict:
        return {
            "max_retries": self.max_retries(event),
            "interval_start": self.interval_start(event),
            "interval_step": self.interval_step(event),
            "interval_max": self.interval_max(event),
            "errback": lambda exc, interval_range: self.error_callback(event, exc, interval_range),
        }
