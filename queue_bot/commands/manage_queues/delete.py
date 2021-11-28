from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_user
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class Delete(Command):
    command_name = 'delete_queue'
    description = commands_descriptions.delete_queue_descr
    access_requirement = AccessLevel.ADMIN

    keyboard_message = None

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.queues_manager.generate_choice_keyboard(cls)
        # todo save to manage queues dialog state
        # ManageQueues.Delete.keyboard_message = \
        #     update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        queue_name = Command.get_arguments(update.callback_query.data)
        if queue_name is not None:
            if bot.queues_manager.remove_queue(queue_name):
                update.effective_chat.send_message(bot.language_pack.queue_removed.format(queue_name))
                bot.refresh_last_queue_msg(update)

                # todo use manage queues dialog state
                # update keyboard
                # if ManageQueues.Delete.keyboard_message is not None:
                #     keyboard = bot.queues_manager.generate_choice_keyboard(cls)
                #     ManageQueues.Delete.keyboard_message.edit_text(
                #         bot.language_pack.title_select_queue,
                #         reply_markup=keyboard)
            else:
                log_bot_user(update, bot, 'queue not found, query: {0}', update.callback_query.data)
        else:
            log_bot_user(update, bot, 'request {0} in {1} has no arguments', update.callback_query.data, cls.__qualname__)