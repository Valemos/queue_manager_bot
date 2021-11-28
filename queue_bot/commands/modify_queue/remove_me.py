from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions


class RemoveMe(Command):
    command_name = 'remove_me'
    description = commands_descriptions.remove_me_descr

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        student = bot.registered_manager.get_user_by_update(update)
        if student in bot.get_queue():
            bot.get_queue().remove_student(student)

            err_msg = bot.last_queue_message.update_contents(bot.queues_manager.get_queue_str(), update.effective_chat)
            if err_msg is not None:
                log_bot_queue(update, bot, err_msg)
            update.message.reply_text(bot.language_pack.you_deleted)

            bot.save_queue_to_file()
            log_bot_queue(update, bot, 'removed himself')
        else:
            update.message.reply_text(bot.language_pack.you_not_found)