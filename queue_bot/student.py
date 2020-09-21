from queue_bot.bot_access_levels import AccessLevel


class Student:

    def __init__(self, name, telegram_id):
        self.name = name
        self.telegram_id = telegram_id
        self.access_level = AccessLevel.USER

    def __eq__(self, other):
        return self.telegram_id == other.telegram_id

    def __ne__(self, other):
        return self.telegram_id != other.telegram_id

    def __str__(self):
        return self.str()

    def __hash__(self):
        return self.telegram_id

    def str(self, position=None):
        if position is None:
            return self.name
        else:
            return '{0} - {1}'.format(position, self.name)

    def log_str(self):
        return '{0} - {1}'.format(self.name, str(self.telegram_id))
