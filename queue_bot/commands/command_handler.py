from typing import Type

from queue_bot.bot.access_levels import AccessLevel
from abstract_command import AbstractCommand


class CommandHandler:

    # ids and commands of type str
    # used to avoid passing long strings to limited telegram keyboard query

    def __init__(self):
        self._command_id_dict = {}  # index for each command class as key
        self._id_command_dict = {}  # command classes using their index as key
        self._name_command = {}     # using command name as key stores it's command class
        self.current_cmd_index = 0

    def add_command(self, command_class: Type[AbstractCommand]):
        self._command_id_dict[command_class] = str(self.current_cmd_index)
        self._id_command_dict[str(self.current_cmd_index)] = command_class
        self._name_command[command_class.command_name] = command_class
        self.current_cmd_index += 1

        # also for every command we must set if we need to check for private chat
        if command_class.check_chat_private is None:
            command_class.check_chat_private = command_class.access_requirement.value < AccessLevel.USER.value

    def handle_keyboard(self, update, bot):
        """
        Requires callback query to be present
        if it is not present, keyboard button was not pressed and it is a programmer error
        """
        if update.callback_query is None:
            raise ValueError('update does not have any callback query. Programmer error')

        index, argument = self.parse_command(update.callback_query.data)

        # find command
        cmd = self.get_command_class(index)

        if argument is None:
            cmd.handle_reply_access(update, bot)
        else:
            cmd.handle_keyboard(update, bot)

    def handle_text_command(self, update, message_entity, bot):
        command_string = update.message.text[message_entity.offset + 1: message_entity.length]
        cmd = self.get_command_by_name(command_string)

        if cmd is None:
            update.effective_message.reply_text(bot.language_pack.unknown_command)
        else:
            cmd.handle_reply_access(update, bot)

    def query(self, cmd, args=None):
        if args is None:
            return self._command_id_dict[cmd]
        else:
            return self._command_id_dict[cmd] + '#' + str(args)

    def get_command_by_name(self, command_string):
        if '@' in command_string:
            command_string = command_string[:command_string.index('@')]

        if command_string in self._name_command:
            return self._name_command[command_string]
        else:
            return None

    @staticmethod
    def parse_command(command_str):
        try:
            index = command_str
            argument = None
            if '#' in command_str:
                argument = command_str[command_str.index('#') + 1:]
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

    def get_command_class(self, command_index) -> Type[AbstractCommand]:
        return self._id_command_dict[command_index]
