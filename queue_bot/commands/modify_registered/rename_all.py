from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel


class RenameAllUsers(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(language_pack.enter_new_list_in_order)
        bot.request_set(cls)

    def handle_request(cls, update, bot):
        names = parsers.parse_names(update.message.text)
        if len(names) <= len(bot.registered_manager):
            for i in range(len(names)):
                bot.registered_manager.rename_user(i, names[i])
        else:
            update.effective_chat.send_message(language_pack.names_more_than_users)
            bot.logger.log('names more than users - {0}'
                           .format(bot.registered_manager.get_update_user_info(update)))
        bot.request_del()