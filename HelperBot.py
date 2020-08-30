from logger import Logger
from varsaver import VariableSaver
from gdrive_saver import DriveSaver, FolderType
from bot_messages import *
from bot_commands import *
from registered_manager import StudentsRegisteredManager
from students_queue import StudentsQueue
import bot_command_handler

from pathlib import Path
import atexit
import os

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import Chat


class QueueBot:

    command_handler = bot_command_handler.CommandHandler
    last_queue_message = None
    command_requested_answer = None

    def _init_(self, bot_token=None):
        self.logger = Logger()
        self.varsaver = VariableSaver(logger=self.logger)
        self.gdrive_saver = DriveSaver()
        self.registered_manager = StudentsRegisteredManager()
        self.queue = StudentsQueue(self.registered_manager)

        if bot_token is None:
            bot_token = self.get_token()

        self.updater = Updater(bot_token, use_context=True)
        self.init_updater_commands()

        atexit.register(self.save_before_stop)

    def init_updater_commands(self):
        self.updater.dispatcher.add_handler(CommandHandler('i_finished', self._h_i_finished))
        self.updater.dispatcher.add_handler(CommandHandler('remove_me', self._h_remove_me))
        self.updater.dispatcher.add_handler(CommandHandler('add_me', self._h_add_me_to_queue))
        self.updater.dispatcher.add_handler(CommandHandler('start', self._h_start))
        self.updater.dispatcher.add_handler(CommandHandler('stop', self._h_stop))
        self.updater.dispatcher.add_handler(CommandHandler('logs', self._h_show_logs))
        self.updater.dispatcher.add_handler(CommandHandler('get_queue', self._h_check_queue_status))
        self.updater.dispatcher.add_handler(CommandHandler('current_and_next', self._h_get_cur_and_next_students))
        self.updater.dispatcher.add_handler(CommandHandler('new_queue', self._h_create_queue))
        self.updater.dispatcher.add_handler(CommandHandler('new_random_queue', self._h_create_random_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_queue', self._h_edit_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_registered', self._h_edit_registered))
        self.updater.dispatcher.add_handler(CommandHandler('owner', self._h_add_new_owner))
        self.updater.dispatcher.add_handler(CommandHandler('del_owner', self._h_del_owner))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self._h_message_text))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self._h_keyboard_chosen))
        self.updater.dispatcher.add_error_handler(self._h_error)

    def start(self):
        self.logger.log('start')
        self.load_defaults()
        self.updater.start_polling()
        self.updater.idle()

    def save_before_stop(self):
        # clear queue, if it was fully completed
        if self.cur_queue_pos is not None and self.cur_queue_pos == len(self.cur_queue):
            self.queue.clear()

        self.save_queue_to_file()
        self.save_to_cloud()

    def save_to_cloud(self):
        dump_path = self.logger.dump_to_file()
        self.gdrive_saver.update_file_list([dump_path], FolderType.Logs)
        self.gdrive_saver.update_file_list(self.queue.get_save_files() +
                                           self.registered_manager.get_save_files(),
                                           FolderType.Data)

        self.logger.log('saved to cloud')

    def load_from_cloud(self):
        self.gdrive_saver.get_file_list(self.queue.get_save_files() + self.registered_manager.get_save_files())

    # loads default values from external file
    def load_defaults(self):
        self.load_from_cloud()

        self.registered_manager.load_file(self.varsaver)
        self.queue.load_file(self.varsaver)

        self.logger.log('loaded data')

    def save_registered_to_file(self):
        self.registered_manager.save_to_file(self.varsaver)
        self.gdrive_saver.update_file_list(self.registered_manager.get_save_files(), FolderType.Data)

    def save_queue_to_file(self):
        self.queue.save_to_file(self.varsaver)

    def get_token(self, path=None):
        if path is None:
            token = os.environ.get('TELEGRAM_TOKEN')
        else:
            token = self.varsaver.load(path)

        if token is None:
            self.logger.log('Fatal error: token is empty')
            raise ValueError('Fatal error: token is empty')

        return token


    # command handlers
    def _h_keyboard_chosen(self, update, context):
        self.command_handler.handle(update.callback_query.data, update, self)
        update.callback_query.answer()

    def _h_message_text(self, update, context):

        if update.effective_chat.type != Chat.PRIVATE or self.command_requested_answer is None:
            return

        self.logger.log(self.command_requested_answer.str())
        self.command_requested_answer.handle_request(update, self)


    def _h_add_new_owner(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            if self.command_requested_answer is None:
                update.message.reply_text(msg_get_user_message)
                self.command_requested_answer = ManageUsers.AddAdmin
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_del_owner(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            if msg_request[0] is None:
                update.message.reply_text(msg_get_user_message)
                msg_request = (update.message.from_user.id, self.request_codes[(self.cmd_del_owner, None)])
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_start(self, update, context):
        if len(self.owners_table) == 0:
            self.owners_table[update.message.from_user.id] = 0
            update.message.reply_text('Первый владелец добавлен - ' + update.message.from_user.username)

            for admin in update.effective_chat.get_administrators():
                self.owners_table[admin.user.id] = 1

            self.save_owners_to_file()
            update.effective_chat.send_message('Администраторы добавлены')

        elif self.check_user_have_access(update.effective_user.id, self.owners_table):
            update.message.reply_text('Бот уже запущен.')

    def _h_stop(self, update, context):
        if self.check_user_have_access(update.effective_user.id, self.owners_table):
            update.message.reply_text('Бот остановлен, и больше не принимает команд')
            self.updater.stop()
            exit()

    def _h_show_logs(self, update, context):
        if self.check_user_have_access(update.effective_user.id, self.owners_table, 0):

            trimmed_msg = self.logger.get_logs()[-4096:]
            if len(trimmed_msg) >= 4096: trimmed_msg = trimmed_msg[trimmed_msg.index('\n'):]

            update.effective_chat.send_message(trimmed_msg)

    def _h_create_random_queue(self, update, context):
        if self.check_user_have_access(update.effective_user.id, self.owners_table):
            if len(self.cur_queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',
                                                   reply_markup=keyboard_reply_create_random_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',
                                                   reply_markup=keyboard_reply_create_random_queue)
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_create_queue(self, update, context):
        if self.check_user_have_access(update.effective_user.id, self.owners_table):
            if len(self.cur_queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',
                                                   reply_markup=keyboard_reply_create_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',
                                                   reply_markup=keyboard_reply_create_queue)
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_edit_queue(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            update.message.reply_text('Редактирование очереди', reply_markup=keyboard_modify_queue)
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_edit_registered(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            update.effective_chat.send_message('Редактирование пользователей', reply_markup=keyboard_modify_registered)
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_check_queue_status(self, update, context):
        if len(self.cur_queue) == 0:
            if self.check_user_have_access(update.effective_user.id, self.owners_table):
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?', reply_markup=keyboard_reply_create_queue)
            else:
                update.effective_chat.send_message('Очереди нет.')
        else:
            msg = update.effective_chat.send_message(self.queue.get_string(), reply_markup=keyboard_move_queue)
            if update.effective_chat.type != Chat.PRIVATE:
                self.last_queue_message = msg

            self.logger.log('user {0} in {1} chat requested queue'.format(update.effective_user.id, update.effective_chat.type))

    def _h_get_cur_and_next_students(self, update, context):
        update.effective_chat.send_message(
            self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))

    def _h_i_finished(self, update, context):
        cur_user_id = update.effective_user.id
        if cur_user_id in self.registered_students.keys():
            if self.cur_queue_pos >= 0 and self.cur_queue_pos < len(self.cur_queue):
                if cur_user_id == self.cur_queue[self.cur_queue_pos][1] or \
                        self.similar(self.registered_students[cur_user_id], self.cur_queue[self.cur_queue_pos][0]):
                    self.cur_queue_pos += 1
                    update.effective_chat.send_message(
                        self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))
                else:
                    update.message.reply_text('{0}, вы не сдаете сейчас.'.format(self.registered_students[cur_user_id]))
            else:
                update.message.reply_text('{0}, вы не сдаете сейчас.'.format(self.registered_students[cur_user_id]))
        else:
            update.message.reply_text(msg_unknown_user)

        self.refresh_last_queue_msg()
        self.save_bot_state_to_file()
        self.logger.log('finished {0} - {1}'.format(cur_user_id, self.cur_queue[self.cur_queue_pos]))

    def _h_remove_me(self, update, context):

        cur_user_id = update.effective_user.id

        if cur_user_id in self.registered_students:
            stud = (self.registered_students[cur_user_id], cur_user_id)
        else:
            stud = (update.effective_user.full_name, None)

        if self.delete_stud_from_queue(stud):
            self.refresh_last_queue_msg()
            self.save_queue_to_file()
            self.save_bot_state_to_file()

            update.message.reply_text('Вы удалены из очереди'.format(self.registered_students[cur_user_id]))
            self.logger.log('removed {0} - {1} '.format(self.registered_students[cur_user_id], cur_user_id))

        else:
            update.message.reply_text('Вы не найдены в очереди')

    def _h_add_me_to_queue(self, update, context):
        cur_user_id = update.effective_user.id

        if (not cur_user_id is None) and (cur_user_id in self.registered_students):
            stud = (self.registered_students[cur_user_id], cur_user_id)
            self.delete_stud_from_queue(stud)
            self.cur_queue.append_user(stud)
        else:
            self.cur_queue.append_user((update.effective_user.full_name, None))

        update.message.reply_text('Вы записаны в очередь')

        self.refresh_last_queue_msg()
        self.save_queue_to_file()
        self.logger.log('added {0} - {1} '.format(*self.cur_queue[-1]))

    # returns True if someone was deleted
    def delete_stud_from_queue(self, del_student):
        delete = []
        for i in range(len(self.cur_queue)):
            stud = self.cur_queue[i]

            appended = False
            if stud[1] == None and stud[0] == del_student[0]:
                delete.append(stud)
                appended = True
            elif stud[1] == del_student[1]:
                delete.append(stud)
                appended = True

            if appended and i < self.cur_queue_pos:
                self.cur_queue_pos -= 1

        if len(delete) > 0:
            for s in delete:
                self.cur_queue.remove(s)
            return True

        return False

    def _h_error(self, update, context):
        print('Error: {0}'.format(context.error))
        self.logger.log(context.error)
        self.logger.save_to_cloud()

    def _delete_cur_queue(self):
        self.cur_queue = []
        self.cur_queue_pos = None

    def _refresh_cur_queue_ids(self):
        for idx in range(len(self.cur_queue)):
            i = self.cur_queue[idx][0]  # name of student in i

            if i in self.registered_students.values():
                self.cur_queue[idx] = (i, self.get_id_by_name(self.registered_students, i))
            else:
                self.cur_queue[idx] = (i, None)

    def refresh_last_queue_msg(self):
        if not self.last_queue_message is None:
            new_text = self.get_queue_str(self.cur_queue, self.cur_queue_pos)
            if self.last_queue_message.text != new_text:
                self.last_queue_message = self.last_queue_message.edit_text(new_text, reply_markup=keyboard_move_queue)

    # Администрирование

    # Передача прав редактирования
    def set_bot_user(self, user_id, user_name):
        self.registered_students[user_id] = user_name
        self.save_registered_to_file()

    def add_new_bot_owner(self, user_id, new_owner_id, new_access_level=None):
        if self.check_user_have_access(user_id, self.owners_table):
            if new_access_level >= 0:
                if new_access_level == None:
                    self.owners_table[new_owner_id] = self.owners_table[user_id] + 1
                    self.save_owners_to_file()
                    return None
                elif self.owners_table[user_id] < new_access_level:
                    self.owners_table[new_owner_id] = new_access_level
                    self.save_owners_to_file()
                    return None

                return msg_permission_denied
            else:
                return msg_code_not_valid
        else:
            return msg_permission_denied

    def del_bot_owner(self, user_id, del_owner_id):
        if self.check_user_have_access(user_id, self.owners_table):
            try:
                if self.owners_table[user_id] < self.owners_table[del_owner_id]:
                    del self.owners_table[del_owner_id]
                    self.save_owners_to_file()
                    return None
                else:
                    return msg_permission_denied
            except ValueError:
                return msg_owner_not_found
        else:
            return msg_permission_denied

    def check_user_have_access(self, user_id, access_levels_dict, access_level=1):
        if user_id in access_levels_dict:
            if access_levels_dict[user_id] <= access_level:
                return True
        return False
