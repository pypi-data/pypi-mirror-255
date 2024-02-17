from abc import ABC, abstractmethod
from typing import List

from buz.event import Event, Subscriber
from buz.event.kombu.retry import ConsumedEventRetry


class ConsumedEventRetryRepository(ABC):
    @abstractmethod
    def save(self, consumed_event_retry: ConsumedEventRetry) -> None:
        pass

    @abstractmethod
    def find_one_by_event_and_subscriber(self, event: Event, subscribers: List[Subscriber]) -> ConsumedEventRetry:
        pass
