import queue_bot.commands.create_queue.finish_creation
from queue_bot.commands.command import Command, log_bot_user
from queue_bot.objects.access_level import AccessLevel


class DefaultQueueName(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        CreateQueue.new_queue_name = bot.language_pack.default_queue_name
        log_bot_user(update, bot, 'queue set default name')
        queue_bot.commands.create_queue.finish_creation.FinishCreation.handle_request(update, bot)