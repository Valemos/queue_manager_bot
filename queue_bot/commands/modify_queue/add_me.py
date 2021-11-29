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
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        info = get_chat_registered(update.effective_chat.id).get_from_update(update)
        get_chat_queues(update.effective_chat.id).get_queue().append_member(name, telegram_id)

        err_msg = bot.last_queue_message.update_contents(get_chat_queues(update.effective_chat.id).get_queue_str(), update.effective_chat)
        if err_msg is not None:
            log_bot_queue(update, bot, err_msg)

        update.message.reply_text(language_pack.you_added_to_queue)

        bot.save_queue_to_file()
        log_bot_queue(update, bot, 'user added himself')