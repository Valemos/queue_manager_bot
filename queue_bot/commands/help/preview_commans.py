from queue_bot.commands.command import Command
from queue_bot.commands.help.shared import get_command_list_help
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class PreviewCommands(Command):
    command_name = 'cmd_preview'
    description = commands_descriptions.help_descr
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(get_command_list_help(bot.available_commands.user_commands))
