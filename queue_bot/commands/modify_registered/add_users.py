from queue_bot.bot import parsers as parsers
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel


class AddListUsers(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.set_registered_students)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        new_users, errors = parsers.parse_users(update.effective_message.text)
        bot.registered_manager.append_users(new_users)

        if len(errors) > 0:
            update.effective_chat.send_message(bot.language_pack.error_in_this_values.format('\n'.join(errors)))
        if len(new_users) > 0:
            update.effective_chat.send_message(bot.language_pack.users_added)

        bot.save_registered_to_file()
        bot.request_del()
        log_bot_queue(update, bot, 'added users: {0}', new_users)