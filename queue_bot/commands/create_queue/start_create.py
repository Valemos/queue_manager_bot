from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class StartCreate(Command):
    command_name = 'new_queue'
    description = commands_descriptions.new_queue_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        # todo refactor this
        pass
