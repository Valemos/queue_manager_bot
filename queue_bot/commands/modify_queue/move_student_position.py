from dataclasses import dataclass

from sqlalchemy import Column, String

from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.a_dialog_state import ADialogState
from queue_bot.database import Base
from queue_bot.objects import AccessLevel
from queue_bot.objects.queues_manager import get_chat_queues
from queue_bot import language_pack


@dataclass
class MoveStudentState(ADialogState, Base):
    selected_student_name = Column(String)


class MoveStudentPosition(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def update_message_keyboard(cls, update, bot):
        try:
            keyboard = get_chat_queues(update.effective_chat.id).get_queue().get_keyboard_with_position(cls)
            update.effective_message.edit_text(language_pack.select_students, reply_markup=keyboard)
        except Exception:
            log_bot_queue(update, bot, "cannot update list selection message")

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        cls.student = None
        cls.new_position = -1
        keyboard = get_chat_queues(update.effective_chat.id).get_queue().get_keyboard_with_position(cls)
        update.effective_chat.send_message(language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        state = MoveStudentState.get_or_create_state(update)
        if state is None:
            return

        student_str = cls.get_arguments(update.callback_query.data)
        selected_info = parsers.parse_student(student_str)

        if state.student is None:
            state.student = selected_info
            cls.update_message_keyboard(update, bot)
            update.effective_chat.send_message(language_pack.selected_object.format(selected_info.name))
        else:
            queue = get_chat_queues(update.effective_chat.id).get_queue()
            new_position = queue.get_student_position(selected_info.name)
            if new_position is not None:
                queue = get_chat_queues(update.effective_chat.id).get_queue()
                queue.set_student_position(state.selected_student_name, new_position)

                sent_message = language_pack.student_moved_to_position.format(
                    state.selected_student_name,
                    new_position + 1)
                update.effective_chat.send_message(sent_message)
                cls.update_message_keyboard(update, bot)
                bot.refresh_last_queue_msg(update)
                bot.request_del()
