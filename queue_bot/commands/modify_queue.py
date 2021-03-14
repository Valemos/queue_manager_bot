from queue_bot.bot import parsers as parsers
from queue_bot.bot.access_levels import AccessLevel
from abstract_command import AbstractCommand
from queue_bot.languages import command_descriptions_rus as commands_descriptions

from command_handler import CommandHandler
from logging_shortcuts import log_bot_queue
from update_queue import ShowCurrentAndNextStudent


class ShowMenu(AbstractCommand):
    command_name = 'edit_queue'
    description = commands_descriptions.edit_queue_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.message.reply_text(bot.language_pack.title_edit_queue,
                                  reply_markup=bot.keyboards.modify_queue)


class ShowList(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        if bot.check_queue_selected():
            update.effective_chat.send_message(bot.get_queue().str_simple())
            log_bot_queue(update, bot, 'showed list')
        else:
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            log_bot_queue(update, bot, 'queue not exists')


class ShowQueueForCopy(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        if bot.check_queue_selected():
            update.effective_chat.send_message(bot.get_queue().get_str_for_copy())
            update.effective_chat.send_message(bot.language_pack.copy_queue)
            log_bot_queue(update, bot, 'showed list for copy')
        else:
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)


class MoveQueuePosition(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.queues_manager.get_queue_str())
        update.effective_chat.send_message(bot.language_pack.send_new_position)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            bot.request_del()
            return

        try:
            new_index = int(update.message.text)
            assert 0 < new_index <= len(bot.get_queue())
            bot.get_queue().set_position(new_index - 1)

            update.effective_chat.send_message(bot.language_pack.position_set)
        except (ValueError, AssertionError):
            update.effective_chat.send_message(bot.language_pack.error_in_values)
        finally:
            bot.refresh_last_queue_msg(update)
            bot.request_del()
            log_bot_queue(update, bot, 'set queue position')


class ClearList(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        log_bot_queue(update, bot, 'clear queue')
        name = bot.get_queue().name if bot.get_queue() is not None else None
        if name is not None:
            bot.queues_manager.clear_current_queue()
            update.effective_chat.send_message(bot.language_pack.queue_removed.format(name))


class RemoveListStudents(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        keyboard = bot.get_queue().get_students_keyboard(cls)
        update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        cls.handle_request(update, bot)

        # after student deleted, message updates
        keyboard = bot.get_queue().get_students_keyboard(cls)
        # keyboards not equal
        if len(keyboard.inline_keyboard) != len(update.effective_message.reply_markup.inline_keyboard):
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_request(cls, update, bot):
        student_str = CommandHandler.get_arguments(update.callback_query.data)
        student = parsers.parse_student(student_str)
        bot.get_queue().remove_student(student)
        bot.refresh_last_queue_msg(update)

        bot.request_del()
        log_bot_queue(update, bot, 'removed student {0}', student)


class MoveStudentToEnd(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    move_student = None

    @classmethod
    def handle_reply(cls, update, bot):
        # todo refactor this handle reply
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        cls.move_student = None
        keyboard = bot.get_queue().get_students_keyboard(cls)
        update.effective_chat.send_message(bot.language_pack.select_student, reply_markup=keyboard)
        update.effective_chat.send_message(bot.language_pack.select_student)
        bot.request_set(cls)

    @classmethod
    def handle_keyboard(cls, update, bot):
        argument = CommandHandler.get_arguments(update.callback_query.data)
        cls.move_student = parsers.parse_student(argument)
        cls.handle_request(update, bot)

    @classmethod
    def handle_request(cls, update, bot):
        if cls.move_student is None:
            return

        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        bot.get_queue().move_to_end(cls.move_student)
        bot.refresh_last_queue_msg(update)
        update.effective_chat.send_message(bot.language_pack.student_added_to_end.format(cls.move_student.str()))
        bot.request_del()
        log_bot_queue(update, bot, 'moved {0} to end', str(cls.move_student))


class MoveStudentPosition(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    student = None
    new_position = -1

    @classmethod
    def update_message_keyboard(cls, update, bot):
        try:
            keyboard = bot.get_queue().get_students_keyboard_with_position(cls)
            update.effective_message.edit_text(bot.language_pack.select_students, reply_markup=keyboard)
        except Exception:
            log_bot_queue(update, bot, "cannot update list selection message")

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        cls.student = None
        cls.new_position = -1
        keyboard = bot.get_queue().get_students_keyboard_with_position(cls)
        update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        if cls.student is None:
            student_str = CommandHandler.get_arguments(update.callback_query.data)
            student = parsers.parse_student(student_str)
            cls.student = student
            cls.update_message_keyboard(update, bot)
            update.effective_chat.send_message(bot.language_pack.selected_object.format(student.str()))
        elif cls.new_position == -1:
            if not bot.check_queue_selected():
                update.effective_chat.send_message(bot.language_pack.queue_not_selected)
                return

            student_str = CommandHandler.get_arguments(update.callback_query.data)
            student = parsers.parse_student(student_str)
            cls.new_position = bot.get_queue().get_student_position(student)
            if cls.new_position is not None:
                update.effective_chat.send_message(
                    bot.language_pack.selected_position.format(str(cls.new_position + 1))
                )
                cls.handle_request(update, bot)
            else:
                update.effective_chat.send_message(bot.language_pack.selected_position_not_exists)
        else:
            cls.student = None
            cls.new_position = -1
            cls.handle_keyboard(update, bot)

    @classmethod
    def handle_request(cls, update, bot):
        log_bot_queue(update, bot, 'set student position {0}', cls.new_position)
        bot.get_queue().set_student_position(cls.student, cls.new_position)
        update.effective_chat.send_message(
            bot.language_pack.student_moved_to_position.format(cls.student.name, cls.new_position + 1)
        )

        # update keyboard for this message
        cls.update_message_keyboard(update, bot)

        bot.refresh_last_queue_msg(update)
        bot.request_del()


class MoveSwapStudents(AbstractCommand):
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
        MoveSwapStudents.keyboard_message = \
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)
        bot.request_set(cls)

    @classmethod
    def handle_keyboard(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        student_str = CommandHandler.get_arguments(update.callback_query.data)
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

        if MoveSwapStudents.keyboard_message is not None:
            MoveSwapStudents.keyboard_message.delete()

        bot.refresh_last_queue_msg(update)
        bot.request_del()
        log_bot_queue(update, bot, 'swapped {0} and {1}', cls.first_student, cls.second_student)


class AddStudent(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        update.effective_chat.send_message(bot.queues_manager.get_queue_str())
        update.effective_chat.send_message(bot.language_pack.send_student_name_to_end)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if parsers.check_student_name(update.message.text):
            if bot.get_queue().append_by_name(update.message.text):
                log_msg = 'found student in registered \'' + update.message.text + '\''
            else:
                log_msg = 'searched similar student \'' + update.message.text + '\''

            update.effective_chat.send_message(bot.language_pack.student_set)
            bot.refresh_last_queue_msg(update)
            bot.request_del()
            log_bot_queue(update, bot, '{0}', log_msg)
        else:
            update.effective_chat.send_message(bot.language_pack.name_incorrect)


class AddMe(AbstractCommand):
    command_name = 'add_me'
    description = commands_descriptions.add_me_descr

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        student = bot.registered_manager.get_user_by_update(update)
        bot.get_queue().append_to_queue(student)

        err_msg = bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
        if err_msg is not None:
            log_bot_queue(update, bot, err_msg)

        update.message.reply_text(bot.language_pack.you_added_to_queue)

        bot.save_queue_to_file()
        log_bot_queue(update, bot, 'user added himself')


class RemoveMe(AbstractCommand):
    command_name = 'remove_me'
    description = commands_descriptions.remove_me_descr

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        student = bot.registered_manager.get_user_by_update(update)
        if student in bot.get_queue():
            bot.get_queue().remove_student(student)

            err_msg = bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(),
                                                             update.effective_chat)
            if err_msg is not None:
                log_bot_queue(update, bot, err_msg)
            update.message.reply_text(bot.language_pack.you_deleted)

            bot.save_queue_to_file()
            log_bot_queue(update, bot, 'removed himself')
        else:
            update.message.reply_text(bot.language_pack.you_not_found)


class StudentFinished(AbstractCommand):
    command_name = 'i_finished'
    description = commands_descriptions.i_finished_descr

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        student_finished = bot.registered_manager.get_user_by_update(update)

        if student_finished == bot.get_queue().get_current():  # finished user currently first
            bot.queues_manager.get_queue().move_next()
            ShowCurrentAndNextStudent.handle_request(update, bot)
        else:
            update.message.reply_text(bot.language_pack.your_turn_not_now
                                      .format(bot.registered_manager.get_user_by_update(update).str()))

        err_msg = bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
        if err_msg is not None:
            log_bot_queue(update, bot, err_msg)

        bot.save_queue_to_file()
        log_bot_queue(update, bot, 'finished: {0}', bot.get_queue().get_current().str_name_id())
