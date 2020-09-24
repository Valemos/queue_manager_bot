from queue_bot.bot_access_levels import AccessLevel
from hashlib import md5


class Student:

    def __init__(self, name, telegram_id):
        self.name = name
        self.telegram_id = telegram_id
        self.access_level = AccessLevel.USER

    def __eq__(self, other):
        if self.telegram_id is not None and other.telegram_id is not None:
            return self.telegram_id == other.telegram_id
        elif self.telegram_id is None and other.telegram_id is None:
            # if both are None
            return self.name == other.name
        else:
            return False

    def __ne__(self, other):
        return self.telegram_id != other.telegram_id

    def __str__(self):
        return self.str()

    def __hash__(self):
        return hash(self.name) + (0 if self.telegram_id is None else self.telegram_id) * (2 << 64)

    def str(self, position=None):
        if position is None:
            return self.name
        else:
            return '{0} - {1}'.format(position, self.name)

    def log_str(self):
        return '{0} - {1}'.format(self.name, str(self.telegram_id))
