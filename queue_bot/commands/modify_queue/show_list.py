from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack


class ShowList(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        if bot.check_queue_selected():
            update.effective_chat.send_message(get_chat_queues(update.effective_chat.id).get_queue().str_simple())
            log_bot_queue(update, bot, 'showed list')
        else:
            update.effective_chat.send_message(language_pack.queue_not_selected)
            log_bot_queue(update, bot, 'queue not exists')
