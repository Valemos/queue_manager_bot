from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class Clear(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        log_bot_queue(update, bot, 'clear queue')
        name = get_chat_queues(update.effective_chat.id).get_queue().name if get_chat_queues(update.effective_chat.id).get_queue() is not None else None
        if name is not None:
            get_chat_queues(update.effective_chat.id).clear_current_queue()
            update.effective_chat.send_message(language_pack.queue_removed.format(name))
