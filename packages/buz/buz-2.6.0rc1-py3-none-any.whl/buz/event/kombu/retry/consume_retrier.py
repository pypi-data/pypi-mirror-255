from abc import ABC, abstractmethod
from typing import List

from buz.event import Event, Subscriber


class ConsumeRetrier(ABC):
    @abstractmethod
    def should_retry(self, event: Event, subscribers: List[Subscriber]) -> bool:
        pass

    @abstractmethod
    def register_retry(self, event: Event, subscribers: List[Subscriber]) -> None:
        pass
