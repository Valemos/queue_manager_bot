from queue_bot.logger import Logger
from queue_bot.object_file_saver import ObjectSaver
from queue_bot.gdrive_saver import DriveSaver, DriveFolder

import queue_bot.languages.bot_messages_rus as messages_rus
import queue_bot.bot_commands as commands
import queue_bot.bot_keyboards
import queue_bot.bot_command_handler as command_handler

from queue_bot.registered_manager import StudentsRegisteredManager, AccessLevel
from queue_bot.multiple_queues import QueuesManager
from queue_bot.students_queue import StudentsQueue
from queue_bot.updatable_message import UpdatableMessage
from queue_bot.subject_choice_manager import SubjectChoiceManager

import atexit
import os

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler


class QueueBot:
    language_pack = messages_rus
    keyboards = queue_bot.bot_keyboards

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
        self.updater.dispatcher.add_handler(CommandHandler('i_finished', self.h_i_finished))
        self.updater.dispatcher.add_handler(CommandHandler('remove_me', self.h_remove_me))
        self.updater.dispatcher.add_handler(CommandHandler('add_me', self.h_add_me))
        self.updater.dispatcher.add_handler(CommandHandler('get_queue', self.h_get_queue))
        self.updater.dispatcher.add_handler(CommandHandler('start', self.h_start))
        self.updater.dispatcher.add_handler(CommandHandler('stop', self.h_stop))
        self.updater.dispatcher.add_handler(CommandHandler('logs', self.h_show_logs))
        self.updater.dispatcher.add_handler(CommandHandler('current_and_next', self.send_cur_and_next))
        self.updater.dispatcher.add_handler(CommandHandler('new_queue', self.h_create_queue))
        self.updater.dispatcher.add_handler(CommandHandler('new_random_queue', self.h_create_random_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_queue', self.h_edit_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_registered', self.h_edit_registered))
        self.updater.dispatcher.add_handler(CommandHandler('admin', self.h_add_new_admin))
        self.updater.dispatcher.add_handler(CommandHandler('del_admin', self.h_del_admin))
        self.updater.dispatcher.add_handler(CommandHandler('setup_subject', self.h_setup_choices))
        self.updater.dispatcher.add_handler(CommandHandler('allow_choose', self.h_allow_pick_subjects))
        self.updater.dispatcher.add_handler(CommandHandler('stop_choose', self.h_stop_pick_subjects))
        self.updater.dispatcher.add_handler(CommandHandler('remove_choice', self.h_remove_choice))
        self.updater.dispatcher.add_handler(CommandHandler('ch', self.h_choice))
        self.updater.dispatcher.add_handler(CommandHandler('get_choice_table', self.h_get_choices_excel_file))
        self.updater.dispatcher.add_handler(CommandHandler('get_subjects', self.h_show_choices))
        self.updater.dispatcher.add_handler(CommandHandler('select_queue', self.h_select_queue))
        self.updater.dispatcher.add_handler(CommandHandler('delete_queue', self.h_delete_queue))
        self.updater.dispatcher.add_handler(CommandHandler('admin_help', self.h_show_admin_help))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.h_message_text))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.h_keyboard_chosen))
        self.updater.dispatcher.add_error_handler(self.h_error)

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
        self.gdrive_saver.update_file_list(self.queues_manager.get_save_files(), DriveFolder.Queues)

        self.logger.log('saved to cloud')

    def load_from_cloud(self):
        self.gdrive_saver.get_files_from_drive(self.registered_manager.get_save_files(), DriveFolder.HelperBotData)
        self.gdrive_saver.get_files_from_drive(self.choice_manager.get_save_files(), DriveFolder.SubjectChoices)

        self.queues_manager.load_queues_from_drive(self.gdrive_saver, self.object_saver)

    def load_defaults(self):
        self.load_from_cloud()

        self.registered_manager.load_file(self.object_saver)
        self.registered_manager.update_access_levels(self.object_saver)
        self.choice_manager.load_file(self.object_saver)
        self.queues_manager.load_file(self.object_saver)

        self.logger.log('loaded data')

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

    def h_keyboard_chosen(self, update, context):
        command_handler.handle(update, self)
        update.callback_query.answer()

    def request_set(self, cls):
        self.command_requested_answer = cls

    def request_del(self):
        self.command_requested_answer = None

    def get_queue(self) -> StudentsQueue:
        return self.queues_manager.get_queue()

    def h_message_text(self, update, context):
        if self.command_requested_answer is None:
            return

        self.logger.log('handled ' + self.command_requested_answer.str())
        self.command_requested_answer.handle_request(update, self)

    def h_add_new_admin(self, update, context):
        commands.ManageAccessRights.AddAdmin.handle_command(update, self)

    def h_del_admin(self, update, context):
        commands.ManageAccessRights.RemoveAdmin.handle_command(update, self)

    def h_start(self, update, context):
        commands.General.Start.handle_command(update, self)

    def h_stop(self, update, context):
        commands.General.Stop.handle_command(update, self)

    def h_show_logs(self, update, context):
        commands.General.ShowLogs.handle_command(update, self)

    def h_create_random_queue(self, update, context):
        commands.ManageQueues.CreateRandom.handle_command(update, self)

    def h_create_queue(self, update, context):
        commands.ManageQueues.CreateSimple.handle_command(update, self)

    def h_edit_queue(self, update, context):
        commands.ModifyCurrentQueue.ShowMenu.handle_command(update, self)

    def h_delete_queue(self, update, context):
        commands.ManageQueues.DeleteQueue.handle_command(update, self)

    def h_select_queue(self, update, context):
        commands.ManageQueues.SelectOtherQueue.handle_command(update, self)

    def h_edit_registered(self, update, context):
        commands.ModifyRegistered.ShowMenu.handle_command(update, self)

    def h_get_queue(self, update, context):
        commands.UpdateQueue.ShowCurrent.handle_command(update, self)

    def send_cur_and_next(self, update, context=None):
        commands.UpdateQueue.ShowCurrentAndNext.handle_command(update, self)

    def h_i_finished(self, update, context):
        commands.ModifyCurrentQueue.StudentFinished.handle_command(update, self)

    def h_remove_me(self, update, context):
        commands.ModifyCurrentQueue.RemoveMe.handle_command(update, self)

    def h_add_me(self, update, context):
        commands.ModifyCurrentQueue.AddMe.handle_command(update, self)

    def h_error(self, update, context):
        string = '{0}: {1} '.format(context.error.__qualname__, str(context.error))
        print(string)
        self.logger.log(string)
        self.logger.save_to_cloud()

    def h_setup_choices(self, update, context):
        commands.CollectSubjectChoices.CreateNewCollectFile.handle_command(update, self)

    def h_allow_pick_subjects(self, update, context):
        commands.CollectSubjectChoices.StartChoose.handle_command(update, self)

    def h_stop_pick_subjects(self, update, context):
        commands.CollectSubjectChoices.StopChoose.handle_command(update, self)

    def h_show_choices(self, update, context):
        commands.CollectSubjectChoices.ShowCurrentChoices.handle_command(update, self)

    def h_choice(self, update, context):
        commands.CollectSubjectChoices.Choose.handle_command(update, self)

    def h_remove_choice(self, update, context):
        commands.CollectSubjectChoices.RemoveChoice.handle_command(update, self)

    def h_show_admin_help(self, update, context):
        commands.Help.ForAdmin.handle_command(update, self)

    def h_get_choices_excel_file(self, update, context):
        commands.CollectSubjectChoices.GetExcelFile.handle_command(update, self)
