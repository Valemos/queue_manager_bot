from queue_bot.logger import Logger
from queue_bot.object_file_saver import ObjectSaver, FolderType
from queue_bot.gdrive_saver import DriveSaver, DriveFolder

import queue_bot.languages.bot_messages_rus as messages_rus
import queue_bot.bot_keyboards
import queue_bot.bot_command_handler as command_handler

from queue_bot.registered_manager import StudentsRegisteredManager
from queue_bot.multiple_queues import QueuesManager
from queue_bot.students_queue import StudentsQueue
from queue_bot.updatable_message import UpdatableMessage
from queue_bot.subject_choice_manager import SubjectChoiceManager
import queue_bot.bot_available_commands

import atexit
import os

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import MessageEntity


class QueueBot:
    language_pack = messages_rus
    keyboards = queue_bot.bot_keyboards
    available_commands = queue_bot.bot_available_commands

    last_queue_message = UpdatableMessage(default_keyboard=keyboards.move_queue)
    cur_students_message = UpdatableMessage()
    subject_choices_message = UpdatableMessage(default_keyboard=keyboards.help_subject_choice)
    command_requested_answer = None

    def __init__(self, bot_token=None):
        self.logger = Logger()
        self.object_saver = ObjectSaver(logger=self.logger)
        self.gdrive_saver = DriveSaver()

        # this bot object passed for access to both classes inside one another
        self.registered_manager = StudentsRegisteredManager(self)
        self.queues_manager = QueuesManager(self)

        # subject choices
        self.choice_manager = SubjectChoiceManager()

        if bot_token is None:
            bot_token = self.get_token()

        self.updater = Updater(bot_token, use_context=True)
        self.init_updater_commands()

        atexit.register(self.save_before_stop)

    def init_updater_commands(self):
        for command in self.available_commands.all_commands:
            self.updater.dispatcher.add_handler(CommandHandler(command.command_name, self.handle_command_selected))

        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_message_text))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_keyboard_chosen))
        # self.updater.dispatcher.add_error_handler(self.handle_error)

    def refresh_last_queue_msg(self, update):
        if not self.last_queue_message.update_contents(self.queues_manager.get_queue_str(), update.effective_chat):
            self.logger.log('message failed to update')

    def start(self):
        self.logger.log('start')
        self.load_defaults()
        self.updater.start_polling()
        self.updater.idle()

    def save_before_stop(self):
        # clear queue, if it was fully completed
        self.queues_manager.clear_finished_queues()
        self.queues_manager.save_to_file(self.object_saver)
        self.save_to_cloud()

    def save_queue_to_file(self):
        self.queues_manager.save_current_to_file()

    # paths inside .get_save_files() must match
    # with paths in load_from_cloud by folders to load correctly
    def save_to_cloud(self):
        dump_path = self.logger.dump_to_file()
        self.gdrive_saver.update_file_list([dump_path], DriveFolder.Log)

        self.gdrive_saver.update_file_list(self.registered_manager.get_save_files(), DriveFolder.HelperBotData)
        self.gdrive_saver.update_file_list(self.choice_manager.get_save_files(), DriveFolder.SubjectChoices)


        self.gdrive_saver.clear_drive_folder(DriveFolder.Queues)
        self.gdrive_saver.update_file_list(self.queues_manager.get_save_files(), DriveFolder.Queues)

        self.logger.log('saved to cloud')

    def load_from_cloud(self):
        self.gdrive_saver.get_files_from_drive(self.registered_manager.get_save_files(), DriveFolder.HelperBotData)
        self.gdrive_saver.get_files_from_drive(self.choice_manager.get_save_files(), DriveFolder.SubjectChoices)
        self.gdrive_saver.load_folder_files(DriveFolder.Queues, FolderType.QueuesData)

    def load_defaults(self):
        self.load_from_cloud()
        self.registered_manager.load_file(self.object_saver)
        self.registered_manager.update_access_levels(self.object_saver)
        self.choice_manager.load_file(self.object_saver)
        self.queues_manager.load_file(self.object_saver)

    # loads default values from external file
    def save_registered_to_file(self):
        self.registered_manager.save_to_file(self.object_saver)
        # self.gdrive_saver.update_file_list(self.registered_manager.get_save_files(), FolderType.Data)

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

    def handle_command_selected(self, update, context):
        for entity in update.message.entities:
            if entity.type == MessageEntity.BOT_COMMAND:
                command_handler.handle_text_command(update, entity, self)

    def handle_keyboard_chosen(self, update, context):
        command_handler.handle_keyboard(update, self)
        update.callback_query.answer()

    def handle_message_text(self, update, context):
        if self.command_requested_answer is not None:
            self.command_requested_answer.handle_request_access(update, self)

    def handle_error(self, update, context):
        print(context.error.message)
        self.logger.log(context.error.message)
        self.logger.save_to_cloud()
