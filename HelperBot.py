from logger import Logger
from varsaver import VariableSaver
from gdrive_saver import DriveSaver, FolderType
import bot_messages as messages
import bot_keyboards as keyboards
import bot_commands as commands
from registered_manager import StudentsRegisteredManager, AccessLevel
from students_queue import StudentsQueue, Student_EMPTY
import bot_command_handler

import atexit
import os

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import Chat


class QueueBot:

    command_handler = bot_command_handler.CommandHandler
    last_queue_message = None
    command_requested_answer = None

    def __init__(self, bot_token=None):
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
        if self.queue.queue_pos >= len(self.queue):
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
        # self.load_from_cloud()

        self.registered_manager.load_file(self.varsaver)
        self.registered_manager.update_access_levels(self.varsaver)
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
        if self.registered_manager.check_access(update.message.from_user.id):
            if self.command_requested_answer is None:
                update.message.reply_text(messages.get_user_message)
                self.command_requested_answer = commands.ManageUsers.AddAdmin
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(messages.permission_denied)

    def _h_del_owner(self, update, context):
        if self.registered_manager.check_access(update.message.from_user.id, AccessLevel.GOD):
            if self.command_requested_answer is None:
                update.message.reply_text(messages.get_user_message)
                self.command_requested_answer = commands.ManageUsers.RemoveAdmin
            else:
                update.message.reply_text('Уже запрошено, пришлите сообщение нового владельца')
        else:
            update.message.reply_text(messages.permission_denied)

    def _h_start(self, update, context):
        if len(self.registered_manager) == 0:
            self.registered_manager.append_new_user(update.message.from_user.username, update.message.from_user.id)
            self.registered_manager.set_god(update.message.from_user.id)
            update.message.reply_text('Первый владелец добавлен - ' + update.message.from_user.username)

            for admin in update.effective_chat.get_administrators():
                self.registered_manager.append_new_user(admin.user.username, admin.user.id)
                self.registered_manager.set_admin(admin.user.id)

            self.save_registered_to_file()
            update.effective_chat.send_message('Администраторы добавлены')

        elif self.registered_manager.check_access(update.effective_user.id):
            update.message.reply_text('Бот уже запущен.')

    def _h_stop(self, update, context):
        if self.registered_manager.check_access(update.effective_user.id):
            update.message.reply_text('Бот остановлен, и больше не принимает команд')
            self.updater.stop()
            exit()

    def _h_show_logs(self, update, context):
        if self.registered_manager.check_access(update.effective_user.id, AccessLevel.GOD):
            trim = 1000
            trimmed_msg = self.logger.get_logs()[-trim:]
            if len(trimmed_msg) >= trim:
                trimmed_msg = trimmed_msg[trimmed_msg.index('\n'):]

            update.effective_chat.send_message(trimmed_msg)

    def _h_create_random_queue(self, update, context):
        if self.registered_manager.check_access(update.effective_user.id):
            if len(self.queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',
                                                   reply_markup=keyboards.create_random_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',
                                                   reply_markup=keyboards.create_random_queue)
        else:
            update.message.reply_text(messages.permission_denied)

    def _h_create_queue(self, update, context):
        if self.registered_manager.check_access(update.effective_user.id):
            if len(self.queue) == 0:
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?',
                                                   reply_markup=keyboards.reply_create_queue)
            else:
                update.effective_chat.send_message('Удалить предыдущую очередь и создать новую?',
                                                   reply_markup=keyboards.reply_create_queue)
        else:
            update.message.reply_text(messages.permission_denied)

    def _h_edit_queue(self, update, context):
        if self.registered_manager.check_access(update.effective_user.id):
            update.message.reply_text('Редактирование очереди', reply_markup=keyboards.modify_queue)
        else:
            update.message.reply_text(messages.permission_denied)

    def _h_edit_registered(self, update, context):
        if self.registered_manager.check_access(update.effective_user.id):
            update.effective_chat.send_message('Редактирование пользователей', reply_markup=keyboards.modify_registered)
        else:
            update.message.reply_text(messages.permission_denied)

    def _h_check_queue_status(self, update, context):
        if len(self.queue) == 0:
            if self.registered_manager.check_access(update.effective_user.id):
                update.effective_chat.send_message('Очереди нет.\nХотите создать новую?', reply_markup=keyboards.reply_create_queue)
            else:
                update.effective_chat.send_message('Очереди нет.')
        else:
            msg = update.effective_chat.send_message(self.queue.get_string(), reply_markup=keyboards.move_queue)
            if update.effective_chat.type != Chat.PRIVATE:
                self.last_queue_message = msg

            self.logger.log('user {0} in {1} chat requested queue'.format(
                self.registered_manager.get_user_by_id(update.effective_user.id).log_str(), update.effective_chat.type))

    def _h_get_cur_and_next_students(self, update, context):
        update.effective_chat.send_message(self.queue.get_cur_and_next_str())

    def _h_i_finished(self, update, context):
        cur_user_id = update.effective_user.id
        if self.registered_manager.get_user_by_id(cur_user_id) is not Student_EMPTY:  # user is registered
            if self.queue.get_current() is not Student_EMPTY:
                self.queue.move_next()
                update.effective_chat.send_message(self.queue.get_cur_and_next_str())
            else:
                update.message.reply_text('{0}, вы не сдаете сейчас.'.format(
                    self.registered_manager.get_user_by_id(cur_user_id).get_string()))
        else:
            update.message.reply_text(messages.unknown_user)

        self.refresh_last_queue_msg()
        self.save_queue_to_file()
        self.logger.log('finished {0} - {1}'.format(cur_user_id, self.queue.get_current().log_str()))

    def _h_remove_me(self, update, context):
        if self.registered_manager.remove_by_id(update.effective_user.id):
            self.refresh_last_queue_msg()
            self.save_queue_to_file()

            update.message.reply_text('Вы удалены из очереди'.format(
                        self.registered_manager.get_user_by_id(update.effective_user.id)))

            self.logger.log('removed {0}'.format(self.registered_manager.get_user_by_id(update.effective_user.id).log_str()))
        else:
            update.message.reply_text('Вы не найдены в очереди')

    def _h_add_me_to_queue(self, update, context):
        student = self.registered_manager.get_user_by_id(update.effective_user.id)
        if student is not Student_EMPTY:
            self.queue.remove(student)
            self.queue.append(student)
        else:
            self.queue.append_new(update.effective_user.full_name, update.effective_user.id)

        update.message.reply_text('Вы записаны в очередь')

        self.refresh_last_queue_msg()
        self.save_queue_to_file()
        self.logger.log('added {0}'.format(self.queue.get_last()))

    def _h_error(self, update, context):
        print('Error: {0}'.format(context.error))
        self.logger.log(context.error)
        self.logger.save_to_cloud()

    def refresh_last_queue_msg(self):
        if self.last_queue_message is not None:
            new_text = self.queue.get_string()
            if self.last_queue_message.text != new_text:
                self.last_queue_message = self.last_queue_message.edit_text(new_text, reply_markup=keyboards.move_queue)
