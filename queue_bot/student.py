from dataclasses import dataclass
from typing import Optional

from queue_bot.bot_access_levels import AccessLevel


@dataclass
class Student:
    name: str
    telegram_id: Optional[int]
    access_level: AccessLevel = AccessLevel.USER

    def __eq__(self, other):
        if not isinstance(other, Student):
            print("Programmer error compairing students")
            return False

        if self.telegram_id is not None and other.telegram_id is not None:
            return self.telegram_id == other.telegram_id
        elif self.telegram_id is None and other.telegram_id is None:
            # if both are None
            return self.name == other.name
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.str_name_id()

    def __hash__(self):
        return hash(self.name) + (0 if self.telegram_id is None else self.telegram_id) * (2 << 64)

    def str(self, position=None):
        if position is None:
            return self.name
        else:
            return f'{position} - {self.name}'

    # to get student back used function in queue_bot.bot_parsers.parse_student
    def str_name_id(self):
        if self.telegram_id is None:
            return str(None) + self.name
        else:
            return '{:0>8}'.format(hex(self.telegram_id)[2:]) + self.name


EmptyStudent = Student('Пусто', None)
