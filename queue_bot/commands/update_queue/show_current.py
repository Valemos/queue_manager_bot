from queue_bot.commands.command import Command, log_bot_user
from queue_bot.languages import command_descriptions_rus as commands_descriptions


class ShowCurrent(Command):
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