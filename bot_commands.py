from bot_messages import *
from bot_keyboards import *

# TODO add request forming here


class CommandGroup:
    class Command:
        @classmethod
        def str(cls):
            return super().__name__ + ':' + cls.__name__

        def handle(self, update, queue):
            pass

        def handle_request(self, update, bot):
            pass


class ModifyQueue(CommandGroup):

    class CreateSimple(CommandGroup.Command):
        def handle(self, update, queue):
            queue.clear()
            update.effective_chat.send_message(msg_set_students)
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

        def handle_request(self, update, bot):
            if '\n' in update.message.text:
                names = update.message.text.split('\n')
            else:
                names = [update.message.text]

            names = [i for i in names if not i == '']

            update.effective_chat.send_message('Студенты установлены')

            bot.queue.generate_simple(names)

            update.effective_chat.send_message(queue.get_string(), reply_markup=keyboard_move_queue)

            bot.save_queue_to_file()
            bot.refresh_last_queue_msg()

    class CreateRandom(CommandGroup.Command):
        def handle(self, update, queue):
            queue.clear()
            update.effective_chat.send_message(msg_set_students)
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

    class Cancel(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_message.delete()

    class ShowList(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_chat.send_message(queue.get_string())

    class SetStudents(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_chat.send_message(msg_set_students)
            # msg_request = (update.effective_user.id, self.request_codes[(self.cmd_create_queue, self.cmd_args_create_queue[0])])

    class SetQueuePosition(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_chat.send_message(queue.get_string())
            update.effective_chat.send_message('Пришлите номер новой позциции')
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

    class ClearList(CommandGroup.Command):
        def handle(self, update, queue):
            queue.clear()
            update.effective_chat.send_message('Очередь удалена')

    class MoveStudentToEnd(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_chat.send_message(queue.get_string())
            update.effective_chat.send_message('Пришлите номер студента в очереди')
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

    class RemoveStudent(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_chat.send_message(queue.get_string())
            update.effective_chat.send_message('Пришлите номер студентов в очереди через пробел')
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

    class SetStudentPosition(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_chat.send_message(queue.get_string())
            update.effective_chat.send_message('Пришлите номер студента в очереди и через пробел номер новой позиции')
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

    class AddStudent(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_chat.send_message(queue.get_string())
            update.effective_chat.send_message('Пришлите имя нового студента, он будет добавлен в конец очереди')
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

    class SwapStudents(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_chat.send_message(queue.get_string())
            update.effective_chat.send_message('Пришлите номера двух студентов через пробел')
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])


class ModifyRegistered(CommandGroup):
    class ShowListUsers(CommandGroup.Command): # 0
        def handle(self, update, queue):
            update.effective_chat.send_message(queue.students_manager.get_users_str())

    class AddListUsers(CommandGroup.Command): # 1
        def handle(self, update, queue):
            update.effective_chat.send_message(msg_set_registered_students)
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

    class AddUser(CommandGroup.Command): # 2
        def handle(self, update, queue):
            update.effective_chat.send_message(msg_get_user_message)
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

    class RemoveUser(CommandGroup.Command): # 3
        def handle(self, update, queue):
            update.effective_chat.send_message(msg_del_registered_students)
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])

    class RenameAllUsers(CommandGroup.Command):
        def handle(self, update, queue):
            update.effective_chat.send_message('Введите список новых имен для всех пользователей в порядке их расположения')
            # msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])


class UpdateQueue(CommandGroup):
    class MovePrevious(CommandGroup.Command):
        def handle(self, update, queue):
            if queue.move_prev():
                update.effective_chat.send_message(queue.get_cur_and_next_str())
                update.callback_query.edit_message_text(queue.get_string(), reply_markup=keyboard_move_queue)

    class MoveNext(CommandGroup.Command):
        def handle(self, update, queue):
            if queue.move_next():
                update.effective_chat.send_message(queue.get_cur_and_next_str())
                update.callback_query.edit_message_text(queue.get_string(), reply_markup=keyboard_move_queue)

    class Refresh(CommandGroup.Command):
        def handle(self, update, queue):
            new_queue_str = queue.get_string()
            if update.callback_query.message.text != new_queue_str:
                update.callback_query.edit_message_text(new_queue_str, reply_markup=keyboard_move_queue)


class ManageOwners(CommandGroup):
    class Add(CommandGroup.Command):
        def handle_request(self, update, queue):
            pass

    class Remove(CommandGroup.Command):
        def handle_request(self, update, queue):
            pass
