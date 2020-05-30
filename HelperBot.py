import random as rnd
from pathlib import Path
from logger import Logger
from varsaver import VariableSaver
from gdrive_saver import DriveSaver, FolderType
import atexit
import os


from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Chat

class QueueBot:
    
    def __init__(self, bot_token = None):
        
        
        self.file_name_owner = Path('data/owners.data')
        self.file_name_registered = Path('data/registered.data')
        self.file_name_queue = Path('data/queue.data')
        self.file_name_bot_state = Path('data/bot_state.data')
        
        self.logger = Logger()
        self.varsaver = VariableSaver(logger = self.logger)
        self.gdrive_saver = DriveSaver()
        
        #  init bot commands
        
        if bot_token is None:
            bot_token = self.get_token()
            
        if bot_token is None:
            self.logger.log('Fatal error: token is empty')
            
        self.updater = Updater(bot_token, use_context=True)

        self.updater.dispatcher.add_handler(CommandHandler('i_finished', self.__h_i_finished))
        self.updater.dispatcher.add_handler(CommandHandler('remove_me', self.__h_remove_me))
        self.updater.dispatcher.add_handler(CommandHandler('add_me', self.__h_add_me_to_queue))
        self.updater.dispatcher.add_handler(CommandHandler('start', self.__h_start))
        self.updater.dispatcher.add_handler(CommandHandler('stop', self.__h_stop))
        self.updater.dispatcher.add_handler(CommandHandler('logs', self.__h_show_logs))
        self.updater.dispatcher.add_handler(CommandHandler('get_queue', self.__h_check_queue_status))
        self.updater.dispatcher.add_handler(CommandHandler('current_and_next', self.__h_get_cur_and_next_students))
        self.updater.dispatcher.add_handler(CommandHandler('new_queue', self.__h_create_queue))
        self.updater.dispatcher.add_handler(CommandHandler('new_random_queue', self.__h_create_random_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_queue', self.__h_edit_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_registered', self.__h_edit_registered))
        self.updater.dispatcher.add_handler(CommandHandler('owner', self.__h_add_new_owner))
        self.updater.dispatcher.add_handler(CommandHandler('del_owner', self.__h_del_owner))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.__h_message_text))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.__h_keyboard_chosen))
        self.updater.dispatcher.add_error_handler(self.__h_error)


        # ':' needed for correct commands split
        self.cmd_create_queue = 'create_queue'
        self.cmd_args_create_queue = ['simple','random']
        self.cmd_modify_queue = 'modify_queue'
        self.cmd_args_modify_queue = ['show_list', 
                                      'change_list', 
                                      'set_queue_pos', 
                                      'clear_list', 
                                      'move_to_end', 
                                      'del_student', 
                                      'set_student_pos', 
                                      'add_student', 
                                      'swap_students']
        self.cmd_move_queue = 'move_queue'
        self.cmd_args_move_queue = ['prev','next','refresh']
        self.cmd_set_owner = 'set_owner'
        self.cmd_del_owner = 'del_owner'
        self.cmd_modify_registered = 'mod_registered'
        self.cmd_args_modify_registered = ['show_list','add_users','reg_one_user','del_users']
        
        
        # stores user who requested
        self.msg_request = (None, None) # first - user id; second - request code
        self.requests_by_code = {
            0 : (self.cmd_create_queue, self.cmd_args_create_queue[0]), # regular queue
            1 : (self.cmd_create_queue, self.cmd_args_create_queue[1]), # random queue
            2 : (self.cmd_set_owner, None),
            3 : (self.cmd_del_owner, None),
            4 : (self.cmd_modify_queue, self.cmd_args_modify_queue[4]),
            8 : (self.cmd_modify_queue, self.cmd_args_modify_queue[5]),
            9 : (self.cmd_modify_queue, self.cmd_args_modify_queue[6]),
            10: (self.cmd_modify_queue, self.cmd_args_modify_queue[7]),
            11: (self.cmd_modify_queue, self.cmd_args_modify_queue[8]),
            12: (self.cmd_modify_queue, self.cmd_args_modify_queue[2]), # set queue pos
            5 : (self.cmd_modify_registered, self.cmd_args_modify_registered[1]),
            6 : (self.cmd_modify_registered, self.cmd_args_modify_registered[2]),
            7 : (self.cmd_modify_registered, self.cmd_args_modify_registered[3]),
        }
        self.request_codes = {req:code for code,req in self.requests_by_code.items()}
        
        

        self.keyb_reply_create_queue = InlineKeyboardMarkup([[InlineKeyboardButton('Создать очередь',callback_data=self.cmd_create_queue+':'+self.cmd_args_create_queue[0])],
                                                        [InlineKeyboardButton('Отмена',callback_data=self.cmd_create_queue+':'+'False')]])
                                                        
        self.keyb_reply_create_random_queue = InlineKeyboardMarkup([[InlineKeyboardButton('Создать очередь',callback_data=self.cmd_create_queue+':'+self.cmd_args_create_queue[1])],
                                                        [InlineKeyboardButton('Отмена',callback_data=self.cmd_create_queue+':'+'False')]])

        self.keyb_modify_queue = InlineKeyboardMarkup([
            [InlineKeyboardButton('Переместить студента в конец',   callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[4])],
            [InlineKeyboardButton('Поменять местами',               callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[8])],
            [InlineKeyboardButton('Поставить студента на позицию',  callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[6])],
            [InlineKeyboardButton('Удалить студентов',              callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[5])],
            [InlineKeyboardButton('Добавить студента',              callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[7])],
            [InlineKeyboardButton('Установить позицию очереди',     callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[2])],
            [InlineKeyboardButton('Показать очередь',               callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[0])],
            [InlineKeyboardButton('Установить новую очередь',       callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[1])],
            [InlineKeyboardButton('Очистить очередь',               callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[3])]
        ])
        
        self.keyb_move_queue = InlineKeyboardMarkup([
            [InlineKeyboardButton('Следующий',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[1])],
            [InlineKeyboardButton('Предыдущий',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[0])],
            [InlineKeyboardButton('Обновить',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[2])]
        ])

        self.keyb_modify_registered = InlineKeyboardMarkup([
            [InlineKeyboardButton('Показать зарегистрированных',        callback_data=self.cmd_modify_registered+':'+self.cmd_args_modify_registered[0])],
            [InlineKeyboardButton('Зарегистрировать пользователя',      callback_data=self.cmd_modify_registered+':'+self.cmd_args_modify_registered[2])],
            [InlineKeyboardButton('Добавить список пользователей(с ID)',callback_data=self.cmd_modify_registered+':'+self.cmd_args_modify_registered[1])],
            [InlineKeyboardButton('Удалить несколько пользователей',    callback_data=self.cmd_modify_registered+':'+self.cmd_args_modify_registered[3])]
        ])

        self.owners_table = {}
        self.registered_students = {} # key - id value - name
        self.cur_students_list = []
        self.cur_queue = []
        self.cur_queue_pos = 0
        self.last_queue_message = None

        self.msg_permission_denied = 'Нет разрешения'
        self.msg_code_not_valid = 'Внутренняя ошибка: Уровень доступа имеет неверный формат'
        self.msg_owner_not_found = 'Не владелец'
        self.msg_set_students = 'Введите новый список студентов\nон должен состоять из строк с именами студентов'
        self.msg_set_registered_students = 'Введите новый список студентов он должен состоять из строк\nв формате: имя_студента-telegram_id'
        self.msg_del_registered_students = 'Чтобы удалить несколько пользователей, введите их позиции в списке через пробел'
        self.msg_get_user_message = 'Перешлите сообщение пользователя'
        self.msg_queue_finished = 'Очередь завершена'
        self.msg_unknown_user = 'Неизвестный пользователь. Вы не можете использовать данную команду (возможно в вашем аккаунте ID закрыт для просмотра)'
        self.msg_queue_commands = 'когда сдашь\n/i_finished\nчтобы выйти из очереди\n/remove_me\nчтобы попасть в конец очереди\n/add_me'
        self.msg_error_in_values = 'Ошибка в значениях'
        
        atexit.register(self.save_before_stop)
        
    def start(self):
        self.logger.log('start')
        self.load_defaults()
        self.updater.start_polling()
        self.updater.idle()
        
    def save_before_stop(self):
        if not self.cur_queue_pos is None:
            if self.cur_queue_pos == len(self.cur_queue):
                self.__delete_cur_queue()
                
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
            new_folder = self.file_name_queue.parent)
    
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
        if self.owners_table is None: self.owners_table = {}
        
    def load_registered_from_file(self):
        self.registered_students = self.varsaver.load(self.file_name_registered)
        if self.registered_students is None: self.registered_students = {}
        
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
        self.varsaver.save({'cur_queue_pos':self.cur_queue_pos}, self.file_name_bot_state)
        
    def save_owners_to_file(self):
        self.varsaver.save(self.owners_table, self.file_name_owner)
        self.gdrive_saver.update_file_list([self.self.file_name_owner])
        
    def save_registered_to_file(self):
        self.varsaver.save(self.registered_students, self.file_name_registered)
        self.gdrive_saver.update_file_list([self.self.file_name_registered])
        
    def save_queue_to_file(self):
        self.varsaver.save(self.cur_queue, self.file_name_queue)
            
    def get_token(self, path = None):
        return os.environ.get('TELEGRAM_TOKEN')

    def __h_keyboard_chosen(self, update, context):
        query = update.callback_query
        cmd, args = self.parce_query_cmd(query.data)
        
        # commands with no access required
        if cmd == self.cmd_move_queue:
            
            if args==self.cmd_args_move_queue[0]:
                # move prev
                if self.cur_queue_pos > 0:
                    self.cur_queue_pos = self.cur_queue_pos - 1
                    update.effective_chat.send_message(self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))
                    query.edit_message_text(self.get_queue_str(self.cur_queue, self.cur_queue_pos), reply_markup=self.keyb_move_queue)
                    
            elif args==self.cmd_args_move_queue[1]:
                # move next
                if self.cur_queue_pos < len(self.cur_queue):
                    self.cur_queue_pos = self.cur_queue_pos + 1
                    update.effective_chat.send_message(self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))
                    query.edit_message_text(self.get_queue_str(self.cur_queue,self.cur_queue_pos), reply_markup = self.keyb_move_queue)
            
            elif args==self.cmd_args_move_queue[2]:
                self.__refresh_cur_queue_ids()
                new_queue_str = self.get_queue_str(self.cur_queue, self.cur_queue_pos)
                if query.message.text != new_queue_str:
                    query.edit_message_text(new_queue_str, reply_markup = self.keyb_move_queue)
            
        elif self.check_user_have_access(query.from_user.id, self.owners_table):
            
            self.logger.log(str(update.effective_user.id)+' - '+query.data)
            
            if cmd is not None:
                if cmd == self.cmd_create_queue:
                    if args != 'False':
                        self.__delete_cur_queue()
                        update.effective_chat.send_message(self.msg_set_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                    else:
                        update.effective_message.delete()
                        
                elif cmd == self.cmd_modify_queue:

                    if args==self.cmd_args_modify_queue[0]:
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue))
                            
                    elif args==self.cmd_args_modify_queue[1]:
                        update.effective_chat.send_message(self.msg_set_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(self.cmd_create_queue, self.cmd_args_create_queue[0])])
                        
                    elif args==self.cmd_args_modify_queue[3]:
                        self.__delete_cur_queue()
                        update.effective_chat.send_message('Очередь удалена')
                        
                    elif args==self.cmd_args_modify_queue[4]:
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue))
                        update.effective_chat.send_message('Пришлите номер студента в очереди')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                        
                    elif args==self.cmd_args_modify_queue[5]:
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue))
                        update.effective_chat.send_message('Пришлите номер студентов в очереди через пробел')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                   
                    elif args==self.cmd_args_modify_queue[6]:
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue))
                        update.effective_chat.send_message('Пришлите номер студента в очереди и через пробел номер новой позиции')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                        
                    elif args==self.cmd_args_modify_queue[7]:
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue))
                        update.effective_chat.send_message('Пришлите имя нового студента, он будет добавлен в конец очереди')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                    
                    elif args==self.cmd_args_modify_queue[8]:
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue))
                        update.effective_chat.send_message('Пришлите номера двух студентов через пробел')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                        
                    elif args==self.cmd_args_modify_queue[2]:
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue))
                        update.effective_chat.send_message('Пришлите номер новой позциции')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                        
                        
                elif cmd == self.cmd_modify_registered:
                    if args == self.cmd_args_modify_registered[0]: # show
                        str_list = []
                        i=1
                        for st_id, name in self.registered_students.items():
                            str_list.append('{0}. {1}-{2}'.format(i, name, str(st_id)))
                            i+=1
                        update.effective_chat.send_message('Все известные пользователи:\n'+'\n'.join(str_list))
                    elif args == self.cmd_args_modify_registered[1]: # add list
                        update.effective_chat.send_message(self.msg_set_registered_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd,args)])
                    elif args == self.cmd_args_modify_registered[2]: # reg one
                        update.effective_chat.send_message(self.msg_get_user_message)
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd,args)])
                    elif args == self.cmd_args_modify_registered[3]: # delete list
                        update.effective_chat.send_message(self.msg_del_registered_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd,args)])
                    elif args == self.cmd_args_modify_registered[4]: # rename all
                        update.effective_chat.send_message('Введите список новых имен для всех пользователей')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd,args)])
                        
            else:
                print('In update \"{0}\" command: {1} not valid'.format(update, query.data))
                self.logger.log('In update \"{0}\" command: {1} not valid'.format(update, query.data))
                
        else:
            update.message.reply_text(self.msg_permission_denied)
        
        update.callback_query.answer()
        
    def __h_message_text(self, update, context):
        
        if update.message.from_user.id != self.msg_request[0] or \
            update.effective_chat.type != Chat.PRIVATE:
            return
        
        self.logger.log(self.msg_request)
        
        if self.msg_request[1] == 0 or self.msg_request[1] == 1:
            
            if '\n' in update.message.text:
                self.cur_students_list = update.message.text.split('\n')
            else:
                self.cur_students_list = [update.message.text]
            
            self.cur_students_list = [i for i in self.cur_students_list if not i=='']
            
            update.effective_chat.send_message('Студенты установлены')
            
            if self.msg_request[1] == 0:
                self.cur_queue = self.gen_queue(self.cur_students_list)
                self.cur_queue_pos = 0
            elif self.msg_request[1] == 1:
                self.cur_queue = self.gen_random_queue(self.cur_students_list)
                self.cur_queue_pos = 0
            
            update.effective_chat.send_message(self.get_queue_str(self.cur_queue), reply_markup = self.keyb_move_queue)
                
            self.save_queue_to_file()
            self.__refresh_last_queue_msg()
            self.msg_request = (None, None)
            
        elif self.msg_request[1] == 2:
            if update.message.forward_from is not None:
                return_msg = self.add_new_bot_owner(update.effective_user.id, update.message.forward_from.id, 1)
                if return_msg is not None:
                    update.message.reply_text(return_msg)
                else:
                    update.message.reply_text('Владелец успешно установлен')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано, отмена')
            self.msg_request = (None, None)

        elif self.msg_request[1] == 3:
            if update.message.forward_from is not None:
                return_msg = self.del_bot_owner(update.effective_user.id,update.message.forward_from.id)
                if return_msg is not None:
                    update.message.reply_text(return_msg)
                else:
                    update.message.reply_text('Владелец успешно удален')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано')
                
            self.msg_request = (None, None)

        elif self.msg_request[1] == 4:
            try:
                move_pos = int(update.message.text)-1
                if move_pos >= len(self.cur_queue) or move_pos < 0:
                    self.msg_request = (None, None)
                    return
                
                self.cur_queue.append(self.cur_queue.pop(move_pos))
                self.__refresh_last_queue_msg()
                update.effective_chat.send_message('Студент добавлен в конец')
            except ValueError:
                update.effective_chat.send_message('Не номер из очереди. Отмена операции')
            finally:
                self.msg_request = (None, None)
        
        elif self.msg_request[1] == 8:
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
                    if pos>0 and pos<=len(self.cur_queue):
                        del_users.append(pos)
                    else:
                        err_list.append(str(pos))
                except Exception:
                    err_list.append(pos_str)
            
            for el in [self.cur_queue[i-1] for i in del_users]:
                self.cur_queue.remove(el)
            
            if len(err_list) > 0: update.effective_chat.send_message('Ошибка возникла в этих значениях:\n'+' '.join(err_list))
            if len(del_users) > 0: update.effective_chat.send_message('Пользователи удалены')
            
            self.save_queue_to_file()
            self.__refresh_last_queue_msg()
            self.msg_request = (None, None)
        
        elif self.msg_request[1] == 9:
            try:
                user_str = update.message.text.split(' ')
                cur_pos, set_pos = int(user_str[0])-1, int(user_str[1])-1
                
                assert  cur_pos >= 0 and cur_pos < len(self.cur_queue) and \
                        set_pos >= 0 and set_pos < len(self.cur_queue)

                self.cur_queue.insert(set_pos, self.cur_queue.pop(cur_pos))
                update.effective_chat.send_message('Студент перемещен')
                
                self.save_queue_to_file()
                self.__refresh_last_queue_msg()

            except Exception:
                update.effective_chat.send_message(self.msg_error_in_values)
            finally:
                self.msg_request = (None, None)
        
        elif self.msg_request[1] == 10:
            self.cur_queue.append(self.find_similar(update.message.text))
            self.logger.log('student set '+str(self.cur_queue[-1]))
            update.effective_chat.send_message('Студент установлен')
            
            self.save_queue_to_file()
            self.__refresh_last_queue_msg()
            self.msg_request = (None, None)
        
        elif self.msg_request[1] == 11:
            try:
                user_str = update.message.text.split(' ')
                cur_pos, swap_pos = int(user_str[0])-1, int(user_str[1])-1
                
                assert  cur_pos >= 0 and cur_pos < len(self.cur_queue) and \
                        swap_pos >= 0 and swap_pos < len(self.cur_queue)
                        
                self.cur_queue[cur_pos], self.cur_queue[swap_pos] = self.cur_queue[swap_pos], self.cur_queue[cur_pos]
                update.effective_chat.send_message('Студенты перемещены')

            except Exception:
                update.effective_chat.send_message(self.msg_error_in_values)
            finally:
                self.save_queue_to_file()
                self.__refresh_last_queue_msg()
                self.msg_request = (None, None)
        
        elif self.msg_request[1] == 12:
            try:
                new_index = int(update.message.text)
                self.cur_queue_pos = new_index - 1
                update.effective_chat.send_message('Позиция установлена')
            except Exception:
                update.effective_chat.send_message(self.msg_error_in_values)
            finally:
                self.save_bot_state_to_file()
                self.__refresh_last_queue_msg()
                self.msg_request = (None, None)
            
        
        elif self.msg_request[1] == 5: # add list
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
                
            
            if len(err_list) > 0: update.effective_chat.send_message('Ошибка возникла в этих строках:\n'+'\n'.join(err_list))
            if len(new_users) > 0: update.effective_chat.send_message('Пользователи добавлены')
            
            self.save_queue_to_file()
            self.__refresh_last_queue_msg()
            self.msg_request = (None, None)        
                
        elif self.msg_request[1] == 6: # add one
            if update.message.forward_from is not None:
                self.set_bot_user(update.message.forward_from.id, update.message.forward_from.full_name)
                update.message.reply_text('Пользователь зарегистрирован')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано, отмена')
            
            self.save_queue_to_file()
            self.__refresh_last_queue_msg()
            self.msg_request = (None, None)
            
        elif self.msg_request[1] == 7: # del list                    
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
                    if pos>0 and pos<=len(self.registered_students):
                        del_users.append(pos)
                    else:
                        err_list.append(str(pos))
                        
                except Exception:
                    err_list.append(pos_str)
                    
            all_user_keys = list(self.registered_students.keys())
            delete_keys = set([all_user_keys[i-1] for i in del_users])
            
            for i in delete_keys:
                del self.registered_students[i]
            
            if len(err_list) > 0: update.effective_chat.send_message('Ошибка в этих значениях:\n'+'\n'.join(err_list))
            if len(del_users) > 0: update.effective_chat.send_message('Пользователи удалены')
            
            self.save_queue_to_file()
            self.__refresh_last_queue_msg()
            self.msg_request = (None, None)
        
    def __h_add_new_owner(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            if self.msg_request[0] is None:              
                update.message.reply_text(self.msg_get_user_message)
                self.msg_request = (update.message.from_user.id, self.request_codes[(self.cmd_set_owner, None)])
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(self.msg_permission_denied)

    def __h_del_owner(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            if self.msg_request[0] is None:           
                update.message.reply_text(self.msg_get_user_message)
                self.msg_request = (update.message.from_user.id, self.request_codes[(self.cmd_del_owner, None)])
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(self.msg_permission_denied)

    def __h_start(self, update, context):
        if len(self.owners_table)==0:
            self.owners_table[update.message.from_user.id] = 0
            update.message.reply_text('Первый владелец добавлен - '+update.message.from_user.username)
            
            for admin in update.effective_chat.get_administrators():
                self.owners_table[admin.user.id] = 1
            
            self.save_owners_to_file()
            update.effective_chat.send_message('Администраторы добавлены')
            
        elif self.check_user_have_access(update.effective_user.id, self.owners_table):
            update.message.reply_text('Бот уже запущен.')

    def __h_stop(self, update, context):
        if self.check_user_have_access(update.effective_user.id, self.owners_table):
            update.message.reply_text('Бот остановлен, и больше не принимает команд')
            self.updater.stop()
            exit()
        
    def __h_show_logs(self, update, context):
        if self.check_user_have_access(update.effective_user.id, self.owners_table, 0):
            
            trimmed_msg = self.logger.get_logs()[-4096:]
            if len(trimmed_msg) >= 4096: trimmed_msg = trimmed_msg[trimmed_msg.index('\n'):]
            
            update.effective_chat.send_message(trimmed_msg)
        
    def __h_create_random_queue(self, update, context):
        if self.check_user_have_access(update.effective_user.id,self.owners_table):
            if len(self.cur_queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup=self.keyb_reply_create_random_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',reply_markup=self.keyb_reply_create_random_queue)
        else:
            update.message.reply_text(self.msg_permission_denied)
            
    def __h_create_queue(self, update, context):
        if self.check_user_have_access(update.effective_user.id,self.owners_table):
            if len(self.cur_queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup=self.keyb_reply_create_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',reply_markup = self.keyb_reply_create_queue)
        else:
            update.message.reply_text(self.msg_permission_denied)

    def __h_edit_queue(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            update.message.reply_text('Редактирование очереди', reply_markup=self.keyb_modify_queue)
        else:
            update.message.reply_text(self.msg_permission_denied)
        
    def __h_edit_registered(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_table):
            update.effective_chat.send_message('Редактирование пользователей', reply_markup=self.keyb_modify_registered)
        else:
            update.message.reply_text(self.msg_permission_denied)
        
    def __h_check_queue_status(self, update, context):
        if len(self.cur_queue)==0:
            if self.check_user_have_access(update.effective_user.id, self.owners_table):
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup = self.keyb_reply_create_queue)
            else:
                update.effective_chat.send_message('Очереди нет.')
        else:
            msg = update.effective_chat.send_message(self.get_queue_str(self.cur_queue, self.cur_queue_pos), reply_markup=self.keyb_move_queue)
            if update.effective_chat.type != Chat.PRIVATE:
                self.last_queue_message = msg
            
            self.logger.log('user {0} in {1} chat requested queue'.format(update.effective_user.id, update.effective_chat.type))
            

    def __h_get_cur_and_next_students(self, update, context):
        update.effective_chat.send_message(self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))
       
    def __h_i_finished(self, update, context):
        cur_user_id = update.effective_user.id
        if cur_user_id in self.registered_students.keys():
            if self.cur_queue_pos>=0 and self.cur_queue_pos<len(self.cur_queue):
                if cur_user_id == self.cur_queue[self.cur_queue_pos][1] or \
                    self.similar(self.registered_students[cur_user_id], self.cur_queue[self.cur_queue_pos][0]):
                    self.cur_queue_pos += 1
                    update.effective_chat.send_message(self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))
                else:
                    update.message.reply_text('{0}, вы не сдаете сейчас.'.format(self.registered_students[cur_user_id]))
            else:
                update.message.reply_text('{0}, вы не сдаете сейчас.'.format(self.registered_students[cur_user_id]))
        else:
            update.message.reply_text(self.msg_unknown_user)
        
        self.__refresh_last_queue_msg()
        self.save_bot_state_to_file()
        self.logger.log('finished {0} - {1}'.format(cur_user_id, self.cur_queue[self.cur_queue_pos]))
            
    def __h_remove_me(self, update, context):
    
        cur_user_id = update.effective_user.id
        
        if cur_user_id in self.registered_students:
            stud = (self.registered_students[cur_user_id], cur_user_id)
        else:
            stud = (update.effective_user.full_name, None)
        
        if self.delete_stud_from_queue(stud):
            self.__refresh_last_queue_msg()
            self.save_queue_to_file()
            self.save_bot_state_to_file()
            
            update.message.reply_text('Вы удалены из очереди'.format(self.registered_students[cur_user_id]))    
            self.logger.log('removed {0} - {1} '.format(self.registered_students[cur_user_id], cur_user_id))
        
        else:
            update.message.reply_text('Вы не найдены в очереди')
            
        
    def __h_add_me_to_queue(self, update, context):
        cur_user_id = update.effective_user.id
        
        if (not cur_user_id is None) and (cur_user_id in self.registered_students):
            stud = (self.registered_students[cur_user_id], cur_user_id)
            self.delete_stud_from_queue(stud)
            self.cur_queue.append(stud)
        else:
            self.cur_queue.append((update.effective_user.full_name, None))

        update.message.reply_text('Вы записаны в очередь')
        
        self.__refresh_last_queue_msg()
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
                
            print('appended',appended, cur_queue_pos, stud, delete)
                
        if len(delete) > 0:
            for s in delete: self.cur_queue.remove(s)
            return True
        
        return False
        
    def __h_error(self, update, context): 
        print('Error: {0}'.format(context.error))
        self.logger.log(context.error)
        self.logger.save_to_cloud()

    def parce_query_cmd(self,command):
        try:
            items = command.split(':')
            return items[0],''.join(items[1:])
        except Exception:
            return None,None
            
    
    # Генерация очереди
    def gen_random_queue(self,items):
        if len(items)>0:
            shuff_items = []
            for i in items:
                shuff_items.append(self.find_similar(i))
            
            rnd.shuffle(shuff_items)
            return shuff_items
        
        return []
    
    def gen_queue(self, items):
        if len(items)>0:
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
        if (len(first)-len(second))>2:
            return False
        
        if first[0] != second[0]:
            return False
        
        if len(first) - sum(l1==l2 for l1, l2 in zip(first[1:], second[1:])) > 2:
            return False
        return True

    def __delete_cur_queue(self):
        self.cur_queue = []
        self.cur_queue_pos = None
    
    def __refresh_cur_queue_ids(self):
        for idx in range(len(self.cur_queue)):
            i = self.cur_queue[idx][0] # name of student in i
            
            if i in self.registered_students.values(): self.cur_queue[idx] = (i, self.get_id_by_name(self.registered_students, i))
            else: self.cur_queue[idx] = (i, None)

    def __refresh_last_queue_msg(self):
        if not self.last_queue_message is None:
            new_text = self.get_queue_str(self.cur_queue, self.cur_queue_pos)
            if self.last_queue_message.text != new_text:
                self.last_queue_message = self.last_queue_message.edit_text(new_text, reply_markup=self.keyb_move_queue)
        
    def get_id_by_name(self, dct, name):
        try:
            return list(dct.keys())[list(dct.values()).index(name)]
        except Exception:
            return None

    def get_queue_str(self, queue, cur_pos = None):
        if len(queue) > 0:
            if cur_pos is not None:
            
                str_list = []

                cur_item, next_item = self.get_cur_and_next(cur_pos, queue)

                if cur_item is None:
                    return self.msg_queue_finished

                str_list.append('Сдает:')
                str_list.append(self.get_queue_student_str(cur_pos, queue))
                str_list.append('\nСледующий:')
                if next_item is not None:
                    str_list.append(self.get_queue_student_str(cur_pos + 1, queue))
                else:
                    str_list.append('Нет')
                    
                if (cur_pos + 2) < len(queue):
                    str_list.append('\nОставшиеся:')
                    for i in range(cur_pos + 2, len(queue)):
                        str_list.append(self.get_queue_student_str(i, queue))
                        
                return '\n'.join(str_list)+'\n\n'+self.msg_queue_commands
            else:
                return 'Очередь:\n'+'\n'.join([self.get_queue_student_str(i, queue) for i in range(len(queue))])
        
        return self.msg_queue_finished
    
    def get_queue_student_str(self, stud_pos, queue):
        return '{0} - {1}'.format(stud_pos+1, queue[stud_pos][0])


    # Получить текущего и следующего человека в очереди
    def get_cur_and_next(self, pos, queue):
        if pos < len(queue)-1 and pos >= 0:
            return queue[pos], queue[pos+1]
        elif pos == len(queue)-1:
            return queue[pos], None
        
        return None, None
    
    def get_cur_and_next_str(self, cur_stud, next_stud):
        msg = ''
        if cur_stud is not None: 
            msg = 'Сдает - {0}'.format(cur_stud[0])
        if next_stud is not None: 
            msg = msg + '\nГотовится - {0}'.format(next_stud[0])
            
        return msg if msg!='' else self.msg_queue_finished
    
    # Администрирование

    # Передача прав редактирования
    def set_bot_user(self, user_id, user_name):
        self.registered_students[user_id] = user_name
        self.save_registered_to_file()
        
    def add_new_bot_owner(self, user_id, new_owner_id, new_access_level = None):
        if self.check_user_have_access(user_id,self.owners_table):
            if new_access_level >= 0:
                if new_access_level == None:
                    self.owners_table[new_owner_id] = self.owners_table[user_id] + 1
                    self.save_owners_to_file()
                    return None
                elif self.owners_table[user_id] < new_access_level:
                    self.owners_table[new_owner_id] = new_access_level
                    self.save_owners_to_file()
                    return None
                
                return self.msg_permission_denied
            else:
                return self.msg_code_not_valid
        else:
            return self.msg_permission_denied

    def del_bot_owner(self, user_id, del_owner_id):
        if self.check_user_have_access(user_id,self.owners_table):
            try:
                if self.owners_table[user_id] < self.owners_table[del_owner_id]:
                    del self.owners_table[del_owner_id]
                    self.save_owners_to_file()
                    return None
                else:
                    return self.msg_permission_denied
            except ValueError:
                return self.msg_owner_not_found
        else:
            return self.msg_permission_denied

    def check_user_have_access(self, user_id, access_levels_dict, access_level = 1):
        if user_id in access_levels_dict:
            if access_levels_dict[user_id]<=access_level:
                return True
        return False
        