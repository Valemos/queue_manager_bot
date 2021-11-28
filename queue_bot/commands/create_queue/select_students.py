import queue_bot.commands.create_queue.set_queue_name
from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command
from queue_bot.commands.create_queue.queue_creation_state import QueueCreateDialogState
from queue_bot.objects.access_level import AccessLevel


class SelectStudents(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.enter_students_list,
                                           reply_markup=bot.keyboards.set_empty_queue)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        state: QueueCreateDialogState

        names = parsers.parse_names(update.message.text)
        state.new_queue_students = bot.registered_manager.get_registered_students(names)
        queue_bot.commands.create_queue.SetQueueName.handle_reply(update, bot)
