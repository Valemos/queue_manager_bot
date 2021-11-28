from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command, log_bot_user
from queue_bot.objects.access_level import AccessLevel


class RenameUser(Command):
    access_requirement = AccessLevel.ADMIN

    edited_user = None

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        cls.edited_user = None
        keyboard = bot.get_queue().get_students_keyboard(cls)
        update.effective_chat.send_message(bot.language_pack.select_student, reply_markup=keyboard)
        update.effective_chat.send_message(bot.language_pack.select_student)
        bot.request_set(cls)

    @classmethod
    def handle_keyboard(cls, update, bot):
        argument = cls.get_arguments(update.callback_query.data)
        cls.edited_user = parsers.parse_student(argument)
        update.effective_chat.send_message(bot.language_pack.enter_student_name)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if cls.edited_user is not None:
            bot.registered_manager.rename_user(cls.edited_user, update.message.text)
            update.effective_chat.send_message(bot.language_pack.value_set)
            log_bot_user(update, bot, 'student {0} renamed to {1}', cls.edited_user, update.message.text)
        else:
            log_bot_user(update, bot, 'error, student was none in {0}', cls.query())