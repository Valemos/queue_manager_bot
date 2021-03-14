from abc import ABCMeta, abstractmethod
from typing import Callable


class NewQueueSettings:
    def __init__(self):
        self.name = None
        self.students = None
        self.generate_function: Callable = None

    def is_valid(self):
        return self.name is not None and \
                self.students is not None and \
                self.generate_function is not None


class ISettingsBuilderCommand(metaclass=ABCMeta):
    settings = NewQueueSettings()

    @classmethod
    @abstractmethod
    def handle_reply(cls, update, bot):
        pass

    @classmethod
    def handle_reply_settings(cls, update, bot, settings):
        cls.settings = settings
        cls.handle_reply(update, bot)
