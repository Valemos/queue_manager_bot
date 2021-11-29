import queue_bot.commands.create_queue.misc
from queue_bot.commands.command import Command
from queue_bot.commands.create_queue.queue_creation_state import QueueCreateDialogState
from queue_bot.commands.misc.logging import log_bot_queue, log_bot_user
from queue_bot.objects.access_level import AccessLevel
from queue_bot.objects.queue import Queue
from queue_bot import language_pack


class FinishCreation(Command):
    access_requirement = AccessLevel.ADMIN

    # this function only shows message about queue finished creation
    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(language_pack.queue_set)

    # this function handles end of dialog chain
    @classmethod
    def handle_request(cls, update, bot):
        state: QueueCreateDialogState
        if state.is_valid():
            queue = Queue(bot, state.new_queue_name)
            state.queue_generate_function(queue, state.new_queue_students)

            # handle_add_queue at the end calls FinishQueueCreation.handle_reply
            queue_bot.commands.create_queue.misc.handle_add_queue(update, bot, queue)
            bot.save_queue_to_file()
            log_bot_queue(update, bot, 'queue set')
        else:
            log_bot_user(update, bot, 'Fatal error: cannot finish queue creation')
        bot.request_del()
