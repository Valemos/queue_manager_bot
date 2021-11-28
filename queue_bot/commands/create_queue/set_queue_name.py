import queue_bot.commands.create_queue.finish_creation
from queue_bot.bot import parsers as parsers
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel


class SetQueueName(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        # todo use queue state
        if CreateQueue.new_queue_students is not None:
            update.effective_chat.send_message(bot.language_pack.enter_queue_name,
                                               reply_markup=bot.keyboards.set_default_queue_name)
            bot.request_set(cls)
        else:
            bot.request_del()
            log_bot_queue(update, bot, 'in AddNameToQueue queue is None. Error')

    @classmethod
    def handle_request(cls, update, bot):
        # todo use queue state
        if parsers.check_queue_name(update.message.text):
            CreateQueue.new_queue_name = update.message.text
            queue_bot.commands.create_queue.finish_creation.FinishCreation.handle_request(update, bot)
        else:
            update.effective_chat.send_message(bot.language_pack.name_incorrect)
            CreateQueue.SetQueueName.handle_reply(update, bot)

        log_bot_queue(update, bot, 'queue name set {0}', update.message.text)