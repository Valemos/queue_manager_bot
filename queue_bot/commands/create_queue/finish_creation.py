from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue, log_bot_user
from queue_bot.objects.access_level import AccessLevel
from queue_bot.objects.students_queue import StudentsQueue


class FinishCreation(Command):
    access_requirement = AccessLevel.ADMIN

    # this function only shows message about queue finished creation
    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.queue_set)

    # this function handles end of dialog chain
    @classmethod
    def handle_request(cls, update, bot):
        # todo use queues dialog state
        if CreateQueue.new_queue_name is not None and \
           CreateQueue.new_queue_students is not None and \
           CreateQueue.queue_generate_function is not None:
            queue = StudentsQueue(bot, CreateQueue.new_queue_name)
            CreateQueue.queue_generate_function(queue, CreateQueue.new_queue_students)

            # handle_add_queue at the end calls FinishQueueCreation.handle_reply
            CreateQueue.handle_add_queue(update, bot, queue)
            bot.save_queue_to_file()
            log_bot_queue(update, bot, 'queue set')
        else:
            log_bot_user(update, bot, 'Fatal error: cannot finish queue creation')
        bot.request_del()
