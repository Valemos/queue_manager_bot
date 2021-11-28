import queue_bot.commands.create_queue.set_queue_name
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel


class SetEmptyStudents(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        CreateQueue.new_queue_students = []
        queue_bot.commands.create_queue.add_queue_name.SetQueueName.handle_reply(update, bot)