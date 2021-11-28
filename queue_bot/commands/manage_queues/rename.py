from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command, log_bot_user, log_bot_queue
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class Rename(Command):
    command_name = 'rename_queue'
    description = commands_descriptions.rename_queue_descr
    access_requirement = AccessLevel.ADMIN

    old_queue_name = None

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.queues_manager.generate_choice_keyboard(cls)
        update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        ManageQueues.Rename.old_queue_name = cls.get_arguments(update.callback_query.data)
        if ManageQueues.Rename.old_queue_name is not None:
            update.effective_chat.send_message(bot.language_pack.queue_rename_send_new_name
                                               .format(ManageQueues.Rename.old_queue_name))
            bot.request_set(cls)
        else:
            log_bot_user(update, bot, 'queue not selected while renaming')

    @classmethod
    def handle_request(cls, update, bot):
        if ManageQueues.Rename.old_queue_name is None:
            ManageQueues.Rename.old_queue_name = bot.language_pack.default_queue_name

        if parsers.check_queue_name(update.message.text):
            bot.queues_manager.rename_queue(ManageQueues.Rename.old_queue_name, update.message.text)
            update.effective_chat.send_message(bot.language_pack.name_set)
            bot.request_del()
            log_bot_queue(update, bot, 'queue renamed', ManageQueues.Rename.old_queue_name)
        else:
            update.effective_chat.send_message(bot.language_pack.name_incorrect)
            update.effective_chat.send_message(bot.language_pack.queue_rename_send_new_name)