from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.queues_manager import get_chat_queues
from queue_bot.objects.registered_manager import get_chat_registered
from queue_bot import language_pack


class RemoveMe(Command):
    command_name = 'remove_me'
    description = commands_descriptions.remove_me_descr

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        queues = get_chat_queues(update.effective_chat.id)
        student = get_chat_registered(update.effective_chat.id).get_update_user_info(update)
        if student in queues:
            get_chat_queues(update.effective_chat.id).get_queue().remove_student(student)

            err_msg = bot.last_queue_message.update_contents(
                get_chat_queues(update.effective_chat.id).get_queue_message(),
                update.effective_chat
            )
            if err_msg is not None:
                log_bot_queue(update, bot, err_msg)
            update.message.reply_text(language_pack.you_deleted)

            bot.save_queue_to_file()
            log_bot_queue(update, bot, 'removed himself')
        else:
            update.message.reply_text(language_pack.you_not_found)
