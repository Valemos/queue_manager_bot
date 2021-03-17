from queue_bot.bot.access_levels import AccessLevel
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.commands.abstract_command import AbstractCommand


class Cancel(AbstractCommand):

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_message.delete()
        bot.request_del()


class Start(AbstractCommand):
    command_name = 'start'
    description = commands_descriptions.start_descr

    @classmethod
    def handle_request(cls, update, bot):
        # if god user not exists, set current user as AccessLevel.GOD and set admins as AccessLevel.ADMIN
        if not bot.registered.exists_user_access(AccessLevel.GOD):
            bot.registered.add_user(update.message.from_user.username, update.message.from_user.telegram_id)
            bot.registered.set_god(update.message.from_user.telegram_id)
            update.message.reply_text(bot.language_pack.first_user_added.format(update.message.from_user.username))

            for admin in update.effective_chat.get_administrators():
                bot.registered.add_user(admin.user.username, admin.user.telegram_id)
                bot.registered.set_admin(admin.user.telegram_id)

            bot.save_registered_to_file()
            update.effective_chat.send_message(bot.language_pack.admins_added)
        else:
            update.message.reply_text(bot.language_pack.bot_already_running)


class Stop(AbstractCommand):
    command_name = 'stop'
    description = commands_descriptions.stop_descr
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_reply(cls, update, bot):
        update.message.reply_text(bot.language_pack.bot_stopped)
        bot.stop()


class ShowLogs(AbstractCommand):
    command_name = 'logs'
    description = commands_descriptions.logs_descr
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_reply(cls, update, bot):
        trim = 4090
        trimmed_msg = bot.logger.get_logs()[-trim:]
        if len(trimmed_msg) >= trim:
            trimmed_msg = "...\n" + trimmed_msg[trimmed_msg.index('\n'):]

        update.effective_chat.send_message(trimmed_msg)
