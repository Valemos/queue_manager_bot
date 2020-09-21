from queue_bot.bot_access_levels import AccessLevel
import queue_bot.bot_parcers as parcers
from telegram import InputFile
from queue_bot.students_queue import StudentsQueue


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
                return cls.__qualname__ + '#' + args

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
        def handle(cls, update, bot):
            pass

        @classmethod
        def handle_request(cls, update, bot):
            pass


class Help(CommandGroup):

    class ForAdmin(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().admin_help)

    class HowToChooseSubject(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().send_choice_numbers)


class General(CommandGroup):

    class Cancel(CommandGroup.Command):

        @classmethod
        def handle(cls, update, bot):
            update.effective_message.delete()
            bot.request_del()


class ModifyCurrentQueue(CommandGroup):

    class ShowList(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queues_manager.get_queue_str())


    class ShowQueueForCopy(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(self, update, bot):
            names = bot.queues_manager.get_queue().get_student_names()
            update.effective_chat.send_message('\n'.join(names))
            update.effective_chat.send_message(bot.get_language_pack().copy_queue)


    class SetStudents(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().enter_students_list)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            QueuesManage.CreateSimple.handle_request(update, bot)


    class SetQueuePosition(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queues_manager.get_queue_str())
            update.effective_chat.send_message(bot.get_language_pack().send_new_position)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            try:
                new_index = int(update.message.text)
                assert 0 < new_index <= len(bot.queues_manager.get_queue())
                bot.queues_manager.get_queue().set_position(new_index - 1)

                update.effective_chat.send_message(bot.get_language_pack().position_set)
            except (ValueError, AssertionError):
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)
            finally:
                bot.refresh_last_queue_msg(update)

                bot.request_del()


    class ClearList(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            bot.queues_manager.clear_current_queue()
            update.effective_chat.send_message(bot.get_language_pack().queue_deleted)


    class MoveStudentToEnd(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queues_manager.get_queue_str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_number)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            try:
                move_pos = int(update.message.text) - 1
                if move_pos >= len(bot.queues_manager.get_queue()) or move_pos < 0:
                    
                    return

                bot.queues_manager.get_queue().move_to_end(move_pos)
                bot.refresh_last_queue_msg(update)
                update.effective_chat.send_message(bot.get_language_pack().student_added_to_end)
            except ValueError:
                update.effective_chat.send_message(bot.get_language_pack().not_index_from_queue)
            bot.request_del()


    class RemoveStudentsList(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queues_manager.get_queue_str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_numbers_with_space)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            positions, errors = parcers.parse_positions_list(update.message.text, 1, len(bot.queues_manager.get_queue()))
            bot.queues_manager.get_queue().remove_by_index([i - 1 for i in positions])
            bot.refresh_last_queue_msg(update)


            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values.format(', '.join(errors)))
            if len(positions) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_deleted)
            bot.request_del()


    class SetStudentPosition(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queues_manager.get_queue_str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_number_and_new_position)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            positions, errors = parcers.parse_positions_list(update.message.text,
                                                             1,
                                                             len(bot.queues_manager.get_queue()))

            if len(positions) >= 2:
                if bot.queues_manager.get_queue().move_to_index(positions[0] - 1, positions[1] - 1):
                    update.effective_chat.send_message(bot.get_language_pack().students_moved)
            elif len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)
            else:
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)

            bot.refresh_last_queue_msg(update)

            bot.request_del()
            

    class AddStudent(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queues_manager.get_queue_str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_name_to_end)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            if bot.queues_manager.get_queue().append_by_name(update.message.text):
                bot.logger.log('student set ' + update.message.text + ' found in registered')
            else:
                bot.logger.log('student set ' + update.message.text + ' not found')

            update.effective_chat.send_message(bot.get_language_pack().student_set)

            bot.refresh_last_queue_msg(update)

            bot.request_del()
            

    class SwapStudents(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queues_manager.get_queue_str())
            update.effective_chat.send_message(bot.get_language_pack().send_two_positions_students_space)
            bot.request_set(cls)
        
        @classmethod
        def handle_request(cls, update, bot):
            try:
                user_str = update.message.text.split(' ')
                cur_pos, swap_pos = int(user_str[0]) - 1, int(user_str[1]) - 1

                if 0 <= cur_pos < len(bot.queues_manager.get_queue()) and 0 <= swap_pos < len(bot.queues_manager):
                    bot.queues_manager.get_queue().swap(cur_pos, swap_pos)
                    update.effective_chat.send_message(bot.get_language_pack().students_moved)
                else:
                    update.effective_chat.send_message(bot.get_language_pack().error_in_values)

            except ValueError:
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)
            finally:
                bot.refresh_last_queue_msg(update)

                bot.request_del()


class QueuesManage(CommandGroup):

    temporary_queue = None

    @staticmethod
    def finish_queue_students_set(update, bot):
        bot.refresh_last_queue_msg(update)
        # TODO after this line Error: Object of type InlineKeyboardMarkup is not JSON serializable
        update.effective_chat.send_message(bot.get_language_pack().students_set, bot.keyboards.add_name_to_queue)
        bot.request_del()

    class CreateSimple(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().enter_students_list)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            names = parcers.parse_names(update.message.text)
            students = bot.registered_manager.get_registered_students(names)

            queue = StudentsQueue(bot)
            queue.generate_simple(students)
            if bot.queues_manager.add_queue(queue):
                update.effective_chat.send_message(bot.get_language_pack().queue_set)
            else:
                update.effective_chat.send_message(bot.get_language_pack().queue_limit_reached)
                bot.request_del()
                return

            QueuesManage.finish_queue_students_set(update, bot)
            QueuesManage.temporary_queue = queue
            QueuesManage.AddNameToQueue.handle(update, bot)


    class CreateRandom(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().enter_students_list)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            names = parcers.parse_names(update.message.text)
            students = bot.registered_manager.get_registered_students(names)

            queue = StudentsQueue(bot)
            queue.generate_random(students)

            QueuesManage.finish_queue_students_set(update, bot)
            QueuesManage.temporary_queue = queue
            QueuesManage.AddNameToQueue.handle(update, bot)


    class AddNameToQueue(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().enter_queue_name,
                                               reply_markup=bot.keyboards.set_default_queue_name)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            if parcers.check_queue_name(update.message.text):
                QueuesManage.temporary_queue.name = update.message.text
                bot.queues_manager.add_queue(QueuesManage.temporary_queue)

                update.effective_chat.send_message(bot.get_language_pack().value_set)
                bot.request_del()
            else:
                update.effective_chat.send_message(bot.get_language_pack().name_incorrect)
                QueuesManage.AddNameToQueue.handle(update, bot)


    class DefaultQueueName(CommandGroup.Command):

        @classmethod
        def handle(cls, update, bot):
            QueuesManage.temporary_queue.name = ''
            bot.queues_manager.add_queue(QueuesManage.temporary_queue)

            update.effective_message.delete()
            update.effective_chat.send_message(bot.get_language_pack().value_set)
            bot.request_del()


    class CreateRandomFromRegistered(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            import random
            new_queue_students = bot.registered_manager.get_users()
            random.shuffle(new_queue_students)
            bot.queues_manager.get_queue().set_students(new_queue_students)
            bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)


    class DeleteQueue(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            queue_name = CommandGroup.Command.get_arguments(update.callback_query.data)
            if queue_name is not None:
                if bot.queues_manager.remove_queue(queue_name):
                    update.effective_chat.send_message(bot.get_language_pack().queue_removed.format(queue_name))
                    update.effective_message.delete()
                else:
                    bot.logger.log('queue not found, query: {0}'.format(update.callback_query.data))
            else:
                bot.logger.log('request {0} in {1} is None'.format(update.callback_query.data, cls.__qualname__))


    class ChooseOtherQueue(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            queue_name = CommandGroup.Command.get_arguments(update.callback_query.data)
            if queue_name is not None:
                if bot.queues_manager.set_current_queue(queue_name):
                    update.effective_chat.send_message(bot.get_language_pack().queue_set)
                else:
                    bot.logger.log('queue not found, query: {0}'.format(update.callback_query.data))
            else:
                bot.logger.log('request {0} in {1} is None'.format(update.callback_query.data, cls.__qualname__))


class ModifyRegistered(CommandGroup):
    class ShowListUsers(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.registered_manager.get_users_str())


    class AddListUsers(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().set_registered_students)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            new_users, errors = parcers.parse_users(update.effective_message.text)
            bot.registered_manager.append_users(new_users)

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values.format('\n'.join(errors)))
            if len(new_users) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_added)

            bot.save_registered_to_file()
            bot.request_del()


    class AddUser(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().get_user_message)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                bot.registered_manager.append_new_user(update.message.forward_from.full_name, update.message.forward_from.id)
                update.message.reply_text(bot.get_language_pack().user_register_successfull)
            else:
                update.message.reply_text(bot.get_language_pack().was_not_forwarded)

            bot.save_registered_to_file()
            bot.request_del()
            

    class RenameAllUsers(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().enter_new_list_in_order)
            bot.request_set(cls)

        def handle_request(cls, update, bot):
            names = parcers.parse_names(update.message.text)
            if len(names) <= len(bot.registered_manager):
                for i in range(len(names)):
                    bot.registered_manager.rename(i, names[i])
            else:
                update.effective_chat.send_message(bot.get_language_pack().names_more_than_users)
            bot.request_del()


    class RemoveListUsers(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.registered_manager.get_users_str())
            update.effective_chat.send_message(bot.get_language_pack().del_registered_students)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            # parse function is inside of queue object
            delete_indexes, errors = parcers.parse_positions_list(update.message.text, 1, len(bot.registered_manager))
            bot.registered_manager.remove_by_index([i - 1 for i in delete_indexes])
            bot.save_registered_to_file()

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values.format('\n'.join(errors)))
            if len(delete_indexes) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_deleted)

            bot.request_del()
            

class UpdateQueue(CommandGroup):
    class MovePrevious(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            if bot.queues_manager.get_queue().move_prev():
                bot.send_cur_and_next(update)
                bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)


    class MoveNext(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            if bot.queues_manager.get_queue().move_next():
                bot.send_cur_and_next(update)
                bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)


    class Refresh(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            if not bot.last_queue_message.message_exists(update.effective_chat):
                update.effective_message.delete()
            bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)


class ManageUsers(CommandGroup):
    class AddAdmin(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                if bot.registered_manager.set_admin(update.effective_user.id):
                    update.message.reply_text(bot.get_language_pack().admin_set)
            else:
                update.message.reply_text(bot.get_language_pack().was_not_forwarded)
            bot.save_registered_to_file()
            bot.request_del()
            

    class RemoveAdmin(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                if bot.registered_manager.set_user(update.message.forward_from.id):
                    update.message.reply_text(bot.get_language_pack().admin_deleted)
            else:
                update.message.reply_text(bot.get_language_pack().was_not_forwarded)
            bot.save_registered_to_file()
            bot.request_del()
            

    class AddUsersList(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle_request(cls, update, bot):
            users, errors = parcers.parse_users(update.message.text)
            bot.registered_manager.append_users(users)

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values('\n'.join(errors)))
            if len(users) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_added)

            bot.save_registered_to_file()
            bot.request_del()


class CollectSubjectChoices(CommandGroup):

    command_parameters = {}

    @staticmethod
    def get_choices_available_str(bot):
        choices_str, available = bot.choice_manager.get_choices_str()
        if choices_str == '':
            choices_str = bot.get_language_pack().choices_not_made
        if available == '':
            available = bot.get_language_pack().not_available
        return bot.get_language_pack().show_choices.format(choices_str, available)

    # These commands (except the last) are executed in a row
    # they collect parameters of subject choices handling
    class CreateNewCollectFile(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().send_choice_file_name)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            subject_name = update.message.text
            if ' ' in subject_name:
                update.effective_chat.send_message(bot.get_language_pack().send_subject_name_without_spaces)
                return
            else:
                CollectSubjectChoices.command_parameters['name'] = subject_name
                update.effective_chat.send_message(bot.get_language_pack().value_set)
                CollectSubjectChoices.SetSubjectsRange.handle(update, bot)


    class SetSubjectsRange(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().send_number_range)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            min_range, max_range = parcers.parce_number_range(update.message.text)
            if min_range is None:
                update.effective_chat.send_message(bot.get_language_pack().number_range_incorrect)
            else:
                CollectSubjectChoices.command_parameters['interval'] = (min_range, max_range)
                update.effective_chat.send_message(bot.get_language_pack().number_interval_set)
                CollectSubjectChoices.SetRepeatLimit.handle(update, bot)
                

    class SetRepeatLimit(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().set_repeatable_limit)
            bot.request_set(cls)

        @classmethod
        def handle_request(cls, update, bot):
            limit = parcers.parce_integer(update.message.text)

            if limit is None:
                update.effective_chat.send_message(bot.get_language_pack().int_value_incorrect)
            else:
                CollectSubjectChoices.command_parameters['repeat_limit'] = limit
                update.effective_chat.send_message(bot.get_language_pack().value_set)
                CollectSubjectChoices.FinishSubjectChoiceCreation.handle(update, bot)


    class FinishSubjectChoiceCreation(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            name = CollectSubjectChoices.command_parameters['name']
            interval = CollectSubjectChoices.command_parameters['interval']
            repeat_limit = CollectSubjectChoices.command_parameters['repeat_limit']
            CollectSubjectChoices.command_parameters = {}

            bot.choice_manager.set_choice_group(name, interval, repeat_limit)
            update.effective_chat.send_message(bot.get_language_pack().finished_choice_manager_creation)

            bot.request_del()


    class Choose(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            if not bot.choice_manager.can_choose:
                update.effective_chat.send_message(bot.get_language_pack().choices_collection_not_started)
                return

            subject_range = bot.choice_manager.get_subject_range()
            choices, errors = parcers.parse_positions_list(update.message.text, *subject_range)

            student_requested = bot.registered_manager.get_user_by_id(update.effective_user.id)
            if student_requested != None:
                subject_chosen = bot.choice_manager.add_choice(student_requested, choices)
                if subject_chosen is not None:
                    # update choices message
                    choices_str = CollectSubjectChoices.get_choices_available_str(bot)
                    bot.subject_choices_message.update_contents(choices_str, update.effective_chat)

                    # send message with reply
                    update.message.reply_text(bot.get_language_pack().your_choice.format(subject_chosen))
                else:
                    update.effective_chat.send_message(bot.get_language_pack().cannot_choose_any_subject)
            else:
                update.effective_chat.send_message(bot.get_language_pack().unknown_user)
            bot.request_del()


    class RemoveChoice(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            if not bot.choice_manager.can_choose:
                update.effective_chat.send_message(bot.get_language_pack().choices_collection_not_started)
                return

            student_requested = bot.registered_manager.get_user_by_id(update.effective_user.id)
            if student_requested != None:
                bot.choice_manager.remove_choice(student_requested)
                update.effective_chat.send_message(bot.get_language_pack().your_choice_deleted)
            else:
                update.effective_chat.send_message(bot.get_language_pack().unknown_user)


    class StartChoose(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().send_choice_numbers)
            if not bot.choice_manager.start_choosing():
                update.effective_chat.send_message(bot.get_language_pack().set_new_choice_file)

            bot.request_set(cls)


    class StopChoose(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(self, update, bot):
            if not bot.choice_manager.can_choose:
                update.effective_chat.send_message(bot.get_language_pack().choices_collection_not_started)
                return

            bot.choice_manager.current_subjects.save_to_excel()
            bot.choice_manager.stop_choosing()
            update.effective_chat.send_message(bot.get_language_pack().choices_collection_stopped)


    class ShowCurrentChoices(CommandGroup.Command):

        @classmethod
        def handle(cls, update, bot):
            if bot.choice_manager.current_subjects is not None:
                choices_str = CollectSubjectChoices.get_choices_available_str(bot)
                bot.subject_choices_message.resend(choices_str, update.effective_chat)
            else:
                update.effective_chat.send_message(bot.get_language_pack().choices_collection_not_started)


    class GetExcelFile(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().get_choices_excel_file)
            excel_path = bot.choice_manager.save_to_excel()

            with excel_path.open('rb') as fin:
                update.effective_chat.send_document(InputFile(fin, filename=str(excel_path)))

