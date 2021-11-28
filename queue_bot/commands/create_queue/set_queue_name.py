import queue_bot.commands.create_queue.finish_creation
from queue_bot.bot import parsers as parsers
from queue_bot.commands.create_queue.queue_creation_state import QueueCreateDialogState
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel


class SetQueueName(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        # todo check for dialogs to resume
        state: QueueCreateDialogState

        update.effective_chat.send_message(bot.language_pack.enter_queue_name,
                                           reply_markup=bot.keyboards.set_default_queue_name)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        state: QueueCreateDialogState

        if parsers.check_queue_name(update.message.text):
            state.new_queue_name = update.message.text
            queue_bot.commands.create_queue.finish_creation.FinishCreation.handle_request(update, bot)
        else:
            update.effective_chat.send_message(bot.language_pack.name_incorrect)
            cls.handle_reply(update, bot)

        log_bot_queue(update, bot, 'queue name set {0}', update.message.text)
