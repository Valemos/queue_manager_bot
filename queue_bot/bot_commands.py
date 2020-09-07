import pandas as pd  # for excel export
from queue_bot.bot_access_levels import AccessLevel
import queue_bot.bot_parcers as parcers

class CommandGroup:
    class Command:

        access_requirement = AccessLevel.USER

        @classmethod
        def __str__(cls):
            return cls.__qualname__

        @classmethod
        def str(cls):
            return cls.__qualname__

        @staticmethod
        def parse_command(command_str):
            try:
                # __qualname__ returns class in format Class.Subclass and query formed only from it
                items = command_str.split('.')
                return items[0], ''.join(items[1:])
            except ValueError:
                return None, None

        @classmethod
        def handle(cls, update, bot):
            pass

        @classmethod
        def handle_request(cls, update, bot):
            pass


class ModifyQueue(CommandGroup):

    class CreateSimple(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            bot.queue.clear()
            update.effective_chat.send_message(bot.get_language_pack().enter_students_list)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            students = parcers.parse_students(update.message.text)
            bot.queue.generate_simple(students)
            bot.refresh_last_queue_msg(update)
            update.effective_chat.send_message(bot.get_language_pack().students_set)
            bot.save_queue_to_file()
            bot.request_handled()


    class CreateRandom(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            bot.queue.clear()
            update.effective_chat.send_message(bot.get_language_pack().enter_students_list)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            students = parcers.parse_students(update.message.text)
            bot.queue.generate_random(students)
            bot.refresh_last_queue_msg(update)
            update.effective_chat.send_message(bot.get_language_pack().students_set)
            bot.save_queue_to_file()
            bot.request_handled()


    class CreateRandomFromRegistered(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            import random
            new_queue_students = bot.registered_manager.get_users()
            random.shuffle(new_queue_students)
            bot.queue.set_students(new_queue_students)
            bot.last_queue_message.update_contents(bot.queue.str())
            bot.save_queue_to_file()


    class Cancel(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_message.delete()


    class ShowList(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())


    class SetStudents(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().enter_students_list)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            ModifyQueue.CreateSimple.handle_request(update, bot)


    class SetQueuePosition(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())
            update.effective_chat.send_message(bot.get_language_pack().send_new_position)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            try:
                new_index = int(update.message.text)
                assert 0 < new_index <= len(bot.queue)
                bot.queue.queue_pos = new_index - 1

                update.effective_chat.send_message(bot.get_language_pack().position_set)
            except (ValueError, AssertionError):
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)
            finally:
                bot.refresh_last_queue_msg(update)
                bot.save_queue_to_file()
                bot.request_handled()
                

    class ClearList(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            bot.queue.clear()
            update.effective_chat.send_message(bot.get_language_pack().queue_deleted)


    class MoveStudentToEnd(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_number)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            try:
                move_pos = int(update.message.text) - 1
                if move_pos >= len(bot.queue) or move_pos < 0:
                    
                    return

                bot.queue.move_to_end(move_pos)
                bot.refresh_last_queue_msg(update)
                update.effective_chat.send_message(bot.get_language_pack().student_added_to_end)
            except ValueError:
                update.effective_chat.send_message(bot.get_language_pack().not_index_from_queue)
            bot.request_handled()


    class RemoveStudentsList(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_numbers_with_space)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            positions, errors = parcers.parse_positions_list(update.message.text, len(bot.queue))
            bot.queue.remove_by_index([i - 1 for i in positions])
            bot.refresh_last_queue_msg(update)
            bot.save_queue_to_file()

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values.format(', '.join(errors)))
            if len(positions) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_deleted)
            bot.request_handled()


    class SetStudentPosition(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_number_and_new_position)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            positions, errors = parcers.parse_positions_list(update.message.text, len(bot.queue))

            if len(positions) >= 2:
                if bot.queue.move_to_index(positions[0]-1, positions[1]-1):
                    update.effective_chat.send_message(bot.get_language_pack().students_moved)
            elif len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)
            else:
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)

            bot.refresh_last_queue_msg(update)
            bot.save_queue_to_file()
            bot.request_handled()
            

    class AddStudent(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_name_to_end)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            if bot.queue.append_by_name(update.message.text):
                bot.logger.log('student set ' + update.message.text + ' found in registered')
            else:
                bot.logger.log('student set ' + update.message.text + ' not found')

            update.effective_chat.send_message(bot.get_language_pack().student_set)

            bot.refresh_last_queue_msg(update)
            bot.save_queue_to_file()
            bot.request_handled()
            

    class SwapStudents(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())
            update.effective_chat.send_message(bot.get_language_pack().send_two_positions_students_space)
            bot.set_request(cls)
        
        @classmethod
        def handle_request(cls, update, bot):
            try:
                user_str = update.message.text.split(' ')
                cur_pos, swap_pos = int(user_str[0]) - 1, int(user_str[1]) - 1

                if 0 <= cur_pos < len(bot.queue) and 0 <= swap_pos < len(bot.queue):
                    bot.queue.swap(cur_pos, swap_pos)
                    update.effective_chat.send_message(bot.get_language_pack().students_moved)
                else:
                    update.effective_chat.send_message(bot.get_language_pack().error_in_values)

            except ValueError:
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)
            finally:
                bot.refresh_last_queue_msg(update)
                bot.save_queue_to_file()
                bot.request_handled()


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
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            new_users, errors = parcers.parse_users(update.effective_message.text)
            bot.registered_manager.append_users(new_users)

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values.format('\n'.join(errors)))
            if len(new_users) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_added)

            bot.save_registered_to_file()
            bot.request_handled()


    class AddUser(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().get_user_message)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                bot.registered_manager.append_new_user(update.message.forward_from.full_name, update.message.forward_from.id)
                update.message.reply_text(bot.get_language_pack().user_register_successfull)
            else:
                update.message.reply_text(bot.get_language_pack().was_not_forwarded)

            bot.save_registered_to_file()
            bot.request_handled()
            

    class RenameAllUsers(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().enter_new_list_in_order)
            bot.set_request(cls)

        def handle_request(cls, update, bot):
            names = parcers.parse_names(update.message.text)
            if len(names) <= len(bot.registered_manager):
                for i in range(len(names)):
                    bot.registered_manager.rename(i, names[i])
            else:
                update.effective_chat.send_message(bot.get_language_pack().names_more_than_users)
            bot.request_handled()


    class RemoveListUsers(CommandGroup.Command):

        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.registered_manager.get_users_str())
            update.effective_chat.send_message(bot.get_language_pack().del_registered_students)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            # parse function is inside of queue object
            delete_indexes, errors = parcers.parse_positions_list(update.message.text, len(bot.registered_manager))
            bot.registered_manager.remove_by_index([i - 1 for i in delete_indexes])

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values.format('\n'.join(errors)))
            if len(delete_indexes) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_deleted)

            bot.save_registered_to_file()
            bot.request_handled()
            

class UpdateQueue(CommandGroup):
    class MovePrevious(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            if bot.queue.move_prev():
                bot.send_cur_and_next(update)
                bot.last_queue_message.update_contents(bot.queue.str(), update.effective_chat)

    class MoveNext(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            if bot.queue.move_next():
                bot.send_cur_and_next(update)
                bot.last_queue_message.update_contents(bot.queue.str(), update.effective_chat)

    class Refresh(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            if not bot.last_queue_message.message_exists(update.effective_chat):
                update.effective_message.delete()
            bot.last_queue_message.update_contents(bot.queue.str(), update.effective_chat)


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
            bot.request_handled()
            

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
            bot.request_handled()
            

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
            bot.request_handled()


class CollectSubjectChoices(CommandGroup):

    command_parameters = {}

    # These commands (except the last) are executed in a row
    # they collect parameters of subject choices handling
    class CreateNewCollectFile(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().send_choice_file_name)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            subject_name = update.message.text
            if ' ' in subject_name:
                update.effective_chat.send_message(bot.get_language_pack().send_subject_name_without_spaces)
                return
            else:
                CollectSubjectChoices.command_parameters['name'] = subject_name
                CollectSubjectChoices.SetSubjectsRange.handle(update, bot)

    class SetSubjectsRange(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().send_number_range)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            min_range, max_range = parcers.parce_number_range(update.message.text)
            if min_range is None:
                update.effective_chat.send_message(bot.get_language_pack().number_range_incorrect)
            else:
                CollectSubjectChoices.command_parameters['interval'] = (min_range, max_range)
                update.effective_chat.send_message(bot.get_language_pack().number_interval_set)
                

    class SetRepeatableMode(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().set_repeatable_limit)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            limit = parcers.parce_integer(update.message.text)

            if limit is None:
                update.effective_chat.send_message(bot.get_language_pack().value_incorrect)
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

            bot.choice_manager.set_choice_group(name,
                                                [i for i in range(interval[0], interval[1] + 1, 1)],
                                                repeat_limit)
            update.effective_chat.send_message(bot.get_language_pack().finished_choice_manager_creation)


    class Collect(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().send_choice_numbers)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            choices, errors = parcers.parse_positions_list(update.inline_query.query)
            # todo add choice to choice_manager. consider priority limits of choice

    class StopCollect(CommandGroup.Command):
        access_requirement = AccessLevel.ADMIN

        @classmethod
        def handle(self, update, bot):
            bot.choice_manager.current_subject.save_to_excel()
            update.effective_chat.send_message(bot.get_language_pack().choices_collection_stopped)