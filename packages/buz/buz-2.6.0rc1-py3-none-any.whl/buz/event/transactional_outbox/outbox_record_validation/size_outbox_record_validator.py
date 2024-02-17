from sys import getsizeof

from buz.event.transactional_outbox import OutboxRecord
from buz.event.transactional_outbox.outbox_record_validation.abstract_outbox_record_validator import (
    AbstractOutboxRecordValidator,
)
from buz.event.transactional_outbox.outbox_record_validation.outbox_record_size_not_allowed_exception import (
    OutboxRecordSizeNotAllowedException,
)


class SizeOutboxRecordValidator(AbstractOutboxRecordValidator):
    def __init__(self, size_limit_in_bytes: int = 1000000):
        self.__size_limit_in_bytes = size_limit_in_bytes
        super().__init__()

    def validate(self, record: OutboxRecord) -> None:
        size = self.__measure_stable_properties(record)
        if size >= self.__size_limit_in_bytes:
            raise OutboxRecordSizeNotAllowedException(
                record=record, size_limit_in_bytes=self.__size_limit_in_bytes, record_size=size
            )

        size += self.__measure_payload(record.event_payload)
        if size >= self.__size_limit_in_bytes:
            raise OutboxRecordSizeNotAllowedException(
                record=record, size_limit_in_bytes=self.__size_limit_in_bytes, record_size=size
            )

        return super().validate(record)

    def __measure_stable_properties(self, record: OutboxRecord) -> int:
        total = 0
        for key, value in record.get_attrs().items():
            if key != "event_payload":
                total += getsizeof(value)

        return total

    def __measure_payload(self, event_payload: dict) -> int:
        total = 0
        for k, v in event_payload.items():
            if isinstance(v, dict):
                total += self.__measure_payload(v)
            else:
                total += getsizeof(v)

        return total
