from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel
from queue_bot.objects.students_queue import StudentsQueue


class StartCreateRandom(Command):
    command_name = 'new_random_queue'
    description = commands_descriptions.new_random_queue_descr
    access_requirement = AccessLevel.ADMIN

    # the same as CreateSimple
    @classmethod
    def handle_reply(cls, update, bot):
        CreateQueue.handle_queue_create_message(cls, update, bot, StudentsQueue.generate_random)

    @classmethod
    def handle_request(cls, update, bot):
        CreateQueue.handle_queue_create_single_command(update, bot, StudentsQueue.generate_random)