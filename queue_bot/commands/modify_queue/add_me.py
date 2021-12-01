from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues
from queue_bot.objects.registered_manager import get_chat_registered


class AddMe(Command):
    command_name = 'add_me'
    description = commands_descriptions.add_me_descr

    @classmethod
    def handle_request(cls, update, bot):
        chat = update.effective_chat
        if not bot.check_queue_selected():
            chat.send_message(language_pack.queue_not_selected)
            return

        info = get_chat_registered(chat.id).get_update_user_info(update)
        queues = get_chat_queues(chat.id)
        queues.get_queue().append_info(info)

        new_queue_str = queues.get_queue_message()
        err_msg = bot.last_queue_message.update_contents(new_queue_str, chat)
        if err_msg is not None:
            log_bot_queue(update, bot, err_msg)

        update.message.reply_text(language_pack.you_added_to_queue)

        bot.save_queue_to_file()
        log_bot_queue(update, bot, 'user added himself')
