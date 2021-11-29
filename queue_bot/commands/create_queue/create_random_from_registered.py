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
    def handle_reply(cls, update, bot):
        queue = Queue(bot)
        queue.generate_random(bot.registered_manager.get_users())  # we specify parameter in "self"

        if not get_chat_queues(update.effective_chat.id)add_queue(queue):
            update.effective_chat.send_message(language_pack.queue_limit_reached)
            bot.request_del()
            log_bot_queue(update, bot, 'queue limit reached')
        else:
            err_msg = bot.last_queue_message.update_contents(get_chat_queues(update.effective_chat.id)get_queue_str(), update.effective_chat)
            if err_msg is not None:
                log_bot_queue(update, bot, err_msg)

            update.effective_chat.send_message(language_pack.queue_set)
            log_bot_queue(update, bot, 'queue added')
            queue_bot.commands.create_queue.add_queue_name.SetQueueName.handle_reply(update, bot)