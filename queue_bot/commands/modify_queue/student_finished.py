import queue_bot.commands.update_queue.show_status
from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class StudentFinished(Command):
    command_name = 'i_finished'
    description = commands_descriptions.i_finished_descr

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        student_finished = bot.registered_manager.get_update_user_info(update)

        if student_finished == get_chat_queues(update.effective_chat.id).get_queue().get_current():  # finished user currently first
            get_chat_queues(update.effective_chat.id).get_queue().move_next()
            queue_bot.commands.update_queue.show_status.ShowStatus.handle_request(update, bot)
        else:
            update.message.reply_text(language_pack.your_turn_not_now.format(
                bot.registered_manager.get_update_user_info(update).description()
            ))

        err_msg = bot.last_queue_message.update_contents(
            get_chat_queues(update.effective_chat.id).get_queue_message(),
            update.effective_chat
        )
        if err_msg is not None:
            log_bot_queue(update, bot, err_msg)

        bot.save_queue_to_file()
        log_bot_queue(update, bot, 'finished: {0}', get_chat_queues(update.effective_chat.id).get_queue().get_current().str_name_id())