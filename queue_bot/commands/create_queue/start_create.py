from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel
from queue_bot.objects.students_queue import StudentsQueue


class StartCreate(Command):
    command_name = 'new_queue'
    description = commands_descriptions.new_queue_descr
    access_requirement = AccessLevel.ADMIN

    # this function handles single command without arguments and runs chain of prompts
    @classmethod
    def handle_reply(cls, update, bot):
        CreateQueue.handle_queue_create_message(cls, update, bot, StudentsQueue.generate_simple)

    # this function handles single command queue initialization
    @classmethod
    def handle_request(cls, update, bot):
        CreateQueue.handle_queue_create_single_command(update, bot, StudentsQueue.generate_simple)