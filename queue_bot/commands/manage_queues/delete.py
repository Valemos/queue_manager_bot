from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_user
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class Delete(Command):
    command_name = 'delete_queue'
    description = commands_descriptions.delete_queue_descr
    access_requirement = AccessLevel.ADMIN

    keyboard_message = None

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = get_chat_queues(update.effective_chat.id).generate_choice_keyboard(cls)
        update.message.reply_text(language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_request(cls, update, bot):
        queue_name = Command.get_arguments(update.callback_query.data)
        if queue_name is None:
            log_bot_user(update, bot, 'request {0} in {1} has no arguments', update.callback_query.data,
                         cls.__qualname__)
            return

        try:
            get_chat_queues(update.effective_chat.id).remove_queue(queue_name)
            update.effective_chat.send_message(language_pack.queue_removed.format(queue_name))
            bot.refresh_last_queue_msg(update)

            # update keyboard
            keyboard = get_chat_queues(update.effective_chat.id).generate_choice_keyboard(cls)
            update.effective_message.edit_text(language_pack.title_select_queue, reply_markup=keyboard)
        except ValueError as err:
            log_bot_user(update, bot, '{0}: {1}', err.args, update.callback_query.data)
