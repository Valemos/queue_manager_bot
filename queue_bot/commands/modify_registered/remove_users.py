from queue_bot.bot import parsers as parsers
from queue_bot.commands.misc.logging import log_bot_queue, log_bot_user
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel


class RemoveListUsers(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.registered_manager.get_users_keyboard(cls)
        update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        cls.handle_request(update, bot)
        keyboard = bot.registered_manager.get_users_keyboard(cls)
        # if keyboards not equal
        if len(keyboard.inline_keyboard) != len(update.effective_message.reply_markup.inline_keyboard):
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_request(cls, update, bot):
        student_str = cls.get_arguments(update.callback_query.data)
        user = parsers.parse_student(student_str)
        if user.telegram_id is not None:
            bot.registered_manager.remove_by_id(user.telegram_id)
            bot.refresh_last_queue_msg(update)

            bot.request_del()
            log_bot_queue(update, bot, 'removed user {0}', user)
        else:
            log_bot_user(update, bot, 'error, user id is None in {0}', cls.query())