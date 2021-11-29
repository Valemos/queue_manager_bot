from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class MoveQueuePosition(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(get_chat_queues(update.effective_chat.id).get_queue_str())
        update.effective_chat.send_message(language_pack.send_new_position)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            bot.request_del()
            return

        try:
            new_index = int(update.message.text)
            assert 0 < new_index <= len(get_chat_queues(update.effective_chat.id).get_queue())
            get_chat_queues(update.effective_chat.id).get_queue().set_position(new_index - 1)

            update.effective_chat.send_message(language_pack.position_set)
        except (ValueError, AssertionError):
            update.effective_chat.send_message(language_pack.error_in_values)
        finally:
            bot.refresh_last_queue_msg(update)
            bot.request_del()
            log_bot_queue(update, bot, 'set queue position')


class MoveStudentPosition(Command):
    access_requirement = AccessLevel.ADMIN

    student = None
    new_position = -1

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
        if cls.student is None:
            student_str = cls.get_arguments(update.callback_query.data)
            student = parsers.parse_student(student_str)
            cls.student = student
            cls.update_message_keyboard(update, bot)
            update.effective_chat.send_message(language_pack.selected_object.format(student.str()))
        elif cls.new_position == -1:
            if not bot.check_queue_selected():
                update.effective_chat.send_message(language_pack.queue_not_selected)
                return

            student_str = cls.get_arguments(update.callback_query.data)
            student = parsers.parse_student(student_str)
            cls.new_position = get_chat_queues(update.effective_chat.id).get_queue().get_student_position(student)
            if cls.new_position is not None:
                update.effective_chat.send_message(
                    language_pack.selected_position.format(str(cls.new_position+1))
                )
                cls.handle_request(update, bot)
            else:
                update.effective_chat.send_message(language_pack.selected_position_not_exists)
        else:
            cls.student = None
            cls.new_position = -1
            cls.handle_keyboard(update, bot)

    @classmethod
    def handle_request(cls, update, bot):
        log_bot_queue(update, bot, 'set student position {0}', cls.new_position)
        get_chat_queues(update.effective_chat.id).get_queue().set_student_position(cls.student, cls.new_position)
        update.effective_chat.send_message(
            language_pack.student_moved_to_position.format(cls.student.name, cls.new_position + 1)
        )

        # update keyboard for this message
        cls.update_message_keyboard(update, bot)

        bot.refresh_last_queue_msg(update)
        bot.request_del()