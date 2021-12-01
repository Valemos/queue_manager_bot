import os
import signal
import threading

from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler

import queue_bot.command_handling.handlers as command_handler
from queue_bot.bot import command_collections, keyboards
from queue_bot.bot.updatable_message import UpdatableMessage
from queue_bot.objects.queues_manager import get_chat_queues


class QueueBot:
    last_queue_message = UpdatableMessage(default_keyboard=keyboards.move_queue)
    cur_students_message = UpdatableMessage()
    command_requested_answer = None

    def __init__(self, bot_token=None):
        # this bot object passed for access to both classes inside one another
        bot_token = bot_token if bot_token is not None else os.environ['TELEGRAM_TOKEN']

        self.updater = Updater(bot_token, use_context=True, user_sig_handler=self.handler_signal)
        self.init_updater_commands()

    def init_updater_commands(self):
        for command in command_collections.all_commands:
            self.updater.dispatcher.add_handler(CommandHandler(command.command_name, self.handle_text_command))

        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_message_reply_command))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_keyboard_chosen))
        self.updater.dispatcher.add_error_handler(self.handle_error)

    def refresh_last_queue_msg(self, update):

        try:
            self.last_queue_message.update_contents(
                get_chat_queues(update.effective_chat.id).get_queue_message(),
                update.effective_chat
            )
        except Exception as exc:
            self.logger.log('message failed to update | ' + str(exc.args))

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def stop(self):
        exit_thread = threading.Thread(target=self.handler_stop)
        exit_thread.start()
        exit_thread.join()

    def handler_stop(self):
        self.updater.stop()

    def handler_signal(self, signum, frame):
        print('handling signal ', signum)
        if signum in (signal.SIGTERM, signal.SIGINT):
            self.handler_stop()

    def request_set(self, cls):
        self.command_requested_answer = cls

    def request_del(self):
        self.command_requested_answer = None

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

        # repeat error message to empty log file
        self.logger.log_err(context.error)
