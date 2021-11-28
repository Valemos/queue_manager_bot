from queue_bot.bot import parsers as parsers
from queue_bot.commands.misc.logging import log_bot_queue, log_bot_user
from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class RenameQueueState:
    def __init__(self, user_id: int, old_queue_name = None):
        self.chat_id = user_id
        self.old_queue_name = old_queue_name


class Rename(Command):

    command_name = 'rename_queue'
    description = commands_descriptions.rename_queue_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        # todo check if can resume or delete
        keyboard = bot.queues_manager.generate_choice_keyboard(cls)
        update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        # todo add state persistence
        name = cls.get_arguments(update.callback_query.data)
        state = RenameQueueState(update.effective_user.id, name)

        update.effective_chat.send_message(bot.language_pack.queue_rename_send_new_name.format(name))
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        # todo query state
        state: RenameQueueState
        if state.old_queue_name is None:
            state.old_queue_name = bot.language_pack.default_queue_name

        new_name = update.message.text
        if parsers.check_queue_name(new_name):
            bot.queues_manager.rename_queue(state.old_queue_name, new_name)
            update.effective_chat.send_message(bot.language_pack.name_set)
            bot.request_del()
            log_bot_queue(update, bot, 'queue renamed {0} {1}', state.old_queue_name, new_name)
        else:
            update.effective_chat.send_message(bot.language_pack.name_incorrect)
            rename_msg = bot.language_pack.queue_rename_send_new_name.format(state.old_queue_name)
            update.effective_chat.send_message(rename_msg)
