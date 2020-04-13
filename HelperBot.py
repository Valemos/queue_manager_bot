import random as rnd
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

class QueueBot:
    
    def __init__(self,bot_token):
        self.updater = Updater(bot_token, use_context=True)

        self.updater.dispatcher.add_handler(CommandHandler('start', self.h_start))
        self.updater.dispatcher.add_handler(CommandHandler('get_queue', self.h_check_queue_status))
        self.updater.dispatcher.add_handler(CommandHandler('current_and_next', self.h_get_cur_and_next_students))
        self.updater.dispatcher.add_handler(CommandHandler('new_queue', self.h_create_queue))
        self.updater.dispatcher.add_handler(CommandHandler('new_random_queue', self.h_create_random_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_queue', self.h_edit_queue))
        self.updater.dispatcher.add_handler(CommandHandler('owner', self.h_add_new_owner))
        self.updater.dispatcher.add_handler(CommandHandler('del_owner', self.h_del_owner))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.h_message_text))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.h_keyboard_chosen))
        self.updater.dispatcher.add_error_handler(self.h_error)


        # ':' needed for correct commands split
        self.cmd_add_students = 'add_students'
        self.cmd_create_queue = 'create_queue'
        self.cmd_args_create_queue = ['simple','random']
        self.cmd_modify_students = 'modify_students'
        self.cmd_args_modify_queue = ['show_list','change_list','add_one_student','clear_list','move_to_end']
        self.cmd_move_queue = 'move_queue'
        self.cmd_args_move_queue = ['prev','next']
        self.cmd_set_owner = 'set_owner'
        self.cmd_del_owner = 'del_owner'

        # self.keyb_reply_add_students = InlineKeyboardMarkup([[InlineKeyboardButton('Добавить студентов',callback_data=self.cmd_add_students+':'+'True')],
                                                        # [InlineKeyboardButton('Отмена',callback_data=self.cmd_add_students+':'+'False')]])

        self.keyb_reply_create_queue = InlineKeyboardMarkup([[InlineKeyboardButton('Создать очередь',callback_data=self.cmd_create_queue+':'+self.cmd_args_create_queue[0])],
                                                        [InlineKeyboardButton('Отмена',callback_data=self.cmd_create_queue+':'+'False')]])
                                                        
        self.keyb_reply_create_random_queue = InlineKeyboardMarkup([[InlineKeyboardButton('Создать очередь',callback_data=self.cmd_create_queue+':'+self.cmd_args_create_queue[1])],
                                                        [InlineKeyboardButton('Отмена',callback_data=self.cmd_create_queue+':'+'False')]])

        self.keyb_modify_queue = InlineKeyboardMarkup([
            [InlineKeyboardButton('Показать очередь',               callback_data=self.cmd_modify_students+':'+self.cmd_args_modify_queue[0])],
            [InlineKeyboardButton('Переместить студента в конец',   callback_data=self.cmd_modify_students+':'+self.cmd_args_modify_queue[4])],
            [InlineKeyboardButton('Установить новую очередь',       callback_data=self.cmd_modify_students+':'+self.cmd_args_modify_queue[1])],
            [InlineKeyboardButton('Пересоздать очередь',            callback_data=self.cmd_modify_students+':'+self.cmd_args_modify_queue[3])]
        ])
        
        self.keyb_move_queue = InlineKeyboardMarkup([
            [InlineKeyboardButton('Следующий',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[1])],
            [InlineKeyboardButton('Предыдущий',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[0])]
        ])

        self.owners_access = {448309618:0}
        self.main_students_list = []
        self.cur_queue = []
        self.cur_queue_pos = 0

        self.msg_permission_denied = 'Нет разрешения'
        self.msg_code_not_valid = 'Внутренняя ошибка: Уровень доступа имеет неверный формат'
        self.msg_owner_not_found = 'Не владелец'
        self.msg_set_students = 'Чтобы установить список, введите новый список студентов\nон должен состоять из строк с именами студентов'

        # stores user who requested
        self.msg_request = (None,None) # first - user id; second - request code
        self.requests_by_code = {
            0 : (self.cmd_create_queue, self.cmd_args_create_queue[0]), # regular queue
            1 : (self.cmd_create_queue, self.cmd_args_create_queue[1]), # random queue
            2 : (self.cmd_set_owner, None),
            3 : (self.cmd_del_owner, None),
            4 : (self.cmd_modify_students, self.cmd_args_modify_queue[4])
        }
        self.request_codes = dict([(req,code) for code,req in self.requests_by_code.items()])
        
    def start(self):
        self.updater.start_polling()
        print('started')
        self.updater.idle()

    def h_message_text(self,update,context):
        
        if self.msg_request[0] is None:
            return
         
        print("requested:",self.msg_request)
        
        if self.msg_request[1] == 0 or self.msg_request[1] == 1:
            if update.message.from_user.id == self.msg_request[0]:
                try:
                    self.main_students_list = update.message.text.split('\n')
                    self.main_students_list = [i for i in self.main_students_list if not i=='']
                    
                    update.effective_chat.send_message('Студенты установлены')
                    if self.msg_request[1] == 0:
                        self.cur_queue = self.gen_queue(self.main_students_list)
                        self.cur_queue_pos = 0
                    elif self.msg_request[1] == 1:
                        self.cur_queue = self.gen_random_queue(self.main_students_list)
                        self.cur_queue_pos = 0
                        
                    update.effective_chat.send_message(self.get_queue_str(self.cur_queue), reply_markup)
                    
                except ValueError:
                    update.effective_chat.send_message('Неверный формат списка. Отмена операции')
                    
                except Exception:
                    logger.warning('Update "%s" caused error', update)
                    print('{0} \nUpdate caused error'.format(str(update)))
                    
                finally:
                    self.msg_request = (None,None)
            else:
                update.message.reply_text(self.msg_permission_denied)
            
        elif self.msg_request[1] == 2:
            if update.message.from_user.id == self.msg_request[0]:
                if update.message.forward_from is not None:
                    return_msg = self.add_new_bot_owner(update.effective_user.id,update.message.forward_from.id, 1)
                    if return_msg is not None:
                        update.message.reply_text(return_msg)
                    else:
                        update.message.reply_text('Владелец успешно установлен')
                    
                    self.msg_request = (None,None)
                else:
                    update.message.reply_text('Сообщение не переслано')

        elif self.msg_request[1] == 3:
            if update.message.from_user.id == self.msg_request[0]:
                if update.message.forward_from is not None:
                    return_msg = self.del_bot_owner(update.effective_user.id,update.message.forward_from.id)
                    if return_msg is not None:
                        update.message.reply_text(return_msg)
                    else:
                        update.message.reply_text('Владелец успешно удален')
                    
                    self.msg_request = (None,None)
                else:
                    update.message.reply_text('Сообщение не переслано')

        elif self.msg_request[1] == 4:
            if update.message.from_user.id == self.msg_request[0]:
                
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
                
    # Handlers
    def h_add_new_owner(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_access):
            if self.new_owner_req_user_id is None:                
                update.message.reply_text('Перешлите сообщение нового владельца боту')
                self.new_owner_req_user_id = update.message.from_user.id
                self.command_requested = True
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(self.msg_permission_denied)

    def h_del_owner(self, update, context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_access):
            if self.del_owner_req_user_id is None:                
                update.message.reply_text('Перешлите сообщение нового владельца боту')
                self.del_owner_req_user_id = update.message.from_user.id
                self.command_requested = True
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(self.msg_permission_denied)

    def h_start(self,update, context):
        if len(self.owners_access)==0:
            self.owners_access[update.message.from_user.id]=0
            update.message.reply_text('Первый владелец добавлен - '+update.message.from_user.username)

    def h_create_random_queue(self,update,context):
        if self.check_user_have_access(update.effective_user.id,self.owners_access):
            if len(self.cur_queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup=self.keyb_reply_create_random_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',reply_markup=self.keyb_reply_create_random_queue)
        else:
            update.effective_chat.send_message(self.msg_permission_denied)
            
    def h_create_queue(self,update,context):
        if self.check_user_have_access(update.effective_user.id,self.owners_access):
            if len(self.cur_queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup=self.keyb_reply_create_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',reply_markup = self.keyb_reply_create_queue)
        else:
            update.effective_chat.send_message(self.msg_permission_denied)

    def h_edit_queue(self,update,context):
        if self.check_user_have_access(update.message.from_user.id, self.owners_access):
            update.message.reply_text('Редактирование очереди', reply_markup=self.keyb_modify_queue)
        else:
            update.message.reply_text(self.msg_permission_denied)
        
    def h_check_queue_status(self,update,context):
        if len(self.cur_queue)==0:
            if self.check_user_have_access(update.effective_user.id, self.owners_access):
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup = self.keyb_reply_create_queue)
            else:
                update.effective_chat.send_message('Очереди нет.')
        else:
            update.effective_chat.send_message(self.get_queue_str(self.cur_queue,self.cur_queue_pos), reply_markup=self.keyb_move_queue)

    def h_get_cur_and_next_students(self,update,context):
        
        cur_stud, next_stud = self.get_cur_and_next(self.cur_queue_pos, self.cur_queue)
        
        msg = ''
        if cur_stud is not None: 
            msg = 'Сдает - {0}'.format(cur_stud)
        if next_stud is not None: 
            msg = msg + '\nГотовится - {0}'.format(next_stud)

        update.message.reply_text(msg)
        
    def parce_query_cmd(self,command):
        try:
            items = command.split(':')
            return items[0],''.join(items[1:])
        except Exception:
            return None,None

    def h_keyboard_chosen(self, update, context):
        query = update.callback_query
        if self.check_user_have_access(query.from_user.id,self.owners_access):
            cmd, args = self.parce_query_cmd(query.data)
            if cmd is not None:
                if cmd == self.cmd_move_queue:
                    if args==self.cmd_args_move_queue[0]:
                        # move prev
                        if self.cur_queue_pos > 0:
                            self.cur_queue_pos = self.cur_queue_pos - 1
                            query.edit_message_text(self.get_queue_str(self.cur_queue,self.cur_queue_pos),reply_markup=self.keyb_move_queue)
                    elif args==self.cmd_args_move_queue[1]:
                        # move next
                        if self.cur_queue_pos < len(self.cur_queue):
                            self.cur_queue_pos = self.cur_queue_pos+1
                            query.edit_message_text(self.get_queue_str(self.cur_queue,self.cur_queue_pos),reply_markup=self.keyb_move_queue)
                
                elif cmd == self.cmd_add_students:
                    if args=='True':
                        query.edit_message_text('Редактирование очереди', reply_markup=self.keyb_modify_queue)
                    else:
                        update.effective_message.delete()
                        
                elif cmd == self.cmd_create_queue:
                    if args == 'False':
                        if args == self.cmd_args_create_queue[0]:
                            self.cur_queue = self.gen_queue(self.main_students_list)
                            update.effective_chat.send_message(self.get_queue_str(self.cur_queue, self.cur_queue_pos), reply_markup = self.keyb_move_queue)
                        elif args == self.cmd_args_create_queue[1]:
                            self.cur_queue = self.gen_random_queue(self.main_students_list)
                            update.effective_chat.send_message(self.get_queue_str(self.cur_queue, self.cur_queue_pos), reply_markup = self.keyb_move_queue)
                        update.effective_message.delete()
                    else:
                        update.effective_chat.send_message(self.msg_set_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                        return
                        
                elif cmd == self.cmd_modify_students:

                    if args==self.cmd_args_modify_queue[0]:
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue,self.cur_queue_pos))
                            
                    elif args==self.cmd_args_modify_queue[1]:
                        update.effective_chat.send_message(self.msg_set_students)
                        self.msg_request = (update.effective_user.id, self.request_codes[(self.cmd_create_queue, self.cmd_args_create_queue[0])])
                        
                    elif args==self.cmd_args_modify_queue[3]:
                        self.cur_queue = self.gen_queue(self.main_students_list)
                        self.cur_queue_pos = 0
                        update.effective_chat.send_message('Очередь создана заново')
                        update.effective_chat.send_message(self.get_queue_str(self.cur_queue), reply_markup = self.keyb_move_queue)
                        
                    elif args==self.cmd_args_modify_queue[4]:
                        update.effective_chat.send_message('Пришлите номер студента в очереди')
                        self.msg_request = (update.effective_user.id, self.request_codes[(cmd, args)])
                        
            else:
                logger.warning('In update "%s" command: %s not vallid', update, query.data)
                print('In update \"{0}\" command: {1} not vallid'.format(update, query.data))
        else:
            update.message.reply_text(self.msg_permission_denied)
            
    def h_error(self,update,context):
        logger.warning('Update "%s" caused error "%s"', update, context.error) 
        
        
        
# Генерация очереди
    def gen_random_queue(self,items):
        if len(items)>0:
            shuff_items = list(items)
            rnd.shuffle(shuff_items)
            return shuff_items
        else:
            return []
            
    def gen_queue(self,items):
        if len(items)>0:
            return items
        else:
            return []

    def get_queue_str(self, queue, cur_pos = None):
        if len(queue) > 0:
            if cur_pos is not None:
            
                str_list = []

                cur_item, next_item = self.get_cur_and_next(cur_pos, queue)

                if cur_item is None:
                    return 'Очередь завершена'

                str_list.append('Сдает:')
                str_list.append('{0} - {1}'.format(cur_pos + 1, cur_item))
                str_list.append('\nСледующий:')
                if next_item is not None:
                    str_list.append('{0} - {1}'.format(cur_pos + 2, next_item))
                else:
                    str_list.append('Нет')
                    
                if (cur_pos + 2) < len(queue):
                    str_list.append('\nОставшиеся:')
                    for i in range(cur_pos + 2, len(queue)):
                        str_list.append('{0} - {1}'.format(i, queue[i]))
                        
                return '\n'.join(str_list)
            else:
                return 'Очередь:\n'+'\n'.join([str(i)+' - '+str(queue[i]) for i in range(len(queue))])
        else:
            return 'Очереди нет.'

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

    # Администрирование

    # Передача прав редактирования еще одному человеку
    def add_new_bot_owner(self, user_id, new_owner_id, new_access_level = 1):
        if self.check_user_have_access(user_id,self.owners_access):
            if new_access_level >= 0:
                if self.owners_access[user_id] < new_access_level:
                    self.owners_access[new_owner_id] = new_access_level
                    print('owner added: ', new_owner_id, 'access_level:', new_access_level)
                    return None
                else:
                    return self.msg_permission_denied
            else:
                return self.msg_code_not_valid
        else:
            return self.msg_permission_denied

    def del_bot_owner(self,user_id,del_owner_id):
        if self.check_user_have_access(user_id,self.owners_access):
            try:
                if self.owners_access[user_id] < self.owners_access[del_owner_id]:
                    del self.owners_access[del_owner_id]
                    print('owner deleted: ', del_owner_id)
                    return None
                else:
                    return self.msg_permission_denied
            except ValueError:
                return self.msg_owner_not_found
        else:
            return self.msg_permission_denied

    
    def check_user_have_access(self,user_id, access_levels_dict, access_level = 1):
        if user_id in access_levels_dict:
            if access_levels_dict[user_id]<=access_level:
                return True
        return False