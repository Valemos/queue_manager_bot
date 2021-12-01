from queue_bot.commands.command import Command, log_bot_user
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class ShowCurrent(Command):
    command_name = 'get_queue'
    description = commands_descriptions.get_queue_descr

    @classmethod
    def handle_request(cls, update, bot):
        # if queue not selected, but it exists
        # todo refactor
        queues = get_chat_queues(update.effective_chat.id)
        if queues.selected_id is None and len(queues) > 0:
            update.effective_chat.send_message(language_pack.select_queue_or_create_new)
        else:
            bot.last_queue_message.resend(
                queues.get_queue_message(),
                update.effective_chat,
                bot.keyboards.move_queue)

        log_bot_user(update, bot, ' in {0} chat requested queue', update.effective_chat.type)
