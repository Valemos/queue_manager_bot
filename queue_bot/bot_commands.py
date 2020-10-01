from te
legram import InputFile

from queue_bot.student import Student
from queue_bot.bot_access_levels import AccessLevel
from queue_bot.students_queue import StudentsQueue
import queue_bot.bot_parsers as parsers


def log_bot_queue(update, bot, message, *args):
    bot.logger.log(' {0} by {1}: '.format(
                       str(bot.get_queue()),
                       bot.registered_manager.get_user_by_update(update)) +
                   message.format(*args))


def log_bot_user(update, bot, message, *args):
    bot.logger.log(' {0}: '.format(
                            bot.registered_manager.get_user_by_update(update)) +
                   message.format(*args))


class CommandGroup:
    class Command:

        access_requirement = AccessLevel.USER

        @classmethod
        def __str__(cls):
            return cls.__qualname__

        @classmethod
        def str(cls, args=None):
            if args is None:
                return cls.__qualname__
            else:
                return cls.__qualname__ + '#' + str(args)

        @staticmethod
        def parse_command(command_str):
            try:
                parts = command_str.split('.')

                cmd_group = parts[0]
                cmd = ''.join(parts[1:])

                if '#' in cmd:
                    cmd = cmd[:cmd.index('#')]

                return cmd_group, cmd
            except ValueError:
                return None, None

        @staticmethod
        def get_arguments(string):
            if '#' in string:
                parts = string.split('#')
                return parts[1]
            else:
                return None

        @classmethod
        def check_access(cls, update, bot, check_chat_private):
            if bot.registered_manager.check_access(update, cls.access_requirement, check_chat_private):
                return True
            else:
                log_bot_user(update, bot, 'tried to get access to {0} command', cls.access_requirement.name)
                if check_chat_private:
                    update.message.reply_text(bot.language_pack.command_for_private_chat)
                else:
                    update.message.reply_text(bot.language_pack.permission_denied)
                return False

        # used as starting point and it checks for user access rights
        @classmethod
        def handle_command(cls, update, bot):
            private_chat_needed = cls.access_requirement is not AccessLevel.USER
            if cls.check_access(update, bot, private_chat_needed):
                cls.handle_reply(update, bot)

        # used to generate message, keyboard and handle_request properly
        @classmethod
        def handle_reply(cls, update, bot):
            cls.handle_request(update, bot)

        # used to handle intermediate states, or multiple choices by keyboard
        # this function will be called only if arguments for command exist
        @classmethod
        def handle_keyboard(cls, update, bot):
            cls.handle_request(update, bot)

        # used for main request handling
        @classmethod
        def handle_request(cls, update, bot):
            print('{0} called default method', cls.str())


class Help(CommandGroup):

    class ForAdmin(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.admin_help)

    class HowToSelectSubject(CommandGroup.Command):
        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.send_choice_numbers)


class General(CommandGroup):

    class Cancel(CommandGroup.Command):

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_message.delete()
            bot.request_del()

    class Start(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            # if god user not exists, set current user as AccessLevel.GOD and set admins as AccessLevel.ADMIN
            if not bot.registered_manager.exists_user_access(AccessLevel.GOD):
                bot.registered_manager.append_new_user(update.message.from_user.username, update.message.from_user.id)
                bot.registered_manager.set_god(update.message.from_user.id)
                update.message.reply_text(bot.language_pack.first_user_added.format(update.message.from_user.username))

                for admin in update.effective_chat.get_administrators():
                    bot.registered_manager.append_new_user(admin.user.username, admin.user.id)
                    bot.registered_manager.set_admin(admin.user.id)

                bot.save_registered_to_file()
                update.effective_chat.send_message(bot.language_pack.admins_added)
            else:
                update.message.reply_text(bot.language_pack.bot_already_running)


    class Stop(CommandGroup.Command):
        access_requirement = AccessLevel.GOD

        @classmethod
        def handle_reply(cls, update, bot):
            update.message.reply_text(bot.language_pack.bot_stopped)
            bot.save_before_stop()
            exit(0)


    class ShowLogs(CommandGroup.Command):
        access_requirement = AccessLevel.GOD

        @classmethod
        def handle_reply(cls, update, bot):
            trim = 4090
            trimmed_msg = bot.logger.get_logs()[-trim:]
            if len(trimmed_msg) >= trim:
                trimmed_msg = "...\n" + trimmed_msg[trimmed_msg.index('\n'):]

            update.effective_chat.send_message(trimmed_msg)


class ModifyCurrentQueue(CommandGroup):

    class ShowMenu(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.message.reply_text(bot.language_pack.title_edit_queue,
                                      reply_markup=bot.keyboards.modify_queue)


    class ShowList(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.get_queue().str_simple())
            log_bot_queue(update, bot, 'showed list')


    class ShowQueueForCopy(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_request(cls, update, bot):
            update.effective_chat.send_message(bot.get_queue().get_str_for_copy())
            update.effective_chat.send_message(bot.language_pack.copy_queue)
            log_bot_queue(update, bot, 'showed list for copy')


    class SetStudents(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.enter_students_list)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            ManageQueues.CreateSimple.handle_request(update, bot)
            log_bot_queue(update, bot, 'set students for {0} by {1}'.format(str(bot.get_queue()),
                                                                            bot.registered_manager.get_user_by_update(update)))


    class SetQueuePosition(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.queues_manager.get_queue_str())
            update.effective_chat.send_message(bot.language_pack.send_new_position)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
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


    class ClearList(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            bot.queues_manager.clear_current_queue()
            update.effective_chat.send_message(bot.language_pack.queue_deleted)
            log_bot_queue(update, bot, 'clear queue')


    class MoveStudentToEnd(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        move_student = None

        @classmethod
        def handle_reply(cls, update, bot):
            cls.move_student = None
            keyboard = bot.get_queue().get_students_keyboard(cls)
            update.effective_chat.send_message(bot.language_pack.select_student, reply_markup=keyboard)
            update.effective_chat.send_message(bot.language_pack.select_student)
            bot.request_set(cls)

        @classmethod
        def handle_keyboard(cls, update, bot):
            argument = cls.get_arguments(update.callback_query.data)
            cls.move_student = parsers.parse_student(argument)
            cls.handle_request(update, bot)

        @classmethod
        def handle_request(cls, update, bot):
            if cls.move_student is None:
                update.callback_query.reply()
                return
            bot.get_queue().move_to_end(cls.move_student)

            bot.refresh_last_queue_msg(update)
            update.effective_chat.send_message(bot.language_pack.student_added_to_end.format(cls.move_student.str()))
            bot.request_del()
            log_bot_queue(update, bot, 'moved {0} to end', str(cls.move_student))


    class RemoveListStudents(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            keyboard = bot.get_queue().get_students_keyboard(cls)
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

        @classmethod
        def handle_keyboard(cls, update, bot):
            cls.handle_request(update, bot)

            # after student deleted, message updates
            keyboard = bot.get_queue().get_students_keyboard(cls)
            # keyboards not equal
            if len(keyboard.inline_keyboard) != len(update.effective_message.reply_markup.inline_keyboard):
                update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

        @classmethod
        def handle_request(cls, update, bot):
            student_str = cls.get_arguments(update.callback_query.data)
            student = parsers.parse_student(student_str)
            bot.get_queue().remove_student(student)
            bot.refresh_last_queue_msg(update)

            bot.request_del()
            log_bot_queue(update, bot, 'removed student {0}', student)


    class SetStudentPosition(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        student = None
        new_position = -1

        @classmethod
        def handle_reply(cls, update, bot):
            cls.student = None
            cls.new_position = -1
            keyboard = bot.get_queue().get_students_keyboard_with_position(cls)
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

        @classmethod
        def handle_keyboard(cls, update, bot):
            if cls.student is None:
                student_str = cls.get_arguments(update.callback_query.data)
                student = parsers.parse_student(student_str)
                cls.student = student
                update.effective_chat.send_message(bot.language_pack.selected_object.format(student.str()))
            elif cls.new_position == -1:
                student = cls.get_arguments(update.callback_query.data)
                position = bot.get_queue().get_student_position(student)
                if position is not None:
                    update.effective_chat.send_message(bot.language_pack.selected_position.format(str(position)))
                    cls.handle_request(update, bot)
                else:
                    update.effective_chat.send_message(bot.language_pack.selected_position_not_exists)

        @classmethod
        def handle_request(cls, update, bot):
            bot.get_queue().set_student_position(cls.student, cls.new_position)
            update.effective_chat.send_message(bot.language_pack.student_moved_to_position.format(cls.student))

            bot.refresh_last_queue_msg(update)
            bot.request_del()
            log_bot_queue(update, bot, 'set student position {0}', cls.new_position)
            

    class AddStudent(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.queues_manager.get_queue_str())
            update.effective_chat.send_message(bot.language_pack.send_student_name_to_end)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            if bot.get_queue().append_by_name(update.message.text):
                log_msg = 'found student in registered \'' + update.message.text + '\''
            else:
                log_msg = 'searched similar student \'' + update.message.text + '\''

            update.effective_chat.send_message(bot.language_pack.student_set)
            bot.refresh_last_queue_msg(update)
            bot.request_del()
            log_bot_queue(update, bot, '{0}', log_msg)
            

    class AddMe(CommandGroup.Command):

        @classmethod
        def handle_request(cls, update, bot):
            student = bot.registered_manager.get_user_by_update(update)
            bot.get_queue().append_to_queue(student)

            bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
            update.message.reply_text(bot.language_pack.you_added_to_queue)

            bot.save_queue_to_file()
            log_bot_queue(update, bot, 'user added himself')


    class RemoveMe(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            student = bot.registered_manager.get_user_by_update(update)
            if student in bot.get_queue():
                bot.get_queue().remove_student(student)

                bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
                update.message.reply_text(bot.language_pack.you_deleted)

                bot.save_queue_to_file()
                log_bot_queue(update, bot, 'removed himself')
            else:
                update.message.reply_text(bot.language_pack.you_not_found)


    class StudentFinished(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            student_finished = bot.registered_manager.get_user_by_update(update)

            if student_finished == bot.queues_manager.get_queue().get_current():  # finished user currently first
                bot.queues_manager.get_queue().move_next()
                bot.send_cur_and_next(update)
            else:
                update.message.reply_text(bot.language_pack.your_turn_not_now
                                          .format(bot.registered_manager.get_user_by_update(update).str()))

            bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
            bot.save_queue_to_file()
            log_bot_queue(update, bot, 'finished: {0}', bot.get_queue().get_current().str_name_id())


    class SwapStudents(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        first_student = None
        second_student = None

        @classmethod
        def handle_reply(cls, update, bot):
            cls.first_student = None
            cls.second_student = None
            keyboard = bot.get_queue().get_students_keyboard_with_position(cls)
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)
            bot.request_set(cls)

        @classmethod
        def handle_keyboard(cls, update, bot):
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
            bot.refresh_last_queue_msg(update)
            bot.request_del()
            log_bot_queue(update, bot, 'swapped {0} and {1}', cls.first_student, cls.second_student)


class ManageQueues(CommandGroup):

    edited_queue = None

    @staticmethod
    def handle_queue_create_request(update, bot, generate_function):
        queue_name, names = parsers.parse_queue_message(update.message.text)
        students = bot.registered_manager.get_registered_students(names)
        queue = bot.queues_manager.create_queue(bot)
        queue.name = queue_name
        generate_function(queue, students)

        if not bot.queues_manager.add_queue(queue):
            update.effective_chat.send_message(bot.language_pack.queue_limit_reached)
            bot.request_del()
            log_bot_queue(update, bot, 'queue limit reached')
        else:
            if queue.name == '':
                # must save queue to add name to it in next command
                ManageQueues.edited_queue = queue
                log_bot_queue(update, bot, 'set students for queue')
                ManageQueues.AddNameToQueue.handle_reply(update, bot)
            else:
                ManageQueues.FinishQueueCreation.handle_reply(update, bot)


    class CreateSimple(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.enter_students_list)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            ManageQueues.handle_queue_create_request(update, bot, StudentsQueue.generate_simple)


    class CreateRandom(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.enter_students_list)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            ManageQueues.handle_queue_create_request(update, bot, StudentsQueue.generate_random)


    class AddNameToQueue(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            if ManageQueues.edited_queue is not None:
                update.effective_chat.send_message(bot.language_pack.enter_queue_name,
                                                   reply_markup=bot.keyboards.set_default_queue_name)
                bot.request_set(cls)
            else:
                bot.request_del()
                log_bot_queue(update, bot, 'in AddNameToQueue queue is None. Error')

        @classmethod
        def handle_request(cls, update, bot):
            if parsers.check_queue_name(update.message.text):
                bot.queues_manager.rename_queue(ManageQueues.edited_queue.name, update.message.text)
                ManageQueues.FinishQueueCreation.handle_reply(update, bot)
            else:
                update.effective_chat.send_message(bot.language_pack.name_incorrect)
                ManageQueues.AddNameToQueue.handle_reply(update, bot)

            log_bot_queue(update, bot, 'queue name set {0}', update.message.text)


    class DefaultQueueName(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_request(cls, update, bot):
            bot.queues_manager.rename_queue(ManageQueues.edited_queue.name, '')
            log_bot_user(update, bot, 'queue set default name')
            ManageQueues.FinishQueueCreation.handle_reply(update, bot)


    class RenameQueue(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            keyboard = bot.queues_manager.generate_choice_keyboard(cls)
            update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

        @classmethod
        def handle_keyboard(cls, update, bot):
            queue_name = cls.get_arguments(update.callback_query.data)
            if queue_name is not None:
                ManageQueues.edited_queue = bot.queues_manager.get_queue_by_name(queue_name)
                ManageQueues.AddNameToQueue.handle_reply(update, bot)
            else:
                log_bot_user(update, bot, 'queue not selected while renaming')


    class FinishQueueCreation(CommandGroup.Command):

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.value_set)
            bot.save_queue_to_file()
            bot.request_del()
            log_bot_queue(update, bot, 'queue set')


    class CreateRandomFromRegistered(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            queue = StudentsQueue(bot)
            queue.generate_random(bot.registered_manager.get_users())  # we specify parameter in "self"

            if not bot.queues_manager.add_queue(queue):
                update.effective_chat.send_message(bot.language_pack.queue_limit_reached)
                bot.request_del()
                log_bot_queue(update, bot, 'queue limit reached')
            else:
                bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
                update.effective_chat.send_message(bot.language_pack.queue_set)
                log_bot_queue(update, bot, 'queue added')
                ManageQueues.AddNameToQueue.handle_reply(update, bot)


    class DeleteQueue(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            keyboard = bot.queues_manager.generate_choice_keyboard(cls)
            update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

        @classmethod
        def handle_request(cls, update, bot):
            queue_name = CommandGroup.Command.get_arguments(update.callback_query.data)
            if queue_name is not None:
                if bot.queues_manager.remove_queue(queue_name):
                    update.effective_chat.send_message(bot.language_pack.queue_removed.format(queue_name))
                    update.effective_message.delete()
                    bot.refresh_last_queue_msg(update)
                else:
                    log_bot_user(update, bot, 'queue not found, query: {2}', update.callback_query.data)
            else:
                log_bot_user(update, bot, 'request {0} in {1} has no arguments', update.callback_query.data, cls.__qualname__)
            update.callback_query.answer()


    class SelectOtherQueue(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            keyboard = bot.queues_manager.generate_choice_keyboard(cls)
            update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

        @classmethod
        def handle_keyboard(cls, update, bot):
            queue_name = CommandGroup.Command.get_arguments(update.callback_query.data)
            if queue_name is not None:
                if bot.queues_manager.set_current_queue(queue_name):
                    update.effective_chat.send_message(bot.language_pack.queue_set)
                    bot.refresh_last_queue_msg(update)
                else:
                    log_bot_queue(update, bot, 'queue not found, query: {0}', update.callback_query.data)
            else:
                log_bot_user(update, bot, 'request {0} in {1} has no arguments', update.callback_query.data, cls.__qualname__)
            update.callback_query.answer()


class ModifyRegistered(CommandGroup):

    class ShowMenu(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.title_edit_registered,
                                               reply_markup=bot.keyboards.modify_registered)


    class ShowListUsers(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.registered_manager.get_users_str())


    class AddListUsers(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.set_registered_students)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            new_users, errors = parsers.parse_users(update.effective_message.text)
            bot.registered_manager.append_users(new_users)

            if len(errors) > 0:
                update.effective_chat.send_message(bot.language_pack.error_in_this_values.format('\n'.join(errors)))
            if len(new_users) > 0:
                update.effective_chat.send_message(bot.language_pack.users_added)

            bot.save_registered_to_file()
            bot.request_del()
            log_bot_queue(update, bot, 'added users: {0}', new_users)


    class AddUser(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.get_user_message)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                bot.registered_manager.append_new_user(update.message.forward_from.full_name, update.message.forward_from.id)
                update.message.reply_text(bot.language_pack.user_register_successfull)
                bot.save_registered_to_file()
                log_bot_queue(update, bot, 'added one user: {0}', update.message.forward_from.full_name)
            else:
                update.message.reply_text(bot.language_pack.was_not_forwarded)

            bot.request_del()
            

    class RenameAllUsers(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.enter_new_list_in_order)
            bot.request_set(cls)

        def handle_request(cls, update, bot):
            names = parsers.parse_names(update.message.text)
            if len(names) <= len(bot.registered_manager):
                for i in range(len(names)):
                    bot.registered_manager.rename_user(i, names[i])
            else:
                update.effective_chat.send_message(bot.language_pack.names_more_than_users)
                bot.logger.log('names more than users - {0}'
                               .format(bot.registered_manager.get_user_by_update(update)))
            bot.request_del()

    class RenameUser(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        edited_user = None

        @classmethod
        def handle_reply(cls, update, bot):
            cls.edited_user = None
            keyboard = bot.get_queue().get_students_keyboard(cls)
            update.effective_chat.send_message(bot.language_pack.select_student, reply_markup=keyboard)
            update.effective_chat.send_message(bot.language_pack.select_student)
            bot.request_set(cls)

        @classmethod
        def handle_keyboard(cls, update, bot):
            argument = cls.get_arguments(update.callback_query.data)
            cls.edited_user = parsers.parse_student(argument)
            update.effective_chat.send_message(bot.language_pack.enter_student_name)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            if cls.edited_user is not None:
                bot.registered_manager.rename_user(cls.edited_user, update.message.text)
                update.effective_chat.send_message(bot.language_pack.value_set)
                log_bot_user(update, bot, 'student {0} renamed to {1}', cls.edited_user, update.message.text)
            else:
                log_bot_user(update, bot, 'error, student was none in {0}', cls.str())



    class RemoveListUsers(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            keyboard = bot.registered_manager.get_users_keyboard(cls)
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

        @classmethod
        def handle_keyboard(cls, update, bot):
            cls.handle_request(update, bot)
            keyboard = bot.registered_manager.get_users_keyboard(cls)
            # if keyboards not equal
            if len(keyboard.inline_keyboard) != len(update.effective_message.reply_markup.inline_keyboard):
                update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

        @classmethod
        def handle_request(cls, update, bot):
            student_str = cls.get_arguments(update.callback_query.data)
            user = parsers.parse_student(student_str)
            if user.telegram_id is not None:
                bot.registered_manager.remove_by_id(user.telegram_id)
                bot.refresh_last_queue_msg(update)

                bot.request_del()
                log_bot_queue(update, bot, 'removed user {0}', user)
            else:
                log_bot_user(update, bot, 'error, user id is None in {0}', cls.str())


class UpdateQueue(CommandGroup):

    class ShowCurrent(CommandGroup.Command):

        @classmethod
        def handle_reply(cls, update, bot):
            bot.last_queue_message.resend(bot.queues_manager.get_queue_str(),
                                          update.effective_chat,
                                          bot.keyboards.move_queue)
            log_bot_user(update, bot, ' in {0} chat requested queue', update.effective_chat.type)


    class ShowCurrentAndNext(CommandGroup.Command):

        @classmethod
        def handle_request(cls, update, bot):
            bot.cur_students_message.resend(bot.get_queue().get_cur_and_next_str(), update.effective_chat)


    class MovePrevious(CommandGroup.Command):
        @classmethod
        def handle_reply(cls, update, bot):
            if bot.get_queue().move_prev():
                bot.send_cur_and_next(update)
                bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
                log_bot_user(update, bot, 'moved previous')


    class MoveNext(CommandGroup.Command):
        @classmethod
        def handle_reply(cls, update, bot):
            if bot.get_queue().move_next():
                bot.send_cur_and_next(update)
                bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
                log_bot_user(update, bot, 'moved queue')


    class Refresh(CommandGroup.Command):
        @classmethod
        def handle_reply(cls, update, bot):
            if not bot.last_queue_message.message_exists(update.effective_chat):
                update.effective_message.delete()
            bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
            log_bot_user(update, bot, 'refreshed queue')


class ManageAccessRights(CommandGroup):

    class AddAdmin(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.get_user_message)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                if bot.registered_manager.set_admin(update.message.forward_from.id):
                    update.message.reply_text(bot.language_pack.admin_set)
                    bot.save_registered_to_file()
                    log_bot_user(update, bot, 'added admin {0}', update.message.forward_from.full_name)
                else:
                    bot.registered_manager.append_new_user(
                        update.message.forward_from.full_name,
                        update.message.forward_from.id)
                    bot.registered_manager.set_admin(update.message.forward_from.id)
            else:
                update.message.reply_text(bot.language_pack.was_not_forwarded)
                log_bot_user(update, bot, 'admin message not forwarded in {0}', cls.str())
            bot.request_del()


    class RemoveAdmin(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            keyboard = bot.registered_manager.get_admins_keyboard(cls)
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

        @classmethod
        def handle_keyboard(cls, update, bot):
            cls.handle_request(update, bot)
            keyboard = bot.registered_manager.get_admins_keyboard(cls)
            if len(keyboard.inline_keyboard) != len(update.effective_message.reply_markup.inline_keyboard):
                update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

        @classmethod
        def handle_request(cls, update, bot):
            student_str = cls.get_arguments(update.callback_query.data)
            user = parsers.parse_student(student_str)
            if user.telegram_id is not None:
                if bot.registered_manager.set_user(user.telegram_id):
                    bot.save_registered_to_file()
                    update.message.reply_text(bot.language_pack.admin_deleted)
                    log_bot_user(update, bot, 'deleted admin {0}', update.message.forward_from.full_name)
            else:
                log_bot_user(update, bot, 'error, admin id was None in {0}', cls.str())
            bot.request_del()


class CollectSubjectChoices(CommandGroup):

    command_parameters = {}

    @staticmethod
    def get_choices_available_str(bot):
        choices_str, available = bot.choice_manager.get_choices_str()
        if choices_str == '':
            choices_str = bot.language_pack.choices_not_made
        if available == '':
            available = bot.language_pack.not_available
        return bot.language_pack.show_choices.format(choices_str, available)

    # These commands (except the last) are executed in a row
    # they collect parameters of subject choices handling
    class CreateNewCollectFile(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.send_choice_file_name)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            subject_name = update.message.text
            if ' ' in subject_name:
                update.effective_chat.send_message(bot.language_pack.send_subject_name_without_spaces)
                return
            else:
                CollectSubjectChoices.command_parameters['name'] = subject_name
                update.effective_chat.send_message(bot.language_pack.value_set)
                log_bot_user(update, bot, 'start setting new subject')
                CollectSubjectChoices.SetSubjectsRange.handle_reply(update, bot)


    class SetSubjectsRange(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.send_number_range)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            min_range, max_range = parsers.parce_number_range(update.message.text)
            if min_range is None:
                update.effective_chat.send_message(bot.language_pack.number_range_incorrect)
            else:
                CollectSubjectChoices.command_parameters['interval'] = (min_range, max_range)
                update.effective_chat.send_message(bot.language_pack.number_interval_set)
                log_bot_user(update, bot, 'set number interval')
                CollectSubjectChoices.SetRepeatLimit.handle_reply(update, bot)
                

    class SetRepeatLimit(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.set_repeatable_limit)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            limit = parsers.parce_integer(update.message.text)

            if limit is None:
                update.effective_chat.send_message(bot.language_pack.int_value_incorrect)
            else:
                CollectSubjectChoices.command_parameters['repeat_limit'] = limit
                update.effective_chat.send_message(bot.language_pack.value_set)
                log_bot_user(update, bot, 'set repeat limit')
                CollectSubjectChoices.FinishSubjectChoiceCreation.handle_reply(update, bot)


    class FinishSubjectChoiceCreation(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_reply(cls, update, bot):
            name = CollectSubjectChoices.command_parameters['name']
            interval = CollectSubjectChoices.command_parameters['interval']
            repeat_limit = CollectSubjectChoices.command_parameters['repeat_limit']
            CollectSubjectChoices.command_parameters = {}

            bot.choice_manager.set_choice_group(name, interval, repeat_limit)
            update.effective_chat.send_message(bot.language_pack.finished_choice_manager_creation)
            bot.request_del()
            log_bot_user(update, bot, 'finished new subject creation')


    class Choose(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            if not bot.choice_manager.can_choose:
                update.effective_chat.send_message(bot.language_pack.choices_collection_not_started)
                return

            subject_range = bot.choice_manager.get_subject_range()
            choices, errors = parsers.parse_positions_list(update.message.text, *subject_range)

            student_requested = bot.registered_manager.get_user_by_update(update)

            if student_requested is None:
                student_requested = Student(update.effective_user.full_name, None)

            subject_chosen = bot.choice_manager.add_choice(student_requested, choices)
            if subject_chosen is not None:
                # update choices message
                choices_str = CollectSubjectChoices.get_choices_available_str(bot)
                bot.subject_choices_message.update_contents(choices_str, update.effective_chat)

                # send message with reply
                update.message.reply_text(bot.language_pack.your_choice.format(subject_chosen))
                log_bot_user(update, bot, 'user chosed subject {0}', subject_chosen)
            else:
                update.effective_chat.send_message(bot.language_pack.cannot_choose_any_subject)
                log_bot_user(update, bot, 'cannot choose subject')

            bot.request_del()


    class RemoveChoice(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            if not bot.choice_manager.can_choose:
                update.effective_chat.send_message(bot.language_pack.choices_collection_not_started)
                log_bot_user(update, bot, 'requested remove while choice not started')
                return

            student_requested = bot.registered_manager.get_user_by_update(update)
            bot.choice_manager.remove_choice(student_requested)
            update.effective_chat.send_message(bot.language_pack.your_choice_deleted)
            log_bot_user(update, bot, 'choice removed')


    class StartChoose(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_request(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.send_choice_numbers)
            if not bot.choice_manager.start_choosing():
                update.effective_chat.send_message(bot.language_pack.set_new_choice_file)
                log_bot_user(update, bot, 'cannot start choice, must perform setup')
            else:
                log_bot_user(update, bot, 'subject choice started')

            bot.request_set(cls)


    class StopChoose(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_request(cls, update, bot):
            if not bot.choice_manager.can_choose:
                update.effective_chat.send_message(bot.language_pack.choices_collection_not_started)
                log_bot_user(update, bot, 'requested stop while choice not started')
                return

            bot.choice_manager.current_subjects.save_to_excel()
            bot.choice_manager.stop_choosing()
            update.effective_chat.send_message(bot.language_pack.choices_collection_stopped)
            log_bot_user(update, bot, 'subject choice stopped')


    class ShowCurrentChoices(CommandGroup.Command):

        @classmethod
        def handle_request(cls, update, bot):
            if bot.choice_manager.current_subjects is not None:
                choices_str = CollectSubjectChoices.get_choices_available_str(bot)
                bot.subject_choices_message.resend(choices_str, update.effective_chat)
                log_bot_user(update, bot, 'requested show choices')
            else:
                update.effective_chat.send_message(bot.language_pack.choices_collection_not_started)


    class GetExcelFile(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_request(cls, update, bot):
            update.effective_chat.send_message(bot.language_pack.get_choices_excel_file)
            excel_path = bot.choice_manager.save_to_excel()

            try:
                with excel_path.open('rb') as fin:
                    update.effective_chat.send_document(InputFile(fin, filename=str(excel_path)))
            except Exception as err:
                log_bot_user(update, bot, 'cannot send choice document to ')
                log_bot_user(update, bot, str(err))

