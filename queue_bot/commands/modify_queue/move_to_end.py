from queue_bot.bot import parsers as parsers
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack


class MoveStudentToEnd(Command):
    access_requirement = AccessLevel.ADMIN

    move_student = None

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        cls.move_student = None
        keyboard = get_chat_queues(update.effective_chat.id).get_queue().get_students_keyboard(cls)
        update.effective_chat.send_message(language_pack.select_student, reply_markup=keyboard)
        update.effective_chat.send_message(language_pack.select_student)
        bot.request_set(cls)

    @classmethod
    def handle_keyboard(cls, update, bot):
        argument = cls.get_arguments(update.callback_query.data)
        cls.move_student = parsers.parse_student(argument)
        cls.handle_request(update, bot)

    @classmethod
    def handle_request(cls, update, bot):
        if cls.move_student is None:
            return

        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        get_chat_queues(update.effective_chat.id).get_queue().move_to_end(cls.move_student)
        bot.refresh_last_queue_msg(update)
        update.effective_chat.send_message(language_pack.student_added_to_end.format(cls.move_student.str()))
        bot.request_del()
        log_bot_queue(update, bot, 'moved {0} to end', str(cls.move_student))