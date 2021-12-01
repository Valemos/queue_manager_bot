from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue, log_bot_user
from queue_bot.objects.queues_manager import get_chat_queues


class Refresh(Command):
    @classmethod
    def handle_request(cls, update, bot):
        if not bot.last_queue_message.message_exists(update.effective_chat):
            update.effective_message.delete()
        err_msg = bot.last_queue_message.update_contents(get_chat_queues(update.effective_chat.id).get_queue_message(), update.effective_chat)
        if err_msg is not None:
            log_bot_queue(update, bot, err_msg)

        log_bot_user(update, bot, 'refreshed queue')