from abc import abstractmethod

from queue_bot.bot.parsers import parse_command_name
from queue_bot.commands.command_mapping_meta import CommandMappingMeta
from queue_bot.commands.misc.logging import log_bot_user
from queue_bot.objects.access_level import AccessLevel


class Command(metaclass=CommandMappingMeta):
    command_name = None
    description = None
    access_requirement = AccessLevel.USER

    # this field is initialized on import if it was not set already
    check_chat_private = None

    @classmethod
    def __init__(cls):
        if cls.check_chat_private is None:
            cls.check_chat_private = cls.access_requirement.value < AccessLevel.USER.value

    @classmethod
    def __str__(cls):
        return cls.__qualname__

    @staticmethod
    def parse_command(command_str):
        try:
            index = command_str
            argument = None
            if '#' in command_str:
                argument = command_str[command_str.index('#')+1:]
                index = command_str[:command_str.index('#')]
            return index, argument
        except ValueError:
            return None, None

    @staticmethod
    def get_arguments(string):
        if '#' in string:
            parts = string.split('#')
            return parts[1]
        else:
            return None

    @classmethod
    def check_access(cls, update, bot):
        if bot.registered_manager.check_access(update, cls.access_requirement, cls.check_chat_private):
            return True
        else:
            log_bot_user(update, bot, 'tried to get access to {0} command', cls.access_requirement.name)
            if cls.check_chat_private:
                update.message.reply_text(bot.language_pack.command_for_private_chat)
            else:
                update.message.reply_text(bot.language_pack.permission_denied)
            return False

    # used as starting point and it checks for user access rights
    @classmethod
    def handle_reply_access(cls, update, bot):
        if cls.check_access(update, bot):
            cls.handle_reply(update, bot)

    @classmethod
    def handle_keyboard_access(cls, update, bot):
        if cls.check_access(update, bot):
            cls.handle_keyboard(update, bot)

    @classmethod
    def handle_request_access(cls, update, bot):
        if cls.check_access(update, bot):
            cls.handle_request(update, bot)

    # used to generate message, keyboard and handle_request properly
    @classmethod
    def handle_reply(cls, update, bot):
        cls.handle_request(update, bot)

    # used to handle intermediate states, or multiple choices by keyboard
    # this function will be called only if arguments for command exist
    @classmethod
    def handle_keyboard(cls, update, bot):
        cls.handle_request(update, bot)

    # used for main request handling
    @classmethod
    @abstractmethod
    def handle_request(cls, update, bot):
        pass
