from queue_bot.bot import parsers as parsers, keyboards
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class MoveStudentToEnd(Command):
    access_requirement = AccessLevel.ADMIN

    move_student = None

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        cls.move_student = None
        queue = get_chat_queues(update.effective_chat.id).get_queue()
        keyboard = keyboards.generate_keyboard(cls, queue.get_member_names())
        update.effective_chat.send_message(language_pack.select_student, reply_markup=keyboard)
        bot.request_set(cls)

    @classmethod
    def handle_keyboard(cls, update, bot):
        argument = cls.get_arguments(update.callback_query.data)
        cls.move_student = parsers.parse_student(argument)

        if cls.move_student is None:
            return

        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        get_chat_queues(update.effective_chat.id).get_queue().move_to_end(cls.move_student)
        bot.refresh_last_queue_msg(update)
        update.effective_chat.send_message(language_pack.student_added_to_end.format(cls.move_student.description()))
