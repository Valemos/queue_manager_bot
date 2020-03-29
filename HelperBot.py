import random as rnd
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

class QueueBot:
    
    def __init__(self,bot_token):
        self.updater = Updater(bot_token, use_context=True)

        self.updater.dispatcher.add_handler(CommandHandler('start', self.h_start))
        self.updater.dispatcher.add_handler(CommandHandler('queue', self.h_check_queue_status))
        self.updater.dispatcher.add_handler(CommandHandler('new_queue', self.h_create_queue))
        self.updater.dispatcher.add_handler(CommandHandler('students', self.h_add_students))
        self.updater.dispatcher.add_handler(CommandHandler('owner', self.h_add_new_owner))
        self.updater.dispatcher.add_handler(CommandHandler('del_owner', self.h_del_owner))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.h_message_text))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.h_keyboard_chosen))
        self.updater.dispatcher.add_error_handler(self.h_error)

        # ':' needed for correct commands split
        self.cmd_add_students = 'add_students'
        self.cmd_create_queue = 'create_queue'
        self.cmd_modify_students = 'modify_students'
        self.cmd_args_modify_students = ['show_list','change_list','add_one_student','clear_list']
        self.cmd_move_queue = 'move_queue'
        self.cmd_args_move_queue = ['prev','next']

        self.keyb_reply_add_students = InlineKeyboardMarkup([[InlineKeyboardButton('Добавить студентов',callback_data=self.cmd_add_students+':'+'True')],
                                                        [InlineKeyboardButton('Отмена',callback_data=self.cmd_add_students+':'+'False')]])

        self.keyb_reply_create_queue = InlineKeyboardMarkup([[InlineKeyboardButton('Создать очередь',callback_data=self.cmd_create_queue+':'+'True')],
                                                        [InlineKeyboardButton('Отмена',callback_data=self.cmd_create_queue+':'+'False')]])

        self.keyb_modify_students = InlineKeyboardMarkup([
            [InlineKeyboardButton('Показать список студентов',callback_data=self.cmd_modify_students+':'+self.cmd_args_modify_students[0])],
            [InlineKeyboardButton('Установить список',callback_data=self.cmd_modify_students+':'+self.cmd_args_modify_students[1])],
            [InlineKeyboardButton('Добавить одного студента',callback_data=self.cmd_modify_students+':'+self.cmd_args_modify_students[2])],
            [InlineKeyboardButton('Очистить список',callback_data=self.cmd_modify_students+':'+self.cmd_args_modify_students[3])],

        ])
        
        self.keyb_move_queue = InlineKeyboardMarkup([
            [InlineKeyboardButton('Следующий',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[1])],
            [InlineKeyboardButton('Предыдущий',callback_data=self.cmd_move_queue+':'+self.cmd_args_move_queue[0])]
        ])

        self.owners_access = {}
        self.main_students_list = []
        self.cur_queue = []
        self.cur_queue_pos = 0

        self.msg_permission_denied = 'Нет разрешения'
        self.msg_code_not_valid = 'Внутренняя ошибка: Уровень доступа имеет неверный формат'
        self.msg_owner_not_found = 'Не владелец'

        # stores user who requested
        self.command_requested = False
        self.students_list_req_user_id = None
        self.one_student_req_user_id = None
        self.new_owner_req_user_id = None
        self.del_owner_req_user_id = None
        
    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    # Генерация очереди
    def gen_random_queue(self,items):
        if len(items)>0:
            shuff_items = list(items)
            rnd.shuffle(shuff_items)
            return [(i+1,shuff_items[i]) for i in range(len(shuff_items))]
        else:
            return []

    def get_queue_str(self, queue, cur_pos = None):
        if len(queue)>0:
            if cur_pos is not None:
            
                str_list = []

                cur_item,next_item=self.get_cur_and_next(cur_pos,queue)

                str_list.append('Сдает:')
                if cur_item is not None: str_list.append('{0} - {1}'.format(*cur_item))
                str_list.append('Следующий:')
                if next_item is not None: str_list.append('{0} - {1}'.format(*next_item))
                str_list.append('Оставшиеся:')

                for i in range(cur_pos+2,len(queue)):
                    str_list.append('{0} - {1}'.format(*queue[i]))

                str_list.append('\nСдали:')

                for i in range(min(cur_pos,len(queue))):
                    str_list.append('{0} - {1}'.format(*queue[i]))
                
                return '\n'.join(str_list)
            else:
                return 'Очередь:\n'+'\n'.join([str(pos)+' - '+str(item) for pos,item in queue])
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
    def get_cur_and_next(self,pos,queue):
        if pos < len(queue)-1 and pos>=0:
            return queue[pos],queue[pos+1]
        elif pos == len(queue)-1:
            return queue[pos],None
        else:
            return None,None

    # Администрирование

    # Передача прав редактирования еще одному человеку
    def add_new_bot_owner(self, user_id, new_owner_id,new_access_level=1):
        if self.check_user_have_access(user_id,self.owners_access):
            if new_access_level >= 0:
                if self.owners_access[user_id] < new_access_level:
                    self.owners_access[new_owner_id]=new_access_level
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
                    return None
                else:
                    return self.msg_permission_denied
            except ValueError:
                return self.msg_owner_not_found
        else:
            return self.msg_permission_denied

    def check_user_have_access(self,user_id,access_levels_dict,access_level=1):
        if user_id in access_levels_dict:
            if access_levels_dict[user_id]<=access_level:
                return True
        return False

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

    def h_add_students(self,update,context):
        if self.check_user_have_access(update.effective_user.id,self.owners_access):
            update.effective_chat.send_message('Редактирование студентов', reply_markup=self.keyb_modify_students)
        else:
            update.effective_chat.send_message(self.msg_permission_denied)

    def h_create_queue(self,update,context):
        if self.check_user_have_access(update.effective_user.id,self.owners_access):
            if len(self.main_students_list)>0:
                self.cur_queue = self.gen_random_queue(self.main_students_list)
                update.effective_chat.send_message(self.get_queue_str(self.cur_queue,0),reply_markup=self.keyb_move_queue)
            else:
                update.effective_chat.send_message('В списке нет студентов, хотите добавить новых?',reply_markup=self.keyb_reply_add_students)
        else:
            update.effective_chat.send_message(self.msg_permission_denied)

    def h_check_queue_status(self,update,context):
        if len(self.cur_queue)==0:
            if self.check_user_have_access(update.effective_user.id,self.owners_access):
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',reply_markup=self.keyb_reply_create_queue)
            else:
                update.message.reply_text('Очереди нет.')
        else:
            update.effective_chat.send_message(self.get_queue_str(self.cur_queue,self.cur_queue_pos),reply_markup=self.keyb_move_queue)
            
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
                            self.cur_queue_pos = self.cur_queue_pos-1
                            query.edit_message_text(self.get_queue_str(self.cur_queue,self.cur_queue_pos),reply_markup=self.keyb_move_queue)
                    elif args==self.cmd_args_move_queue[1]:
                        # move next
                        if self.cur_queue_pos < len(self.cur_queue):
                            self.cur_queue_pos = self.cur_queue_pos+1
                            query.edit_message_text(self.get_queue_str(self.cur_queue,self.cur_queue_pos),reply_markup=self.keyb_move_queue)
                elif cmd == self.cmd_add_students:
                    if args=='True':
                        
                        query.edit_message_text('Редактирование студентов', reply_markup=self.keyb_modify_students)
                    else:
                        )
                        
                elif cmd == self.cmd_create_queue:
                    if args=='True':
                        
                        if len(self.main_students_list)==0:
                            query.edit_message_text('В списке нет студентов, хотите добавить новых?',reply_markup=self.keyb_reply_add_students)
                        else:
                            self.h_create_queue(update,context)
                            )
                    else:
                        )
                        
                elif cmd == self.cmd_modify_students:

                    # args = ['show_list','change_list','add_one_student','clear_list']

                    if args==self.cmd_args_modify_students[0]:
                        
                        if len(self.main_students_list)>0:
                            update.effective_chat.send_message('Текущий список студентов:\n'+'\n'.join(self.main_students_list))
                        else:
                            update.effective_chat.send_message('Нет студентов в списке')
                    elif args==self.cmd_args_modify_students[1]:
                        
                        update.effective_chat.send_message('Чтобы установить список, введите новый список студентов\nон должен состоять из блоков, разделенных \";\"')
                        self.students_list_req_user_id = update.effective_user.id
                        self.command_requested = True
                        return
                    elif args==self.cmd_args_modify_students[2]:
                        
                        update.effective_chat.send_message('Пришлите сообщение с именем нового студента')
                        self.one_student_req_user_id = update.effective_user.id
                        self.command_requested = True
                        return
                    elif args==self.cmd_args_modify_students[3]:
                        
                        self.main_students_list = []
                        update.effective_chat.send_message('Список очищен')
            else:
                logger.warning('In update "%s" command: %s not vallid', update, query.data)
        else:
            update.message.reply_text(self.msg_permission_denied)

    def h_message_text(self,update,context):
        if not self.command_requested:
            return
            
        if self.students_list_req_user_id is not None:
            if update.message.from_user.id==self.students_list_req_user_id or \
                self.check_user_have_access(update.message.from_user.id,self.owners_access):
                try:
                    self.main_students_list = update.message.text.split(';')
                    self.main_students_list = [i[:-1] if i.endswith('\n') and len(i)>1 else i for i in self.main_students_list]
                    self.main_students_list = [i[1:] if i.startswith('\n') and len(i)>1 else i for i in self.main_students_list]
                    self.main_students_list = sorted([i for i in self.main_students_list if not i==''])
                    
                    update.effective_chat.send_message('Студенты установлены')
                except ValueError:
                    update.effective_chat.send_message('Неверный формат списка. Отмена операции')
                except Exception:
                    logger.warning('Update "%s" caused error', update)
                finally:
                    self.students_list_req_user_id = None
            else:
                update.message.reply_text(self.msg_permission_denied)
            
        elif self.one_student_req_user_id is not None:
            if update.message.from_user.id==self.one_student_req_user_id or \
               self.check_user_have_access(update.message.from_user.id,self.owners_access):
                self.main_students_list.append(update.message.text)
                update.effective_chat.send_message('Студент добавлен')
                self.one_student_req_user_id = None
            
        elif self.new_owner_req_user_id is not None:
            if update.message.from_user.id==self.new_owner_req_user_id or \
               self.check_user_have_access(update.message.from_user.id,self.owners_access):
                if update.message.forward_from is not None:
                    return_msg = self.add_new_bot_owner(update.effective_user.id,update.message.forward_from.id, 1)
                    if return_msg is not None:
                        update.message.reply_text(return_msg)
                    else:
                        update.message.reply_text('Владелец успешно установлен')
                    
                    self.new_owner_req_user_id = None
                    self.command_requested = False
                else:
                    update.message.reply_text('Сообщение не переслано')
        
        elif self.del_owner_req_user_id is not None:
            if update.message.from_user.id==self.del_owner_req_user_id or \
               self.check_user_have_access(update.message.from_user.id,self.owners_access):
                if update.message.forward_from is not None:
                    return_msg = self.del_bot_owner(update.effective_user.id,update.message.forward_from.id)
                    if return_msg is not None:
                        update.message.reply_text(return_msg)
                    else:
                        update.message.reply_text('Владелец успешно удален')
                    
                    self.del_owner_req_user_id = None
                    self.command_requested = False
                else:
                    update.message.reply_text('Сообщение не переслано')
       
    def h_error(self,update,context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)