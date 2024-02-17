from typing import Dict

from kombu import Message


class EventRestoreException(Exception):
    def __init__(self, body: Dict, message: Message) -> None:
        self.body = body
        self.message = message
        super().__init__(f"Event could not be restored. Body: {body}. Message: {message}")
