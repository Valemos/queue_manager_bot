from queue_bot.commands.command import Command, log_bot_queue
from queue_bot.objects.access_level import AccessLevel


class Clear(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        log_bot_queue(update, bot, 'clear queue')
        name = bot.get_queue().name if bot.get_queue() is not None else None
        if name is not None:
            bot.queues_manager.clear_current_queue()
            update.effective_chat.send_message(bot.language_pack.queue_removed.format(name))