from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_user, log_bot_queue
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class SelectQueue(Command):
    command_name = 'select_queue'
    description = commands_descriptions.select_queue_descr
    access_requirement = AccessLevel.USER
    check_chat_private = False

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = get_chat_queues(update.effective_chat.id).generate_choice_keyboard(cls)
        update.message.reply_text(language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_request(cls, update, bot):
        queue_name = Command.get_arguments(update.callback_query.data)
        if queue_name is not None:
            queues = get_chat_queues(update.effective_chat.id)
            queues.set_current_queue(queue_name)
            if queues.is_queue_selected():
                update.effective_chat.send_message(language_pack.queue_set_format.format(get_chat_queues(update.effective_chat.id).get_queue().name))
                bot.refresh_last_queue_msg(update)
                log_bot_queue(update, bot, f'selected queue {queue_name}')
            else:
                update.effective_chat.send_message(language_pack.queue_not_selected)
                log_bot_user(update, bot, f'queue not selected {queue_name}')

        update.effective_message.delete()
