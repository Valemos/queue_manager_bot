from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.objects.access_level import AccessLevel


class SwapStudentsState:

    def __init__(self, chat_id: int, first_student=None, second_student=None):
        self.chat_id = chat_id
        self.first_student = first_student
        self.second_student = second_student

    def add_student(self, student):
        if self.first_student is None:
            self.first_student = student
        elif self.second_student is None:
            self.second_student = student

    def is_ready(self):
        return self.first_student is not None and \
               self.second_student is not None


class MoveSwapStudents(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return
        # todo check for previous dialogs
        dialog_state = SwapStudentsState(update.effective_chat.id)
        keyboard = bot.get_queue().get_students_keyboard_with_position(cls)
        update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)
        bot.request_set(cls)

    @classmethod
    def handle_keyboard(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        student_str = cls.get_arguments(update.callback_query.data)
        student = parsers.parse_student(student_str)

        # todo add persistence for dialog_state
        dialog_state.add_student(student)

        if dialog_state.is_ready():
            cls.handle_request(update, bot)
        else:
            update.effective_chat.send_message(bot.language_pack.selected_object.format(student.str()))

    @classmethod
    def handle_request(cls, update, bot):
        dialog_state
        bot.get_queue().swap_students(dialog_state.first_student, dialog_state.second_student)
        update.effective_chat.send_message(
            bot.language_pack.students_swapped.format(
                dialog_state.first_student.str(),
                dialog_state.second_student.str()))

        bot.refresh_last_queue_msg(update)
        bot.request_del()
        log_bot_queue(update, bot, 'swapped {0} and {1}', dialog_state.first_student, dialog_state.second_student)
