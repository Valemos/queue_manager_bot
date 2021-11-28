from queue_bot.commands.command import Command
from queue_bot.commands.help.shared import get_command_list_help
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class ForAdmin(Command):
    command_name = 'help_admin'
    description = commands_descriptions.admin_help_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        update.effective_chat.send_message(get_command_list_help(bot.available_commands.admin_commands))
