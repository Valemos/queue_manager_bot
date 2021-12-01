from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class MoveQueuePosition(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(get_chat_queues(update.effective_chat.id).get_queue_message())
        update.effective_chat.send_message(language_pack.send_new_position)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            bot.request_del()
            return

        try:
            new_index = int(update.message.text)
            assert 0 < new_index <= len(get_chat_queues(update.effective_chat.id).get_queue())
            get_chat_queues(update.effective_chat.id).get_queue().set_position(new_index - 1)

            update.effective_chat.send_message(language_pack.position_set)
        except (ValueError, AssertionError):
            update.effective_chat.send_message(language_pack.error_in_values)
        finally:
            bot.refresh_last_queue_msg(update)
            bot.request_del()
            log_bot_queue(update, bot, 'set queue position')


