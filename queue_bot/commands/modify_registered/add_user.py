from queue_bot.commands.command import Command, log_bot_queue
from queue_bot.objects.access_level import AccessLevel


class AddUser(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.get_user_message)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if update.message.forward_from is not None:
            bot.registered_manager.append_new_user(update.message.forward_from.full_name, update.message.forward_from.id)
            update.message.reply_text(bot.language_pack.user_register_successfull)
            bot.save_registered_to_file()
            log_bot_queue(update, bot, 'added one user: {0}', update.message.forward_from.full_name)
        else:
            update.message.reply_text(bot.language_pack.was_not_forwarded)

        bot.request_del()