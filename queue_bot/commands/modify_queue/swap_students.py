from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command, log_bot_queue
from queue_bot.objects.access_level import AccessLevel


class MoveSwapStudents(Command):
    access_requirement = AccessLevel.ADMIN

    keyboard_message = None

    first_student = None
    second_student = None

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        cls.first_student = None
        cls.second_student = None
        keyboard = bot.get_queue().get_students_keyboard_with_position(cls)
        ModifyCurrentQueue.MoveSwapStudents.keyboard_message = \
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)
        bot.request_set(cls)

    @classmethod
    def handle_keyboard(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        student_str = cls.get_arguments(update.callback_query.data)
        student = parsers.parse_student(student_str)
        if cls.first_student is None:
            cls.first_student = student
            update.effective_chat.send_message(bot.language_pack.selected_object.format(student.str()))
        elif cls.second_student is None:
            cls.second_student = student
            update.effective_chat.send_message(bot.language_pack.selected_object.format(student.str()))
            cls.handle_request(update, bot)

    @classmethod
    def handle_request(cls, update, bot):
        bot.get_queue().swap_students(cls.first_student, cls.second_student)
        update.effective_chat.send_message(
            bot.language_pack.students_swapped.format(
                cls.first_student.str(),
                cls.second_student.str()))

        if ModifyCurrentQueue.MoveSwapStudents.keyboard_message is not None:
            ModifyCurrentQueue.MoveSwapStudents.keyboard_message.delete()

        bot.refresh_last_queue_msg(update)
        bot.request_del()
        log_bot_queue(update, bot, 'swapped {0} and {1}', cls.first_student, cls.second_student)