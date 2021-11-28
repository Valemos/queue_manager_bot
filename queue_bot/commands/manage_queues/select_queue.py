from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_user, log_bot_queue
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class SelectQueue(Command):
    command_name = 'select_queue'
    description = commands_descriptions.select_queue_descr
    access_requirement = AccessLevel.USER
    check_chat_private = False

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.queues_manager.generate_choice_keyboard(cls)
        update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        queue_name = Command.get_arguments(update.callback_query.data)
        if queue_name is not None:
            if bot.queues_manager.set_current_queue(queue_name):
                if not bot.check_queue_selected():
                    update.effective_chat.send_message(bot.language_pack.queue_not_selected)
                    log_bot_user(update, bot, 'queue was selected by name, but it is not found')
                    return

                update.effective_chat.send_message(bot.language_pack.queue_set_format.format(bot.get_queue().name))
                bot.refresh_last_queue_msg(update)
                log_bot_queue(update, bot, 'selected queue')
            else:
                log_bot_queue(update, bot, 'queue not found, query: {0}', update.callback_query.data)
        else:
            log_bot_user(update, bot, 'request {0} in {1} has no arguments', update.callback_query.data, cls.__qualname__)
        update.effective_message.delete()