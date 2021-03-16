import logging

from queue_bot.bot.access_levels import AccessLevel
from queue_bot.commands.logging_shortcuts import log_user


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class AbstractCommand:
    """
    To add new command, class must be a child class of AbstractCommand,
    must be added in corresponding command group in __init__.py
    If new command group is needed, it must be in separate file
    and listed in _command_modules list to properly initialize
    """

    command_name = None
    description = None
    access_requirement = AccessLevel.USER

    # this field is initialized on import if it was not set already
    check_chat_private = None

    @classmethod
    def __str__(cls):
        return cls.__qualname__

    @classmethod
    def check_access(cls, update, bot):
        if bot.registered.check_access(update, cls.access_requirement, cls.check_chat_private):
            return True
        else:
            log.info(log_user(update, bot, f'tried to get access to {cls.access_requirement.name} command'))
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
    def handle_request(cls, update, bot):
        print('{0} called default request method. Command is empty', cls.__qualname__)
