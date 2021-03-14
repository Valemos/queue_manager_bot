from queue_bot.bot.access_levels import AccessLevel
from queue_bot.commands import get_command_list_help
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from abstract_command import AbstractCommand


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
