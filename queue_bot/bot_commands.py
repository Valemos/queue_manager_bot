class CommandGroup:
    class Command:

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
        @classmethod
        def handle(cls, update, bot):
            bot.queue.clear()
            update.effective_chat.send_message(bot.get_language_pack().enter_students_list)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            students = bot.queue.parse_students(update.message.text)
            bot.queue.generate_simple(students)
            bot.refresh_last_queue_msg(update)
            update.effective_chat.send_message(bot.get_language_pack().students_set)
            bot.save_queue_to_file()


    class CreateRandom(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            bot.queue.clear()
            update.effective_chat.send_message(bot.get_language_pack().enter_students_list)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            students = bot.queue.parse_students(update.message.text)
            bot.queue.generate_random(students)
            bot.refresh_last_queue_msg(update)
            update.effective_chat.send_message(bot.get_language_pack().students_set)
            bot.save_queue_to_file()


    class CreateRandomFromRegistered(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            import random
            new_queue_students = bot.registered_manager.get_users()
            random.shuffle(new_queue_students)
            bot.queue.set_students(new_queue_students)
            bot.last_queue_message.update_contents(bot.queue.str())
            bot.save_queue_to_file()

    class Cancel(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_message.delete()


    class ShowList(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())


    class SetStudents(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().enter_students_list)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            ModifyQueue.CreateSimple.handle_request(update, bot)


    class SetQueuePosition(CommandGroup.Command):
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
                

    class ClearList(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            bot.queue.clear()
            update.effective_chat.send_message(bot.get_language_pack().queue_deleted)


    class MoveStudentToEnd(CommandGroup.Command):
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


    class RemoveStudentsList(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_numbers_with_space)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            positions, errors = bot.queue.parse_positions_list(update.message.text)
            bot.queue.remove_by_index([i - 1 for i in positions])
            bot.refresh_last_queue_msg(update)
            bot.save_queue_to_file()

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values.format(', '.join(errors)))
            if len(positions) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_deleted)


    class SetStudentPosition(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.str())
            update.effective_chat.send_message(bot.get_language_pack().send_student_number_and_new_position)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            positions, errors = bot.queue.parse_positions_list(update.message.text)

            if len(positions) >= 2:
                if bot.queue.move_to_index(positions[0]-1, positions[1]-1):
                    update.effective_chat.send_message(bot.get_language_pack().students_moved)
            elif len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)
            else:
                update.effective_chat.send_message(bot.get_language_pack().error_in_values)

            bot.save_queue_to_file()
            bot.refresh_last_queue_msg(update)
            

    class AddStudent(CommandGroup.Command):
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
            bot.save_queue_to_file()
            bot.refresh_last_queue_msg(update)
            

    class SwapStudents(CommandGroup.Command):
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
                bot.save_queue_to_file()
                bot.refresh_last_queue_msg(update)
                

class ModifyRegistered(CommandGroup):
    class ShowListUsers(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.registered_manager.get_users_str())


    class AddListUsers(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().set_registered_students)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            new_users, errors = bot.registered_manager.parse_users(update.effective_message.text)
            bot.registered_manager.append_users(new_users)

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values.format('\n'.join(errors)))
            if len(new_users) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_added)

            bot.save_registered_to_file()


    class AddUser(CommandGroup.Command):
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
            

    class RenameAllUsers(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.get_language_pack().enter_new_list_in_order)
            bot.set_request(cls)

        def handle_request(cls, update, bot):
            names = bot.registered_manager.parse_names(update.message.text)
            if len(names) <= len(bot.registered_manager):
                for i in range(len(names)):
                    bot.registered_manager.rename(i, names[i])
            else:
                update.effective_chat.send_message(bot.get_language_pack().names_more_than_users)


    class RemoveListUsers(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.registered_manager.get_users_str())
            update.effective_chat.send_message(bot.get_language_pack().del_registered_students)
            bot.set_request(cls)

        @classmethod
        def handle_request(cls, update, bot):
            # parse function is inside of queue object
            delete_indexes, errors = bot.queue.parse_positions_list(update.message.text, len(bot.registered_manager))
            bot.registered_manager.remove_by_index([i - 1 for i in delete_indexes])

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values.format('\n'.join(errors)))
            if len(delete_indexes) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_deleted)

            bot.save_registered_to_file()
            

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
        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                if bot.registered_manager.set_admin(update.effective_user.id):
                    update.message.reply_text(bot.get_language_pack().admin_set)
            else:
                update.message.reply_text(bot.get_language_pack().was_not_forwarded)
            

    class RemoveAdmin(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                if bot.registered_manager.set_user(update.message.forward_from.id):
                    update.message.reply_text(bot.get_language_pack().admin_deleted)
            else:
                update.message.reply_text(bot.get_language_pack().was_not_forwarded)
            

    class AddUsersList(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            users, errors = bot.registered_manager.parse_users()
            bot.registered_manager.append_users(users)

            if len(errors) > 0:
                update.effective_chat.send_message(bot.get_language_pack().error_in_this_values('\n'.join(errors)))
            if len(users) > 0:
                update.effective_chat.send_message(bot.get_language_pack().users_added)

            bot.save_registered_to_file()
