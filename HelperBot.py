import random as rnd
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

class QueueBot:
    
    def __init__(self,bot_token):
        self.updater = Updater(bot_token, use_context=True)

        self.updater.dispatcher.add_handler(CommandHandler('start', self.h_start))
        self.updater.dispatcher.add_handler(CommandHandler('get_queue', self.h_check_queue_status))
        # self.updater.dispatcher.add_handler(CommandHandler('i_finished', self.h_i_finished))
        self.updater.dispatcher.add_handler(CommandHandler('current_and_next', self.h_get_cur_and_next_students))
        self.updater.dispatcher.add_handler(CommandHandler('new_queue', self.h_create_queue))
        self.updater.dispatcher.add_handler(CommandHandler('new_random_queue', self.h_create_random_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_queue', self.h_edit_queue))
        # self.updater.dispatcher.add_handler(CommandHandler('edit_registered', self.h_edit_registered))
        self.updater.dispatcher.add_handler(CommandHandler('owner', self.h_add_new_owner))
        self.updater.dispatcher.add_handler(CommandHandler('del_owner', self.h_del_owner))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.h_message_text))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.h_keyboard_chosen))
        self.updater.dispatcher.add_error_handler(self.h_error)


        # ':' needed for correct commands split
        self.cmd_add_students = 'add_students'
        self.cmd_create_queue = 'create_queue'
        self.cmd_args_create_queue = ['simple','random']
        self.cmd_modify_queue = 'modify_queue'
        self.cmd_args_modify_queue = ['show_list','change_list','add_one_student','clear_list','move_to_end','del_student']
        self.cmd_move_queue = 'move_queue'
        self.cmd_args_move_queue = ['prev','next','refresh']
        self.cmd_set_owner = 'set_owner'
        self.cmd_del_owner = 'del_owner'
        self.cmd_modify_registered = 'mod_registered'
        self.cmd_args_modify_registered = ['show_list','add_users','reg_one_user','del_users']
        

        self.keyb_reply_create_queue = InlineKeyboardMarkup([[InlineKeyboardButton('Создать очередь',callback_data=self.cmd_create_queue+':'+self.cmd_args_create_queue[0])],
                                                        [InlineKeyboardButton('Отмена',callback_data=self.cmd_create_queue+':'+'False')]])
                                                        
        self.keyb_reply_create_random_queue = InlineKeyboardMarkup([[InlineKeyboardButton('Создать очередь',callback_data=self.cmd_create_queue+':'+self.cmd_args_create_queue[1])],
                                                        [InlineKeyboardButton('Отмена',callback_data=self.cmd_create_queue+':'+'False')]])

        self.keyb_modify_queue = InlineKeyboardMarkup([
            [InlineKeyboardButton('Показать очередь',               callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[0])],
            [InlineKeyboardButton('Переместить студента в конец',   callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[4])],
            [InlineKeyboardButton('Удалить студента',               callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[5])],
            [InlineKeyboardButton('Установить новую очередь',       callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[1])],
            [InlineKeyboardButton('Пересоздать очередь',            callback_data=self.cmd_modify_queue+':'+self.cmd_args_modify_queue[3])]
        ])
        
        self.keyb_move_queue = InlineKeyboardMarkup([
            [InlineKeyboardButton('Следующий',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[1])],
            [InlineKeyboardButton('Предыдущий',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[0])],
            [InlineKeyboardButton('Обновить',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[2])]
        ])

        self.keyb_modify_registered = InlineKeyboardMarkup([
            [InlineKeyboardButton('Показать зарегистрированных',        callback_data=self.cmd_modify_registered+':'+self.cmd_args_modify_registered[0])],
            [InlineKeyboardButton('Добавить список пользователей(ID)',  callback_data=self.cmd_modify_registered+':'+self.cmd_args_modify_registered[1])],
            [InlineKeyboardButton('Зарегистрировать пользователя',      callback_data=self.cmd_modify_registered+':'+self.cmd_args_modify_registered[2])],
            [InlineKeyboardButton('Удалить несколько пользователей',    callback_data=self.cmd_modify_registered+':'+self.cmd_args_modify_registered[3])]
        ])

        self.users_access_table = {448309618:0, 364109973:1, 286511343:1}
        self.registered_students = {} # first - id second - name
        self.cur_students_list = []
        self.cur_queue = []
        self.cur_queue_pos = 0

        self.msg_permission_denied = 'Нет разрешения'
        self.msg_code_not_valid = 'Внутренняя ошибка: Уровень доступа имеет неверный формат'
        self.msg_owner_not_found = 'Не владелец'
        self.msg_set_students = 'Введите новый список студентов\nон должен состоять из строк с именами студентов'
        self.msg_set_registered_students = 'Введите новый список студентов он должен состоять из строк\nв формате: имя_студента-telegram_id'
        self.msg_del_registered_students = 'Чтобы удалить несколько пользователей, введите их позиции в списке каждую в новой строке'
        self.msg_get_user_message = 'Перешлите сообщение пользователя'
        self.msg_queue_finished = 'Очередь завершена'

        # stores user who requested
        self.msg_request = (None, None) # first - user id; second - request code
        self.requests_by_code = {
            0 : (self.cmd_create_queue, self.cmd_args_create_queue[0]), # regular queue
            1 : (self.cmd_create_queue, self.cmd_args_create_queue[1]), # random queue
            2 : (self.cmd_set_owner, None),
            3 : (self.cmd_del_owner, None),
            4 : (self.cmd_modify_queue, self.cmd_args_modify_queue[4]),
            8 : (self.cmd_modify_queue, self.cmd_args_modify_queue[5]),
            5 : (self.cmd_modify_registered, self.cmd_args_modify_registered[1]),
            6 : (self.cmd_modify_registered, self.cmd_args_modify_registered[2]),
            7 : (self.cmd_modify_registered, self.cmd_args_modify_registered[3])
        }
        self.request_codes = dict([(req,code) for code,req in self.requests_by_code.items()])
        
    def start(self):
        self.updater.start_polling()
        # print('started')
        self.updater.idle()

    def h_keyboard_chosen(self, update, context):
        query = update.callback_query
        if self.check_user_have_access(query.from_user.id,self.users_access_table):
            cmd, args = self.parce_query_cmd(query.data)
            if cmd is not None:
                if cmd == self.cmd_move_queue:
                    if args==self.cmd_args_move_queue[0]:
                        # move prev
                        if self.cur_queue_pos > 0:
                            self.cur_queue_pos = self.cur_queue_pos - 1
                            query.edit_message_text(self.get_queue_str(self.cur_queue,self.cur_queue_pos),reply_markup=self.keyb_move_queue)
                            update.effective_chat.send_message(self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))
                            
                    elif args==self.cmd_args_move_queue[1]:
                        # move next
                        if self.cur_queue_pos < len(self.cur_queue):
                            self.cur_queue_pos = self.cur_queue_pos + 1
                            query.edit_message_text(self.get_queue_str(self.cur_queue,self.cur_queue_pos),reply_markup=self.keyb_move_queue)
                            update.effective_chat.send_message(self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))
                    elif args==self.cmd_args_move_queue[2]:
                            query.edit_message_text(self.get_queue_str(self.cur_queue,self.cur_queue_pos),reply_markup=self.keyb_move_queue)
                
                elif cmd == self.cmd_add_students:
                    if args=='True':
                        query.edit_message_text('Редактирование очереди', reply_markup=self.keyb_modify_queue)
                    else:
                        update.effective_message.delete()
                        
                elif cmd == self.cmd_create_queue:
                    if args != 'False':
                        self.delete_cur_queue()
                        update.effective_chat.send_message(self.msg_set_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                    else:
                        update.effective_message.delete()
                        
                elif cmd == self.cmd_modify_queue:

                    if args==self.cmd_args_modify_queue[0]:
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue,self.cur_queue_pos))
                            
                    elif args==self.cmd_args_modify_queue[1]:
                        update.effective_chat.send_message(self.msg_set_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(self.cmd_create_queue, self.cmd_args_create_queue[0])])
                        
                    elif args==self.cmd_args_modify_queue[3]:
                        self.delete_cur_queue()
                        update.effective_chat.send_message('Очередь удалена')
                        
                    elif args==self.cmd_args_modify_queue[4]:
                        update.effective_chat.send_message('Пришлите номер студента в очереди')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                        
                    elif args==self.cmd_args_modify_queue[5]:
                        update.effective_chat.send_message('Пришлите номер студента в очереди')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                   
                elif cmd == self.cmd_modify_registered:
                    if args == self.cmd_args_modify_registered[0]: # show
                        update.effective_chat.send_message('Все известные пользователи:\n'+'\n'.join([name+' - '+str(st_id) for st_id, name in self.registered_students.items()]))
                    elif args == self.cmd_args_modify_registered[1]: # add list
                        update.effective_chat.send_message(self.msg_set_registered_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd,args)])
                    elif args == self.cmd_args_modify_registered[2]: # reg one
                        update.effective_chat.send_message(self.msg_get_user_message)
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd,args)])
                    elif args == self.cmd_args_modify_registered[3]: # delete list
                        update.effective_chat.send_message(self.msg_del_registered_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd,args)])
                        
            else:
                logger.warning('In update "%s" command: %s not vallid', update, query.data)
                # print('In update \"{0}\" command: {1} not vallid'.format(update, query.data))
        else:
            if cmd == self.cmd_move_queue:
                if args==self.cmd_args_move_queue[2]:
                    query.edit_message_text(self.get_queue_str(self.cur_queue,self.cur_queue_pos),reply_markup=self.keyb_move_queue)
            else:
                update.message.reply_text(self.msg_permission_denied)

    def h_message_text(self, update, context):
        
        if update.message.from_user.id != self.msg_request[0]:
            return
         
        print("request:",self.msg_request)
        
        if self.msg_request[1] == 0 or self.msg_request[1] == 1:
            try:
                self.cur_students_list = update.message.text.split('\n')
                self.cur_students_list = [i for i in self.cur_students_list if not i=='']
                
                update.effective_chat.send_message('Студенты установлены')
                
                if self.msg_request[1] == 0:
                    self.cur_queue = self.gen_queue(self.cur_students_list)
                elif self.msg_request[1] == 1:
                    self.cur_queue = self.gen_random_queue(self.cur_students_list)
                    
                update.effective_chat.send_message(self.get_queue_str(self.cur_queue), reply_markup)
                
            except ValueError:
                update.effective_chat.send_message('Неверный формат списка. Отмена операции')
                
            except Exception:
                logger.warning('Update "%s" caused error', update)
                # print('{0} \nUpdate caused error'.format(str(update)))
                
            finally:
                self.msg_request = (None,None)
            
        elif self.msg_request[1] == 2:
            if update.message.forward_from is not None:
                return_msg = self.add_new_bot_owner(update.effective_user.id,update.message.forward_from.id, 1)
                if return_msg is not None:
                    update.message.reply_text(return_msg)
                else:
                    update.message.reply_text('Владелец успешно установлен')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано, отмена')
            self.msg_request = (None,None)

        elif self.msg_request[1] == 3:
            if update.message.forward_from is not None:
                return_msg = self.del_bot_owner(update.effective_user.id,update.message.forward_from.id)
                if return_msg is not None:
                    update.message.reply_text(return_msg)
                else:
                    update.message.reply_text('Владелец успешно удален')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано')
                
            self.msg_request = (None,None)

        elif self.msg_request[1] == 4:
            try:
                move_pos = int(update.message.text)-1
                if move_pos >= len(self.cur_queue) or move_pos < 0:
                    self.msg_request = (None,None)
                    return
                
                self.cur_queue.append(self.cur_queue.pop(move_pos))
                
                update.effective_chat.send_message('Студент добавлен в конец')
            except ValueError:
                update.effective_chat.send_message('Не номер из очереди. Отмена операции')
            finally:
                self.msg_request = (None,None)
        
        elif self.msg_request[1] == 8:
            try:
                move_pos = int(update.message.text)-1
                if move_pos >= len(self.cur_queue) or move_pos < 0:
                    update.effective_chat.send_message('Не номер из очереди. Отмена операции')
                    self.msg_request = (None, None)
                    return
                
                self.cur_queue.pop(move_pos)
                self.cur_queue.pop(move_pos)
                
                update.effective_chat.send_message('Студент удален')
            except ValueError:
                update.effective_chat.send_message('Не номер из очереди. Отмена операции')
            finally:
                self.msg_request = (None, None)
        
        elif self.msg_request[1] == 5: # add list
            new_users_str = []
            print(update.message.text)
            if '\n' in update.message.text:
                new_users_str = update.message.text.split('\n')
            else:
                new_users_str = [update.message.text]
                
            err_list = []
            new_users = []
            
            # закончить парсинг через тире
                    
            for u in new_users:
                self.registered_students[u[1]] = u[0]
            
            if len(err_list) > 0: update.effective_chat.send_message('Ошибка возникла в этих значениях:\n'+', '.join(err_list))
            if len(new_users) > 0: update.effective_chat.send_message('Пользователи добавлены')
        
        elif self.msg_request[1] == 6: # add one
            if update.message.forward_from is not None:
                return_msg = self.add_new_bot_owner(update.effective_user.id,update.message.forward_from.id, 1)
                if return_msg is not None:
                    update.message.reply_text(return_msg)
                else:
                    update.message.reply_text('Владелец успешно установлен')
            else:
                update.message.reply_text('Сообщение ни от кого не переслано, отмена')
           
        elif self.msg_request[1] == 7: # del list
            del_users_str = update.message.text.split('\n')
            
            err_list = []
            del_users = []
            for i in range(len(del_users_str)):
                try:
                    del_users.append(int(del_users_str[i]))
                except ValueError:
                    err_list.append(del_users_str[i])
                    
            for i in del_users:
                if i>=0 and i<len(self.registered_students):
                    del self.registered_students[i]
                else:
                    err_list.append(i)
            
            if len(err_list) > 0: update.effective_chat.send_message('Ошибка возникла в этих значениях:\n'+', '.join(err_list)+'\nНе в списке или не целые числа')
            if len(del_users) > 0: update.effective_chat.send_message('Пользователи удалены')
        
    def h_add_new_owner(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.users_access_table):
            if self.msg_request[0] is None:              
                update.message.reply_text(self.msg_get_user_message)
                self.msg_request = (update.message.from_user.id, self.request_codes[(self.cmd_set_owner, None)])
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(self.msg_permission_denied)

    def h_del_owner(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.users_access_table):
            if self.msg_request[0] is None:           
                update.message.reply_text(self.msg_get_user_message)
                self.msg_request = (update.message.from_user.id, self.request_codes[(self.cmd_del_owner, None)])
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(self.msg_permission_denied)

    def h_start(self,update, context):
        if len(self.users_access_table)==0:
            self.users_access_table[update.message.from_user.id]=0
            update.message.reply_text('Первый владелец добавлен - '+update.message.from_user.username)
            
            # add initializing every admin of chat as owner
            
        elif self.check_user_have_access(update.effective_user.id, self.users_access_table):
            update.message.reply_text('Бот уже запущен.');

    def h_create_random_queue(self, update, context):
        if self.check_user_have_access(update.effective_user.id,self.users_access_table):
            if len(self.cur_queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup=self.keyb_reply_create_random_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',reply_markup=self.keyb_reply_create_random_queue)
        else:
            update.message.reply_text(self.msg_permission_denied)
            
    def h_create_queue(self, update, context):
        if self.check_user_have_access(update.effective_user.id,self.users_access_table):
            if len(self.cur_queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup=self.keyb_reply_create_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',reply_markup = self.keyb_reply_create_queue)
        else:
            update.message.reply_text(self.msg_permission_denied)

    def h_edit_queue(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.users_access_table):
            update.message.reply_text('Редактирование очереди', reply_markup=self.keyb_modify_queue)
        else:
            update.message.reply_text(self.msg_permission_denied)
        
    def h_edit_registered(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.users_access_table):
            update.effective_chat.send_message('Редактирование пользователей', reply_markup=self.keyb_modify_registered)
        else:
            update.message.reply_text(self.msg_permission_denied)
        
    def h_check_queue_status(self, update, context):
        if len(self.cur_queue)==0:
            if self.check_user_have_access(update.effective_user.id, self.users_access_table):
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup = self.keyb_reply_create_queue)
            else:
                update.effective_chat.send_message('Очереди нет.')
        else:
            update.effective_chat.send_message(self.get_queue_str(self.cur_queue,self.cur_queue_pos), reply_markup=self.keyb_move_queue)

    def h_get_cur_and_next_students(self, update, context):
        update.effective_chat.send_message(self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))
       
    def h_i_finished(self, update, context):
        cur_user_id = update.effective_user.id
        
        if cur_user_id in self.registered_students.values():
            if cur_user_id == self.cur_queue[self.cur_queue_pos]:
                self.cur_queue_pos += 1
                update.effective_chat.send_message(self.get_cur_and_next_str(*self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)))
            else:
                update.message.reply_text('Вы не сдаете сейчас.')
        else:
            update.message.reply_text('Неизвестный пользователь. Вы не можете использовать данную команду. Зарегистрируйтесь у администратора')
            
    def parce_query_cmd(self,command):
        try:
            items = command.split(':')
            return items[0],''.join(items[1:])
        except Exception:
            return None,None
            
    def h_error(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error) 
    
    # Генерация очереди
    def gen_random_queue(self,items):
        if len(items)>0:
            shuff_items = []
            for i in items:
                if i in self.registered_students: shuff_items.append((i, self.registered_students[i]))
                else: shuff_items.append((i, None))
            
            rnd.shuffle(shuff_items)
            return shuff_items
        else:
            return []
            
    def gen_queue(self, items):
        if len(items)>0:
            lst = []
            
            for i in items:
                if i in self.registered_students: lst.append((i, self.registered_students[i]))
                else: lst.append((i, None))
            
            return lst
        else:
            return []

    def delete_cur_queue(self):
        self.cur_queue = []
        self.cur_queue_pos = 0

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
                        
                return '\n'.join(str_list)
            else:
                return 'Очередь:\n'+'\n'.join([self.get_queue_student_str(i, queue) for i in range(len(queue))])
        else:
            return self.msg_queue_finished
    
    def get_queue_student_str(self, stud_pos, queue):
        return '{0} - {1}'.format(stud_pos+1, queue[stud_pos][0])

    # Удаление из очереди
    def del_from_queue(self,queue,pos):
        new_queue = list(queue)
        new_queue.pop(pos)
        return [(i+1,new_queue[i][1]) for i in range(len(new_queue))]

    # Добавить человека в конец очереди
    def add_to_end(self,item,queue):
        queue.append((len(queue)+1,item))
        return queue

    # Переключить очередь вперед
    def move_queue_next(self,pos,queue):
        cur_item,next_item = get_cur_and_next(pos+1,queue)
        return pos+1,cur_item,next_item

    # Переключить очередь назад
    def move_queue_prev(self,pos,queue):
        cur_item,next_item = get_cur_and_next(pos-1,queue)
        return pos-1,cur_item,next_item

    # Получить текущего и следующего человека в очереди
    def get_cur_and_next(self, pos, queue):
        if pos < len(queue)-1 and pos >= 0:
            return queue[pos], queue[pos+1]
        elif pos == len(queue)-1:
            return queue[pos], None
        else:
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
    def add_new_bot_owner(self, user_id, new_owner_id, new_access_level = None):
        if self.check_user_have_access(user_id,self.users_access_table):
            if new_access_level >= 0:
                if new_access_level == None:
                    self.users_access_table[new_owner_id] = self.users_access_table[user_id] + 1
                    print('owner added: ', new_owner_id, 'access_level:', self.users_access_table[new_owner_id])
                    return None
                elif self.users_access_table[user_id] < new_access_level:
                    self.users_access_table[new_owner_id] = new_access_level
                    print('owner added: ', new_owner_id, 'access_level:', new_access_level)
                    return None
                else:
                    return self.msg_permission_denied
            else:
                return self.msg_code_not_valid
        else:
            return self.msg_permission_denied

    def del_bot_owner(self, user_id, del_owner_id):
        if self.check_user_have_access(user_id,self.users_access_table):
            try:
                if self.users_access_table[user_id] < self.users_access_table[del_owner_id]:
                    del self.users_access_table[del_owner_id]
                    # print('owner deleted: ', del_owner_id)
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
        