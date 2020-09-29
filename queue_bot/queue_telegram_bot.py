from queue_bot.logger import Logger
from queue_bot.object_file_saver import ObjectSaver
from queue_bot.gdrive_saver import DriveSaver, DriveFolder

import queue_bot.languages.bot_messages_rus as messages_rus
import queue_bot.bot_commands as commands
import queue_bot.bot_keyboards
import queue_bot.bot_command_handler as command_handler

from queue_bot.registered_manager import StudentsRegisteredManager, AccessLevel
from queue_bot.multiple_queues import QueuesManager
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
        self.updater.dispatcher.add_handler(CommandHandler('i_finished', self._h_i_finished))
        self.updater.dispatcher.add_handler(CommandHandler('remove_me', self._h_remove_me))
        self.updater.dispatcher.add_handler(CommandHandler('add_me', self._h_add_me))
        self.updater.dispatcher.add_handler(CommandHandler('start', self._h_start))
        self.updater.dispatcher.add_handler(CommandHandler('stop', self._h_stop))
        self.updater.dispatcher.add_handler(CommandHandler('logs', self._h_show_logs))
        self.updater.dispatcher.add_handler(CommandHandler('get_queue', self._h_get_queue))
        self.updater.dispatcher.add_handler(CommandHandler('current_and_next', self.send_cur_and_next))
        self.updater.dispatcher.add_handler(CommandHandler('new_queue', self._h_create_queue))
        self.updater.dispatcher.add_handler(CommandHandler('new_random_queue', self._h_create_random_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_queue', self._h_edit_queue))
        self.updater.dispatcher.add_handler(CommandHandler('edit_registered', self._h_edit_registered))
        self.updater.dispatcher.add_handler(CommandHandler('admin', self._h_add_new_admin))
        self.updater.dispatcher.add_handler(CommandHandler('del_admin', self._h_del_admin))
        self.updater.dispatcher.add_handler(CommandHandler('setup_subject', self._h_setup_choices))
        self.updater.dispatcher.add_handler(CommandHandler('allow_choose', self._h_allow_pick_subjects))
        self.updater.dispatcher.add_handler(CommandHandler('stop_choose', self._h_stop_pick_subjects))
        self.updater.dispatcher.add_handler(CommandHandler('remove_choice', self._h_remove_choice))
        self.updater.dispatcher.add_handler(CommandHandler('ch', self._h_choice))
        self.updater.dispatcher.add_handler(CommandHandler('get_choice_table', self._h_get_choices_excel_file))
        self.updater.dispatcher.add_handler(CommandHandler('get_subjects', self._h_show_choices))
        self.updater.dispatcher.add_handler(CommandHandler('select_queue', self._h_select_queue))
        self.updater.dispatcher.add_handler(CommandHandler('delete_queue', self._h_delete_queue))
        self.updater.dispatcher.add_handler(CommandHandler('admin_help', self._h_show_admin_help))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self._h_message_text))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self._h_keyboard_chosen))
        self.updater.dispatcher.add_error_handler(self._h_error)

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

    def _h_keyboard_chosen(self, update, context):
        command_handler.handle(update, self)
        update.callback_query.answer()

    def request_set(self, cls):
        self.command_requested_answer = cls

    def request_del(self):
        self.command_requested_answer = None

    def get_queue(self):
        return self.queues_manager.get_queue()

    # command handlers
    def handle_access_check(self, update, access_level=AccessLevel.ADMIN, check_chat_private=True):
        if self.registered_manager.check_access(update, access_level, check_chat_private):
            return True
        else:
            self.logger.log('user {0} tried to get access to {1} command'.format(
                                self.registered_manager.get_user_by_update(update),
                                access_level.name))
            update.message.reply_text(self.language_pack.permission_denied)
            return False

    def _h_message_text(self, update, context):
        if self.command_requested_answer is None:
            return

        self.logger.log('handled ' + self.command_requested_answer.str())
        self.command_requested_answer.handle_request(update, self)

    def _h_add_new_admin(self, update, context):
        self.handle_admin_command(update, commands.ManageUsers.AddAdmin)

    def _h_del_admin(self, update, context):
        self.handle_admin_command(update, commands.ManageUsers.RemoveAdmin)

    def handle_admin_command(self, update, cmd):
        if self.registered_manager.check_access(update, cmd.access_requirement):
            if self.command_requested_answer is None:
                update.message.reply_text(self.language_pack.get_user_message)
                self.request_set(cmd)
            else:
                update.message.reply_text(self.language_pack.already_requested_send_message)
        else:
            self.logger.log('user {0} tried to get access to admin command'
                            .format(self.registered_manager.get_user_by_update(update)))
            update.message.reply_text(self.language_pack.permission_denied)

    def _h_start(self, update, context):
        if len(self.registered_manager) == 0:
            self.registered_manager.append_new_user(update.message.from_user.username, update.message.from_user.id)
            self.registered_manager.set_god(update.message.from_user.id)
            update.message.reply_text(
                self.language_pack.first_user_added.format(update.message.from_user.username))

            for admin in update.effective_chat.get_administrators():
                self.registered_manager.append_new_user(admin.user.username, admin.user.id)
                self.registered_manager.set_admin(admin.user.id)

            self.save_registered_to_file()
            update.effective_chat.send_message(self.language_pack.admins_added)

        elif self.registered_manager.check_access(update):
            update.message.reply_text(self.language_pack.bot_already_running)

    def _h_stop(self, update, context):
        if self.registered_manager.check_access(update, AccessLevel.GOD):
            update.message.reply_text(self.language_pack.bot_stopped)
            self.save_before_stop()
            exit(0)

    def _h_show_logs(self, update, context):
        if self.registered_manager.check_access(update, AccessLevel.GOD):
            trim = 1000
            trimmed_msg = self.logger.get_logs()[-trim:]
            if len(trimmed_msg) >= trim:
                trimmed_msg = trimmed_msg[trimmed_msg.index('\n'):]

            update.effective_chat.send_message(trimmed_msg)

    # if queue can be updated, returns true
    def generate_queue_message(self, update, keyboard):
        if self.queues_manager.queue_empty():
            if self.handle_access_check(update):
                if len(self.queues_manager) == 0:  # no queues
                    msg = self.language_pack.queue_not_exists_create_new
                else:
                    msg = self.language_pack.select_queue_or_create_new
                update.effective_chat.send_message(msg, reply_markup=keyboard)
            else:  # user not admin
                update.effective_chat.send_message(self.language_pack.queue_not_exists)
        else:
            return True

    def _h_create_random_queue(self, update, context):
        if update.callback_query is None:
            self.generate_queue_message(update, self.keyboards.create_random_queue)
        else:
            commands.ManageQueues.CreateRandom.handle_request(update, self)

    def _h_create_queue(self, update, context):
        if update.message.text == '/new_queue':
            self.generate_queue_message(update, self.keyboards.create_simple_queue)
        else:
            commands.ManageQueues.CreateSimple.handle_request(update, self)

    def _h_edit_queue(self, update, context):
        if self.handle_access_check(update):
            update.message.reply_text(self.language_pack.title_edit_queue,
                                      reply_markup=self.keyboards.modify_queue)

    def _h_delete_queue(self, update, context):
        if self.handle_access_check(update):
            keyboard = self.queues_manager.generate_choice_keyboard(commands.ManageQueues.DeleteQueue)
            update.message.reply_text(self.language_pack.title_select_queue, reply_markup=keyboard)

    def _h_select_queue(self, update, context):
        if self.handle_access_check(update):
            keyboard = self.queues_manager.generate_choice_keyboard(commands.ManageQueues.ChooseOtherQueue)
            update.message.reply_text(self.language_pack.title_select_queue, reply_markup=keyboard)

    def _h_edit_registered(self, update, context):
        if self.handle_access_check(update):
            update.effective_chat.send_message(self.language_pack.title_edit_registered,
                                               reply_markup=self.keyboards.modify_registered)

    def _h_get_queue(self, update, context):
        if self.generate_queue_message(update, self.keyboards.create_simple_queue):
            self.last_queue_message.resend(self.queues_manager.get_queue_str(), update.effective_chat)
        self.logger.log('user {0} in {1} chat requested queue'.format(
            self.registered_manager.get_user_by_update(update).str_name_id(), update.effective_chat.type))

    def send_cur_and_next(self, update, context=None):
        self.cur_students_message.resend(self.queues_manager.get_queue().get_cur_and_next_str(), update.effective_chat)

    def _h_i_finished(self, update, context):
        student_finished = self.registered_manager.get_user_by_update(update)

        if student_finished == self.queues_manager.get_queue().get_current():  # finished user currently first
            self.queues_manager.get_queue().move_next()
            self.send_cur_and_next(update)
        else:
            update.message.reply_text(self.language_pack.your_turn_not_now
                                      .format(self.registered_manager.get_user_by_update(update).str()))
            self.queues_manager.get_queue()

        self.last_queue_message.update_contents(self.queues_manager.get_queue_str(), update.effective_chat)
        self.save_queue_to_file()
        self.logger.log('finished: {0}'.format(self.queues_manager.get_queue().get_current().str_name_id()))

    def _h_remove_me(self, update, context):
        commands.ModifyCurrentQueue.RemoveMe.handle(update, self)

    def _h_add_me(self, update, context):
        commands.ModifyCurrentQueue.AddMe.handle(update, self)

    def _h_error(self, update, context):
        string = '{0}: {1}'.format(context.error.__qualname__, context.error)
        print(string)
        self.logger.log(string)
        self.logger.save_to_cloud()

    def _h_setup_choices(self, update, context):
        if self.handle_access_check(update):
            commands.CollectSubjectChoices.CreateNewCollectFile.handle(update, self)

    def _h_allow_pick_subjects(self, update, context):
        if self.registered_manager.check_access(update, check_chat_private=False):
            commands.CollectSubjectChoices.StartChoose.handle(update, self)

    def _h_stop_pick_subjects(self, update, context):
        if self.handle_access_check(update, check_chat_private=False):
            commands.CollectSubjectChoices.StopChoose.handle(update, self)

    def _h_show_choices(self, update, context):
        if self.handle_access_check(update):
            commands.CollectSubjectChoices.ShowCurrentChoices.handle(update, self)

    def _h_choice(self, update, context):
        if self.handle_access_check(update, AccessLevel.USER):
            commands.CollectSubjectChoices.Choose.handle_request(update, self)

    def _h_remove_choice(self, update, context):
        commands.CollectSubjectChoices.RemoveChoice.handle(update, self)

    def _h_show_admin_help(self, update, context):
        if self.handle_access_check(update, check_chat_private=False):
            commands.Help.ForAdmin.handle(update, self)

    def _h_get_choices_excel_file(self, update, context):
        if self.handle_access_check(update, check_chat_private=False):
            commands.CollectSubjectChoices.GetExcelFile.handle(update, self)
