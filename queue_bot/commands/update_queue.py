from abstract_command import AbstractCommand
from logging_shortcuts import log_bot_queue, log_bot_user
from queue_bot.languages import command_descriptions_rus as commands_descriptions


class ShowCurrentQueue(AbstractCommand):
    command_name = 'get_queue'
    description = commands_descriptions.get_queue_descr

    @classmethod
    def handle_reply(cls, update, bot):
        # if queue not selected, but it exists
        if bot.queues_manager.selected_queue is None and len(bot.queues_manager) > 0:
            update.effective_chat.send_message(bot.language_pack.select_queue_or_create_new)
        else:
            bot.last_queue_message.resend(
                bot.queues_manager.get_queue_str(),
                update.effective_chat,
                bot.keyboards.move_queue)

        log_bot_user(update, bot, ' in {0} chat requested queue', update.effective_chat.type)


class Refresh(AbstractCommand):
    @classmethod
    def handle_request(cls, update, bot):
        if not bot.last_queue_message.message_exists(update.effective_chat):
            update.effective_message.delete()
        err_msg = bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
        if err_msg is not None:
            log_bot_queue(update, bot, err_msg)

        log_bot_user(update, bot, 'refreshed queue')


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
            log_bot_user(update, bot, 'moved previous')
            Refresh.handle_request(update, bot)


class MoveNext(AbstractCommand):
    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        if bot.get_queue().move_next():
            ShowCurrentAndNextStudent.handle_request(update, bot)
            log_bot_user(update, bot, 'moved queue')
            Refresh.handle_request(update, bot)
