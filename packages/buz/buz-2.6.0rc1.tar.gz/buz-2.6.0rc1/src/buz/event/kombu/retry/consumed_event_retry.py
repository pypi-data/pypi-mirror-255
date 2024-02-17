from dataclasses import dataclass
from typing import List


@dataclass
class ConsumedEventRetry:
    event_id: str
    subscribers_fqns: List[str]
    retries: int

    def register_retry(self) -> None:
        self.retries += 1
