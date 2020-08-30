from logger import Logger
from varsaver import VariableSaver
from gdrive_saver import DriveSaver, FolderType
from bot_messages import *
from bot_commands import *
from registered_manager import RegisteredManager
from students_queue import StudentsQueue
import bot_command_handler

from pathlib import Path
import atexit
import os

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import Chat

class QueueBot:
    command_handler = bot_command_handler.CommandHandler

    def _init_(self, bot_token=None):

        self.file_name_owner = Path('data/owners.data')
        self.file_name_registered = Path('data/registered.data')
        self.file_name_queue = Path('data/queue.data')
        self.file_name_bot_state = Path('data/bot_state.data')

        self.logger = Logger()
        self.varsaver = VariableSaver(logger=self.logger)
        self.gdrive_saver = DriveSaver()
        self.registered_manager = RegisteredManager()

        if bot_token is None:
            bot_token = self.get_token()

        if bot_token is None:
            self.logger.log('Fatal error: token is empty')

        self.updater = Updater(bot_token, use_context=True)
        self.init_updater_commands()

        self.command_requested_answer = None
        self.last_queue_message = None

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
        if self.cur_queue_pos is not None and self.cur_queue_pos == len(self.cur_queue):
            self.delete_cur_queue()

        self.save_queue_to_file()
        self.save_bot_state_to_file()
        self.save_all_to_cloud()

    def save_all_to_cloud(self):
        dump_path = self.logger.dump_to_file()
        self.gdrive_saver.update_file_list([dump_path], FolderType.Logs)

        self.gdrive_saver.update_file_list([
            self.file_name_owner,
            self.file_name_registered,
            self.file_name_queue,
            self.file_name_bot_state],
            FolderType.Data)

        self.logger.log('saved to cloud')

    def load_from_cloud(self):

        self.gdrive_saver.get_file_list([
            self.file_name_registered,
            self.file_name_owner,
            self.file_name_bot_state,
            self.file_name_registered,
            self.file_name_queue],
            new_folder=self.file_name_queue.parent)

    # loads default values from external file
    def load_defaults(self):
        self.load_from_cloud()
        self.load_registered_from_file()
        self.load_owners_from_file()
        self.load_queue_from_file()
        self.load_bot_state_from_file()

        self.logger.log('loaded data')

    def load_owners_from_file(self):
        self.owners_table = self.varsaver.load(self.file_name_owner)
        if self.owners_table is None:
            self.owners_table = {}

    def load_registered_from_file(self):
        self.registered_manager.get_registered_from_file()

    def load_queue_from_file(self):
        self.cur_queue = self.varsaver.load(self.file_name_queue)
        if self.cur_queue is None: self.cur_queue = []

    def load_bot_state_from_file(self):
        state = self.varsaver.load(self.file_name_bot_state)

        if not state is None:
            self.cur_queue_pos = state['cur_queue_pos']
        else:
            self.cur_queue_pos = 0

    def save_bot_state_to_file(self):
        self.varsaver.save({'cur_queue_pos': self.cur_queue_pos}, self.file_name_bot_state)

    def save_owners_to_file(self):
        self.varsaver.save(self.owners_table, self.file_name_owner)
        self.gdrive_saver.update_file_list([self.file_name_owner])

    def save_registered_to_file(self):
        self.varsaver.save(self.registered_students, self.file_name_registered)
        self.gdrive_saver.update_file_list([self.file_name_registered])

    def save_queue_to_file(self):
        self.varsaver.save(self.cur_queue, self.file_name_queue)

    def get_token(self, path=None):
        return os.environ.get('TELEGRAM_TOKEN')

    def _h_keyboard_chosen(self, update, context):
        self.command_handler.handle_command(update.callback_query.data)
        update.callback_query.answer()

    def _h_message_text(self, update, context):

        if update.message.from_user.id != msg_request[0] or \
                update.effective_chat.type != Chat.PRIVATE:
            return

        self.logger.log(msg_request)

        if msg_request[1] == 0 or msg_request[1] == 1:

            if '\n' in update.message.text:
                self.cur_students_list = update.message.text.split('\n')
            else:
                self.cur_students_list = [update.message.text]

            self.cur_students_list = [i for i in self.cur_students_list if not i == '']

            update.effective_chat.send_message('Студенты установлены')

            if msg_request[1] == 0:
                self.cur_queue = self.gen_queue(self.cur_students_list)
                self.cur_queue_pos = 0
            elif msg_request[1] == 1:
                self.cur_queue = self.gen_random_queue(self.cur_students_list)
                self.cur_queue_pos = 0

            update.effective_chat.send_message(self.get_queue_str(self.cur_queue), reply_markup=self.keyb_move_queue)

            self.save_queue_to_file()
            self.refresh_last_queue_msg()
            msg_request = (None, None)

        elif msg_request[1] == 2:
            if update.message.forward_from is not None:
                return_msg = self.add_new_bot_owner(update.effective_user.id, update.message.forward_from.id, 1)
                if return_msg is not None:
                    update.message.reply_text(return_msg)
                else:
                    update.message.reply_text('Владелец успешно установлен')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано, отмена')
            msg_request = (None, None)

        elif msg_request[1] == 3:
            if update.message.forward_from is not None:
                return_msg = self.del_bot_owner(update.effective_user.id, update.message.forward_from.id)
                if return_msg is not None:
                    update.message.reply_text(return_msg)
                else:
                    update.message.reply_text('Владелец успешно удален')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано')

            msg_request = (None, None)

        elif msg_request[1] == 4:
            try:
                move_pos = int(update.message.text) - 1
                if move_pos >= len(self.cur_queue) or move_pos < 0:
                    msg_request = (None, None)
                    return

                self.cur_queue.append(self.cur_queue.pop(move_pos))
                self.refresh_last_queue_msg()
                update.effective_chat.send_message('Студент добавлен в конец')
            except ValueError:
                update.effective_chat.send_message('Не номер из очереди. Отмена операции')
            finally:
                msg_request = (None, None)

        elif msg_request[1] == 8:
            del_users_str = []
            if ' ' in update.message.text:
                del_users_str = update.message.text.split(' ')
            else:
                del_users_str = [update.message.text]

            err_list = []
            del_users = []

            for pos_str in del_users_str:
                try:
                    pos = int(pos_str)
                    if pos > 0 and pos <= len(self.cur_queue):
                        del_users.append(pos)
                    else:
                        err_list.append(str(pos))
                except Exception:
                    err_list.append(pos_str)

            for el in [self.cur_queue[i - 1] for i in del_users]:
                self.cur_queue.remove(el)

            if len(err_list) > 0: update.effective_chat.send_message(
                'Ошибка возникла в этих значениях:\n' + ' '.join(err_list))
            if len(del_users) > 0: update.effective_chat.send_message('Пользователи удалены')

            self.save_queue_to_file()
            self.refresh_last_queue_msg()
            msg_request = (None, None)

        elif msg_request[1] == 9:
            try:
                user_str = update.message.text.split(' ')
                cur_pos, set_pos = int(user_str[0]) - 1, int(user_str[1]) - 1

                assert cur_pos >= 0 and cur_pos < len(self.cur_queue) and \
                       set_pos >= 0 and set_pos < len(self.cur_queue)

                self.cur_queue.insert(set_pos, self.cur_queue.pop(cur_pos))
                update.effective_chat.send_message('Студент перемещен')

                self.save_queue_to_file()
                self.refresh_last_queue_msg()

            except Exception:
                update.effective_chat.send_message(msg_error_in_values)
            finally:
                msg_request = (None, None)

        elif msg_request[1] == 10:
            self.cur_queue.append(self.find_similar(update.message.text))
            self.logger.log('student set ' + str(self.cur_queue[-1]))
            update.effective_chat.send_message('Студент установлен')

            self.save_queue_to_file()
            self.refresh_last_queue_msg()
            msg_request = (None, None)

        elif msg_request[1] == 11:
            try:
                user_str = update.message.text.split(' ')
                cur_pos, swap_pos = int(user_str[0]) - 1, int(user_str[1]) - 1

                assert cur_pos >= 0 and cur_pos < len(self.cur_queue) and \
                       swap_pos >= 0 and swap_pos < len(self.cur_queue)

                self.cur_queue[cur_pos], self.cur_queue[swap_pos] = self.cur_queue[swap_pos], self.cur_queue[cur_pos]
                update.effective_chat.send_message('Студенты перемещены')

            except Exception:
                update.effective_chat.send_message(msg_error_in_values)
            finally:
                self.save_queue_to_file()
                self.refresh_last_queue_msg()
                msg_request = (None, None)

        elif msg_request[1] == 12:
            try:
                new_index = int(update.message.text)
                self.cur_queue_pos = new_index - 1
                update.effective_chat.send_message('Позиция установлена')
            except Exception:
                update.effective_chat.send_message(msg_error_in_values)
            finally:
                self.save_bot_state_to_file()
                self.refresh_last_queue_msg()
                msg_request = (None, None)


        elif msg_request[1] == 5:  # add list
            new_users_str_lines = []
            if '\n' in update.message.text:
                new_users_str_lines = update.message.text.split('\n')
            else:
                new_users_str_lines = [update.message.text]

            err_list = []
            new_users = []

            for line in new_users_str_lines:
                try:
                    user_temp = line.split('-')
                    user_temp = (user_temp[0], int(user_temp[1]))

                    new_users.append(user_temp)
                except Exception:
                    err_list.append(line)

            for u in new_users:
                self.set_bot_user(u[1], u[0])

            if len(err_list) > 0: update.effective_chat.send_message(
                'Ошибка возникла в этих строках:\n' + '\n'.join(err_list))
            if len(new_users) > 0: update.effective_chat.send_message('Пользователи добавлены')

            self.save_queue_to_file()
            self.refresh_last_queue_msg()
            msg_request = (None, None)

        elif msg_request[1] == 6:  # add one
            if update.message.forward_from is not None:
                self.set_bot_user(update.message.forward_from.id, update.message.forward_from.full_name)
                update.message.reply_text('Пользователь зарегистрирован')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано, отмена')

            self.save_queue_to_file()
            self.refresh_last_queue_msg()
            msg_request = (None, None)

        elif msg_request[1] == 7:  # del list
            del_users_str = []
            if ' ' in update.message.text:
                del_users_str = update.message.text.split(' ')
            else:
                del_users_str = [update.message.text]

            err_list = []
            del_users = []

            for pos_str in del_users_str:
                try:
                    pos = int(pos_str)
                    if pos > 0 and pos <= len(self.registered_students):
                        del_users.append(pos)
                    else:
                        err_list.append(str(pos))

                except Exception:
                    err_list.append(pos_str)

            all_user_keys = list(self.registered_students.keys())
            delete_keys = set([all_user_keys[i - 1] for i in del_users])

            for i in delete_keys:
                del self.registered_students[i]

            if len(err_list) > 0: update.effective_chat.send_message('Ошибка в этих значениях:\n' + '\n'.join(err_list))
            if len(del_users) > 0: update.effective_chat.send_message('Пользователи удалены')

            self.save_queue_to_file()
            self.refresh_last_queue_msg()
            msg_request = (None, None)

    def _h_add_new_owner(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            if msg_request[0] is None:
                update.message.reply_text(msg_get_user_message)
                msg_request = (update.message.from_user.id, self.request_codes[(self.cmd_set_owner, None)])
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
                                                   reply_markup=self.keyb_reply_create_random_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',
                                                   reply_markup=self.keyb_reply_create_random_queue)
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_create_queue(self, update, context):
        if self.check_user_have_access(update.effective_user.id, self.owners_table):
            if len(self.cur_queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',
                                                   reply_markup=self.keyb_reply_create_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',
                                                   reply_markup=self.keyb_reply_create_queue)
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_edit_queue(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            update.message.reply_text('Редактирование очереди', reply_markup=self.keyb_modify_queue)
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_edit_registered(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            update.effective_chat.send_message('Редактирование пользователей', reply_markup=self.keyb_modify_registered)
        else:
            update.message.reply_text(msg_permission_denied)

    def _h_check_queue_status(self, update, context):
        if len(self.cur_queue) == 0:
            if self.check_user_have_access(update.effective_user.id, self.owners_table):
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',
                                                   reply_markup=self.keyb_reply_create_queue)
            else:
                update.effective_chat.send_message('Очереди нет.')
        else:
            msg = update.effective_chat.send_message(self.get_queue_str(self.cur_queue, self.cur_queue_pos),
                                                     reply_markup=self.keyb_move_queue)
            if update.effective_chat.type != Chat.PRIVATE:
                self.last_queue_message = msg

            self.logger.log(
                'user {0} in {1} chat requested queue'.format(update.effective_user.id, update.effective_chat.type))

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
            self.cur_queue.append(stud)
        else:
            self.cur_queue.append((update.effective_user.full_name, None))

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
            for s in delete: self.cur_queue.remove(s)
            return True

        return False

    def _h_error(self, update, context):
        print('Error: {0}'.format(context.error))
        self.logger.log(context.error)
        self.logger.save_to_cloud()

    # Генерация очереди
    def gen_random_queue(self, items):
        if len(items) > 0:
            shuff_items = []
            for i in items:
                shuff_items.append(self.find_similar(i))

            rnd.shuffle(shuff_items)
            return shuff_items

        return []

    def gen_queue(self, items):
        if len(items) > 0:
            lst = []
            for i in items:
                lst.append(self.find_similar(i))

            return lst
        return []

    def find_similar(self, name):
        for st_id, st_name in self.registered_students.items():
            if self.similar(name, st_name):
                return (st_name, st_id)
        return (name, None)

    def similar(self, first, second):
        if (len(first) - len(second)) > 2:
            return False

        if first[0] != second[0]:
            return False

        if len(first) - sum(l1 == l2 for l1, l2 in zip(first[1:], second[1:])) > 2:
            return False
        return True

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
                self.last_queue_message = self.last_queue_message.edit_text(new_text, reply_markup=self.keyb_move_queue)

    def get_id_by_name(self, dct, name):
        try:
            return list(dct.keys())[list(dct.values()).index(name)]
        except Exception:
            return None

    def get_queue_str(self, queue, cur_pos=None):
        # TODO add queue object
        pass

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
