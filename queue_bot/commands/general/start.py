from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class Start(Command):
    command_name = 'start'
    description = commands_descriptions.start_descr

    @classmethod
    def handle_request(cls, update, bot):
        # if god user not exists, set current user as AccessLevel.GOD and set admins as AccessLevel.ADMIN
        if not bot.registered_manager.exists_user_access(AccessLevel.GOD):
            bot.registered_manager.append_new_user(update.message.from_user.username, update.message.from_user.id)
            bot.registered_manager.set_god(update.message.from_user.id)
            update.message.reply_text(bot.language_pack.first_user_added.format(update.message.from_user.username))

            for admin in update.effective_chat.get_administrators():
                bot.registered_manager.append_new_user(admin.user.username, admin.user.id)
                bot.registered_manager.set_admin(admin.user.id)

            bot.save_registered_to_file()
            update.effective_chat.send_message(bot.language_pack.admins_added)
        else:
            update.message.reply_text(bot.language_pack.bot_already_running)