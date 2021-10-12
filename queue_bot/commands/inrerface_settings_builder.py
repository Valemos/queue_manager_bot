from abc import ABCMeta, abstractmethod


class NewQueueSettings:
    def __init__(self):
        self.name = None
        self.students = None
        self.is_random = False

    def is_valid(self):
        return self.name is not None and \
                self.students is not None


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
