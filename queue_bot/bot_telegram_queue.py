import signal
import os
import threading

from queue_bot.misc.logger import Logger
from queue_bot.misc.object_file_saver import ObjectSaver, FolderType
from queue_bot.misc.gdrive_saver import DriveSaver, DriveFolderType

import queue_bot.languages.bot_messages_rus as messages_rus
import queue_bot.bot_keyboards
import queue_bot.bot_command_handler as command_handler

from queue_bot.registered_manager import StudentsRegisteredManager
from queue_bot.queues_manager import QueuesManager
from queue_bot.students_queue import StudentsQueue
from queue_bot.updatable_message import UpdatableMessage
import queue_bot.bot_available_commands

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import MessageEntity


class QueueBot:
    language_pack = messages_rus
    keyboards = queue_bot.bot_keyboards
    available_commands = queue_bot.bot_available_commands

    last_queue_message = UpdatableMessage(default_keyboard=keyboards.move_queue)
    cur_students_message = UpdatableMessage()
    command_requested_answer = None

    def __init__(self, bot_token=None):
        # logger contains drive saver
        # and drive saver uses logger
        self.logger = Logger()
        self.object_saver = ObjectSaver(logger=self.logger)
        self.gdrive_saver = self.logger.drive_saver

        # this bot object passed for access to both classes inside one another
        self.registered_manager = StudentsRegisteredManager(self)
        self.queues_manager = QueuesManager(self)

        if bot_token is None:
            bot_token = self.get_token()

        self.updater = Updater(bot_token, use_context=True, user_sig_handler=self.handler_signal)
        self.init_updater_commands()

    def init_updater_commands(self):
        for command in self.available_commands.all_commands:
            self.updater.dispatcher.add_handler(CommandHandler(command.command_name, self.handle_text_command))

        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_message_reply_command))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_keyboard_chosen))
        self.updater.dispatcher.add_error_handler(self.handle_error)

    def refresh_last_queue_msg(self, update):
        if not self.last_queue_message.update_contents(self.queues_manager.get_queue_str(), update.effective_chat):
            self.logger.log('message failed to update')

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
        self.queues_manager.clear_finished_queues()
        self.queues_manager.save_to_file(self.object_saver)
        self.save_to_cloud()
        self.updater.stop()

    def handler_signal(self, signum, frame):
        print('handling signal ', signum)
        if signum in (signal.SIGTERM, signal.SIGINT):
            self.handler_stop()

    def save_queue_to_file(self):
        self.queues_manager.save_current_to_file()

    # paths inside .get_save_files() must match
    # with paths in load_from_cloud by folders to load correctly
    def save_to_cloud(self):

        self.gdrive_saver.update_file_list(self.registered_manager.get_save_files(), DriveFolderType.Root)
        self.gdrive_saver.update_file_list(self.queues_manager.get_save_files(), DriveFolderType.Queues)

        all_file_names = [
            file.name for file in (self.registered_manager.get_save_files()
                                   + self.queues_manager.get_save_files())
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
        self.queues_manager.load_file(self.object_saver)

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
        return self.queues_manager.get_queue() is not None

    def get_queue(self) -> StudentsQueue:
        return self.queues_manager.get_queue()

    def get_queue_log(self):
        return '\"not selected\"'

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

        # dump logs to another file
        new_log_path = self.logger.dump_to_file()
        # save file to cloud
        self.gdrive_saver.update_file_list([new_log_path], DriveFolderType.Log)

        # repeat error message to empty log file
        self.logger.delete_logs()
        self.logger.log_err(context.error)

