from queue_bot.commands.command import Command, log_bot_user
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack


class AddAdmin(Command):
    command_name = 'admin'
    description = commands_descriptions.admin_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(language_pack.get_user_message)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if update.message.forward_from is not None:
            if bot.registered_manager.set_admin(update.message.forward_from.id):
                update.message.reply_text(language_pack.admin_set)
                bot.save_registered_to_file()
                log_bot_user(update, bot, 'added admin {0}', update.message.forward_from.full_name)
            else:
                bot.registered_manager.add_new_user(
                    update.message.forward_from.full_name,
                    update.message.forward_from.id)
                bot.registered_manager.set_admin(update.message.forward_from.id)
        else:
            update.message.reply_text(language_pack.was_not_forwarded)
            log_bot_user(update, bot, 'admin message not forwarded in {0}', cls.query())
        bot.request_del()