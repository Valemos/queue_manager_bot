from HelperBot import QueueBot
from bot_messages import *
from bot_keyboards import *


class CommandGroup:
    class Command:
        @classmethod
        def str(cls):
            return super().__name__ + ':' + cls.__name__
        
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
            update.effective_chat.send_message(msg_set_students)
            bot.command_requested_answer = cls

        @classmethod
        def handle_request(cls, update, bot):
            students = bot.queue.parse_students(update.message.text)
            bot.queue.generate_simple(students)

            update.effective_chat.send_message('Студенты установлены')
            update.effective_chat.send_message(bot.queue.get_string(), reply_markup=keyboard_move_queue)

            bot.save_queue_to_file()
            bot.refresh_last_queue_msg()
            bot.command_requested_answer = None

    class CreateRandom(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            bot.queue.clear()
            update.effective_chat.send_message(msg_set_students)
            bot.command_requested_answer = cls

        @classmethod
        def handle_request(cls, update, bot):
            students = bot.queue.parse_students(update.message.text)
            bot.queue.generate_random(students)

            update.effective_chat.send_message('Студенты установлены')
            update.effective_chat.send_message(bot.queue.get_string(), reply_markup=keyboard_move_queue)

            bot.save_queue_to_file()
            bot.refresh_last_queue_msg()
            bot.command_requested_answer = None

    class Cancel(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_message.delete()

    class ShowList(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.get_string())

    class SetStudents(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(msg_set_students)
            bot.command_requested_answer = cls

        @classmethod
        def handle_request(cls, update, bot):
            ModifyQueue.CreateSimple.handle_request(update, bot)

    class SetQueuePosition(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.get_string())
            update.effective_chat.send_message('Пришлите номер новой позциции')
            bot.command_requested_answer = cls

        @classmethod
        def handle_request(cls, update, bot):
            try:
                new_index = int(update.message.text)
                assert 0 < new_index <= len(bot.queue)
                bot.queue.queue_pos = new_index - 1

                update.effective_chat.send_message('Позиция установлена')
            except (ValueError, AssertionError):
                update.effective_chat.send_message(msg_error_in_values)
            finally:
                bot.save_bot_state_to_file()
                bot.refresh_last_queue_msg()
                bot.command_requested_answer = None

    class ClearList(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            bot.queue.clear()
            update.effective_chat.send_message('Очередь удалена')

    class MoveStudentToEnd(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.get_string())
            update.effective_chat.send_message('Пришлите номер студента в очереди')
            bot.command_requested_answer = cls

        @classmethod
        def handle_request(cls, update, bot):
            try:
                move_pos = int(update.message.text) - 1
                if move_pos >= len(bot.queue) or move_pos < 0:
                    bot.command_requested_answer = None
                    return

                bot.queue.move_to_end(move_pos)
                bot.refresh_last_queue_msg()
                update.effective_chat.send_message('Студент добавлен в конец')
            except ValueError:
                update.effective_chat.send_message('Не номер из очереди. Отмена операции')
            finally:
                bot.command_requested_answer = None

    class RemoveStudentsList(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.get_string())
            update.effective_chat.send_message('Пришлите номер студентов в очереди через пробел')
            bot.command_requested_answer = cls

        @classmethod
        def handle_request(cls, update, bot):
            indexes, errors = bot.queue.parse_index_list(update.message.text)
            bot.queue.remove_by_index(indexes)

            if len(errors) > 0:
                update.effective_chat.send_message('Ошибка возникла в этих значениях:\n' + ' '.join(errors))
            if len(indexes) > 0:
                update.effective_chat.send_message('Пользователи удалены')

            bot.save_queue_to_file()
            bot.refresh_last_queue_msg()
            bot.command_requested_answer = None

    class SetStudentPosition(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.get_string())
            update.effective_chat.send_message('Пришлите номер студента в очереди и через пробел номер новой позиции')
            bot.command_requested_answer = cls

        @classmethod
        def handle_request(cls, update, bot):
            indexes, errors = bot.queue.parse_index_list(update.message.text)

            if len(indexes) >= 2:
                bot.queue.move_student_to_index(indexes[0], indexes[1])
                update.effective_chat.send_message('Студент перемещен')
            elif len(errors) > 0:
                update.effective_chat.send_message(msg_error_in_values)
            else:
                update.effective_chat.send_message(msg_error_in_values)

            bot.save_queue_to_file()
            bot.refresh_last_queue_msg()
            bot.command_requested_answer = None

    class AddStudent(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.get_string())
            update.effective_chat.send_message('Пришлите имя нового студента, он будет добавлен в конец очереди')
            bot.command_requested_answer = cls

        @classmethod
        def handle_request(cls, update, bot):
            if bot.queue.append_by_name(update.message.text):
                bot.logger.log('student set ' + update.message.text + ' found in registered')
            else:
                bot.logger.log('student set ' + update.message.text + ' not found')

            update.effective_chat.send_message('Студент установлен')
            bot.save_queue_to_file()
            bot.refresh_last_queue_msg()
            bot.command_requested_answer = None

    class SwapStudents(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.get_string())
            update.effective_chat.send_message('Пришлите номера двух студентов через пробел')
            bot.command_requested_answer = cls
        
        @classmethod
        def handle_request(cls, update, bot):
            try:
                user_str = update.message.text.split(' ')
                cur_pos, swap_pos = int(user_str[0]) - 1, int(user_str[1]) - 1

                if 0 <= cur_pos < len(bot.queue) and 0 <= swap_pos < len(bot.queue):
                    bot.queue.swap(cur_pos, swap_pos)
                    update.effective_chat.send_message('Студенты перемещены')
                else:
                    update.effective_chat.send_message(msg_error_in_values)

            except ValueError:
                update.effective_chat.send_message(msg_error_in_values)
            finally:
                bot.save_queue_to_file()
                bot.refresh_last_queue_msg()
                bot.command_requested_answer = None


class ModifyRegistered(CommandGroup):
    class ShowListUsers(CommandGroup.Command): # 0
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(bot.queue.registered_manager.get_users_str())

    class AddListUsers(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(msg_set_registered_students)
            bot.command_requested_answer = cls

    class AddUser(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message(msg_get_user_message)
            bot.command_requested_answer = cls

        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                bot.registered_manager.append_new_user(update.message.forward_from.full_name, update.message.forward_from.id)
                update.message.reply_text(msg_user_register_successfull)
            else:
                update.message.reply_text(msg_was_not_forwarded)

            bot.save_queue_to_file()
            bot.refresh_last_queue_msg()
            bot.command_requested_answer = None

    class RenameAllUsers(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            update.effective_chat.send_message('Введите список новых имен для всех пользователей в порядке их расположения')
            bot.command_requested_answer = cls

    class RemoveListUsers(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            delete_indexes, errors = bot.queue.parse_index_list(update.message.text)
            bot.registered_manager.remove_by_index([i - 1 for i in delete_indexes])

            if len(errors) > 0:
                update.effective_chat.send_message('Ошибка в этих значениях:\n' + '\n'.join(errors))
            if len(delete_indexes) > 0:
                update.effective_chat.send_message('Пользователи удалены')

            bot.save_queue_to_file()
            bot.refresh_last_queue_msg()
            bot.command_requested_answer = None


class UpdateQueue(CommandGroup):
    class MovePrevious(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            if bot.queue.move_prev():
                update.effective_chat.send_message(bot.queue.get_cur_and_next_str())
                update.callback_query.edit_message_text(bot.queue.get_string(), reply_markup=keyboard_move_queue)

    class MoveNext(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            if bot.queue.move_next():
                update.effective_chat.send_message(bot.queue.get_cur_and_next_str())
                update.callback_query.edit_message_text(bot.queue.get_string(), reply_markup=keyboard_move_queue)

    class Refresh(CommandGroup.Command):
        @classmethod
        def handle(cls, update, bot):
            new_queue_str = bot.queue.get_string()
            if update.callback_query.message.text != new_queue_str:
                update.callback_query.edit_message_text(new_queue_str, reply_markup=keyboard_move_queue)


class ManageUsers(CommandGroup):
    class AddAdmin(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                return_msg = bot.registered_manager.add_admin(update.effective_user.id)
                if return_msg is not None:
                    update.message.reply_text(return_msg)
                else:
                    update.message.reply_text('Владелец успешно установлен')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано, отмена')
            bot.command_requested_answer = None

    class RemoveAdmin(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot):
            if update.message.forward_from is not None:
                return_msg = bot.registered_manager.set_user(update.message.forward_from.id)
                if return_msg is not None:
                    update.message.reply_text(return_msg)
                else:
                    update.message.reply_text('Владелец успешно удален')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано')
            bot.command_requested_answer = None

    class AddUsersList(CommandGroup.Command):
        @classmethod
        def handle_request(cls, update, bot: QueueBot):
            users, errors = bot.registered_manager.parse_users()
            bot.registered_manager.append_users(users)

            if len(errors) > 0:
                update.effective_chat.send_message('Ошибка возникла в этих строках:\n' + '\n'.join(errors))
            if len(users) > 0:
                update.effective_chat.send_message('Пользователи добавлены')

            bot.save_registered_to_file()
            bot.command_requested_answer = None
