import queue_bot.commands
from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.objects.access_level import AccessLevel
from queue_bot.objects.queue import Queue
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class CreateRandomFromRegistered(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        new_queue = Queue(bot)
        new_queue.generate_random(bot.registered_manager.get_users())  # we specify parameter in "self"
        queues = get_chat_queues(update.effective_chat.id)

        if not queues.can_add_queue():
            update.effective_chat.send_message(language_pack.queue_limit_reached)
            bot.request_del()
            log_bot_queue(update, bot, 'queue limit reached')
        else:
            queues.add_queue(new_queue)
            bot.last_queue_message.update_contents(queues.get_queue_message(), update.effective_chat)
            update.effective_chat.send_message(language_pack.queue_set)
            log_bot_queue(update, bot, 'queue added')
            queue_bot.commands.create_queue.SetQueueName.handle_reply(update, bot)
