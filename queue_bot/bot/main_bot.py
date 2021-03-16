import signal
import os
import threading

from queue_bot.database import init_database

from queue_bot.objects import QueueStudents
from queue_bot.objects.queue_parameters import QueueParameters
from queue_bot.objects.registered_manager import RegisteredManager
from queue_bot.objects.queues_container import QueuesContainer

from queue_bot.commands import console_commands, command_handler

from queue_bot.bot.updatable_message import UpdatableMessage
import queue_bot.languages.bot_messages_rus as language_pack
import queue_bot.bot.keyboards as bot_keyboards


from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import MessageEntity


class QueueBot:
    language_pack = language_pack
    keyboards = bot_keyboards

    last_queue_message = UpdatableMessage(default_keyboard=keyboards.move_queue)
    cur_students_message = UpdatableMessage()
    command_requested_answer = None

    def __init__(self, bot_token=None):
        # todo use logging module

        # this bot object passed for access to both commands inside one another
        self.registered_manager = RegisteredManager()
        self.queues = QueuesContainer()

        if bot_token is None:
            bot_token = self.get_token()

        self.updater = Updater(bot_token, use_context=True, user_sig_handler=self.handler_signal)
        self.init_commands(self.updater)

        init_database()

    def init_commands(self, updater):
        for command in console_commands:
            updater.dispatcher.add_handler(CommandHandler(command.command_name, self.handle_text_command))

        updater.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_message_reply_command))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_keyboard_chosen))
        updater.dispatcher.add_error_handler(self.handle_error)

    def refresh_last_queue_msg(self, update):
        err_msg = self.last_queue_message.update_contents(self.queues.get_queue_str(), update.effective_chat)
        if err_msg is not None:
            self.logger.log('message failed to update | ' + err_msg)

    def start(self):
        self.logger.log('start')
        self.load_defaults()
        self.updater.start_polling()
        self.updater.idle()

    def stop(self):
        exit_thread = threading.Thread(target=self.handler_stop)
        exit_thread.start()
        exit_thread.join()

    def handler_stop(self):
        self.queues.clear_finished_queues()
        self.queues.save_to_file(self.object_saver)
        self.save_to_cloud()
        self.updater.stop()

    def handler_signal(self, signum, frame):
        print('handling signal ', signum)
        if signum in (signal.SIGTERM, signal.SIGINT):
            self.handler_stop()

    def save_queue_to_file(self):
        self.queues.save_current_to_file()

    # paths inside .get_save_files() must match
    # with paths in load_from_cloud by folders to load correctly
    def save_to_cloud(self):

        self.gdrive_saver.update_file_list(self.registered_manager.get_save_files(), DriveFolderType.Root)
        self.gdrive_saver.update_file_list(self.queues.get_save_files(), DriveFolderType.Queues)

        all_file_names = [
            file.name for file in (self.registered_manager.get_save_files()
                                   + self.queues.get_save_files())
        ]

        self.logger.log("saved files to cloud:\n" + "\n".join(all_file_names))
        print("saved files to cloud:\n" + "\n".join(all_file_names))

        dump_path = self.logger.dump_to_file()
        self.gdrive_saver.update_file_list([dump_path], DriveFolderType.Log)
        self.logger.delete_logs()

    def load_defaults(self):
        self.gdrive_saver.get_folder_files(self.registered_manager.get_save_files(), DriveFolderType.Root)
        self.gdrive_saver.get_all_folder_files(DriveFolderType.Queues, FolderType.QueuesData)

        self.registered_manager.load_file(self.object_saver)
        self.registered_manager.update_access_levels(self.object_saver)
        self.queues.load_file(self.object_saver)

    # loads default values from external file
    def save_registered_to_file(self):
        self.registered_manager.save_to_file(self.object_saver)
        self.gdrive_saver.update_file_list(self.registered_manager.get_save_files(), FolderType.Data)

    def get_token(self, path=None):
        if path is None:
            token = os.environ.get('TELEGRAM_TOKEN')
        else:
            token = self.object_saver.load(path)

        if token is None:
            self.logger.log('Fatal error: token is empty')
            raise ValueError('Fatal error: token is empty')

        return token

    def request_set(self, cls):
        self.command_requested_answer = cls

    def request_del(self):
        self.command_requested_answer = None

    def check_queue_selected(self):
        return self.queues.get_queue() is not None

    def get_queue(self) -> QueueStudents:
        return self.queues.get_queue()

    def new_queue(self, students=None, name=None):
        return self.queues.create_queue(QueueParameters(self.registered_manager, name, students))

    def handle_text_command(self, update, context):
        for entity in update.message.entities:
            if entity.type == MessageEntity.BOT_COMMAND:
                command_handler.handle_text_command(update, entity, self)

    def handle_keyboard_chosen(self, update, context):
        command_handler.handle_keyboard(update, self)
        update.callback_query.answer()

    def handle_message_reply_command(self, update, context):
        if self.command_requested_answer is not None:
            self.command_requested_answer.handle_request_access(update, self)

    def handle_error(self, update, context):
        self.logger.log_err(context.error)
        self.save_to_cloud()

        # repeat error message to empty log file
        self.logger.log_err(context.error)