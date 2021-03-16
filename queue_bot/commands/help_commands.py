from queue_bot.bot.access_levels import AccessLevel
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from .abstract_command import AbstractCommand


def get_command_list_help(cmd_list):
    """
    Collects data about command_handling in list and creates help message
    :param cmd_list: list of CommandGroup.CommandGroup objects
    :return: str help message
    """

    # get max cmd length
    max_len = max((len(cmd.command_name) for cmd in cmd_list if cmd is not None)) + 3

    final_message = []
    for command in cmd_list:
        if command is not None:
            final_message.append(f"/{command.command_name:<{max_len}} - {command.description}")
        else:
            final_message.append('')

    return '\n'.join(final_message)


class TelegramPreviewCommands(AbstractCommand):
    command_name = 'cmd_preview'
    description = commands_descriptions.help_descr
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(get_command_list_help(bot.available_commands.user_commands))


class ForAdmin(AbstractCommand):
    command_name = 'help_admin'
    description = commands_descriptions.admin_help_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(
            get_command_list_help(bot.available_commands.admin_commands)
        )


class ForGod(AbstractCommand):
    command_name = 'ghelp'
    description = commands_descriptions.god_help_descr
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(
            get_command_list_help(bot.available_commands.god_commands)
        )
