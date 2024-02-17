from abc import ABC, abstractmethod
from typing import List

from buz.event import Event, Subscriber


class RejectCallback(ABC):
    @abstractmethod
    def on_reject(self, event: Event, subscribers: List[Subscriber]) -> None:
        pass
