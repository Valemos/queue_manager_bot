import queue_bot.commands
from queue_bot.commands.command import Command, log_bot_user
from queue_bot import language_pack


class MovePrevious(Command):
    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        get_chat_queues(update.effective_chat.id).get_queue().move_prev()
        queue_bot.commands.update_queue.show_status.ShowStatus.handle_request(update, bot)
        log_bot_user(update, bot, 'moved previous')
        queue_bot.commands.update_queue.refresh.Refresh.handle_request(update, bot)
