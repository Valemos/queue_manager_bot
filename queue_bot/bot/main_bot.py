import logging
import pickle
import signal
import os
import threading

from queue_bot.database import init_database

from queue_bot.objects.queue_parameters import QueueParameters
from queue_bot.objects.registered_manager import RegisteredManager
from queue_bot.objects.queues_container import QueuesContainer

from queue_bot.command_handling import command_handler, console_commands

from queue_bot.bot.updatable_message import UpdatableMessage
import queue_bot.languages.bot_messages_rus as language_pack
import queue_bot.bot.keyboards as bot_keyboards


from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import MessageEntity


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class QueueBot:
    language_pack = language_pack
    keyboards = bot_keyboards

    last_queue_message = UpdatableMessage(default_keyboard=keyboards.move_queue)
    cur_students_message = UpdatableMessage()
    command_requested_answer = None

    def __init__(self, bot_token=None):
        init_database()

        # this bot object passed for access to both commands inside one another
        self.registered_manager = RegisteredManager()
        self.queues = QueuesContainer()

        if bot_token is None:
            bot_token = self.get_token()

        self.updater = Updater(bot_token, use_context=True, user_sig_handler=self.handler_signal)
        self.init_commands(self.updater)

    def init_commands(self, updater):
        for command in console_commands:
            updater.dispatcher.add_handler(CommandHandler(command.command_name, self.handle_text_command))

        updater.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_message_reply_command))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_keyboard_chosen))
        updater.dispatcher.add_error_handler(self.handle_error)

    def refresh_last_queue_msg(self, update):
        err_msg = self.last_queue_message.update_contents(self.queues.get_queue_str(), update.effective_chat)
        if err_msg is not None:
            log.warning('message failed to update | ' + err_msg)

    def start(self):
        log.info('bot started')
        self.updater.start_polling()
        self.updater.idle()

    def stop(self):
        exit_thread = threading.Thread(target=self.handler_stop)
        exit_thread.start()
        exit_thread.join()

    def handler_stop(self):
        self.queues.clear_finished_queues()
        self.updater.stop()

    def handler_signal(self, signum, frame):
        print('handling signal ', signum)
        if signum in (signal.SIGTERM, signal.SIGINT):
            self.handler_stop()

    @staticmethod
    def get_token(path=None):
        token = None
        if path is None:
            token = os.environ.get('TELEGRAM_TOKEN')
        else:
            if path.exists():
                token = pickle.load(path)

        if token is None:
            msg = f'Fatal error: token is empty and {str(path)} does not exists'
            log.error(msg)
            raise ValueError(msg)

        return token

    def request_set(self, cls):
        self.command_requested_answer = cls

    def request_del(self):
        self.command_requested_answer = None

    def check_queue_selected(self):
        return self.queues.get_queue() is not None

    def get_queue(self):
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

    @staticmethod
    def handle_error(update, context):
        log.error(context.error)
