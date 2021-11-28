from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class ForGod(Command):
    command_name = 'ghelp'
    description = commands_descriptions.god_help_descr
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(
            Help.get_command_list_help(bot.available_commands.god_commands)
        )