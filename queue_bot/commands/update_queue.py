import logging

from queue_bot.languages import command_descriptions_rus as commands_descriptions

from .abstract_command import AbstractCommand
from .logging_shortcuts import log_queue, log_user


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ShowCurrentQueue(AbstractCommand):
    command_name = 'get_queue'
    description = commands_descriptions.get_queue_descr

    @classmethod
    def handle_reply(cls, update, bot):
        # if queue not selected, but it exists
        if bot.queues.selected_queue is None and len(bot.queues) > 0:
            update.effective_chat.send_message(bot.language_pack.select_queue_or_create_new)
        else:
            bot.last_queue_message.resend(
                bot.queues.get_queue_str(),
                update.effective_chat,
                bot.keyboards.move_queue)

        log.info(log_user(update, bot, f'in chat {update.effective_chat.type} requested queue'))


class Refresh(AbstractCommand):
    @classmethod
    def handle_request(cls, update, bot):
        if not bot.last_queue_message.message_exists(update.effective_chat):
            update.effective_message.delete()
        err_msg = bot.last_queue_message.update_contents(bot.queues.get_queue_str(), update.effective_chat)
        if err_msg is not None:
            log.warning(log_queue(update, bot, err_msg))

        log.info(log_user(update, bot, 'refreshed queue'))


class ShowCurrentAndNextStudent(AbstractCommand):
    command_name = 'current_and_next'
    description = commands_descriptions.current_and_next_descr

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        bot.cur_students_message.resend(bot.get_queue().get_cur_and_next_str(), update.effective_chat)


class MovePrevious(AbstractCommand):
    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        if bot.get_queue().move_prev():
            ShowCurrentAndNextStudent.handle_request(update, bot)
            log.info(log_user(update, bot, 'moved previous'))
            Refresh.handle_request(update, bot)


class MoveNext(AbstractCommand):
    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        if bot.get_queue().move_next():
            ShowCurrentAndNextStudent.handle_request(update, bot)
            log.info(log_user(update, bot, 'moved queue'))
            Refresh.handle_request(update, bot)
