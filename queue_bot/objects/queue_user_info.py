from dataclasses import dataclass, field
from typing import Optional

from queue_bot.objects import AccessLevel


@dataclass
class QueueUserInfo:
    name: str
    telegram_id: Optional[int]
    access_level: AccessLevel = AccessLevel.USER

    @classmethod
    def from_student(cls, student):
        return cls(student.name, student.telegram_id, student.access_level)
