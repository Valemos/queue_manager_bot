from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command, log_bot_user
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot.objects.access_level import AccessLevel


class RemoveAdmin(Command):
    command_name = 'del_admin'
    description = commands_descriptions.del_admin_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.registered_manager.get_admins_keyboard(cls)
        update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        cls.handle_request(update, bot)
        keyboard = bot.registered_manager.get_admins_keyboard(cls)
        if len(keyboard.inline_keyboard) != len(update.effective_message.reply_markup.inline_keyboard):
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_request(cls, update, bot):
        student_str = cls.get_arguments(update.callback_query.data)
        user = parsers.parse_student(student_str)
        if user.telegram_id is not None:
            if bot.registered_manager.set_user(user.telegram_id):
                bot.save_registered_to_file()
                update.message.reply_text(bot.language_pack.admin_deleted)
                log_bot_user(update, bot, 'deleted admin {0}', update.message.forward_from.full_name)
        else:
            log_bot_user(update, bot, 'error, admin id was None in {0}', cls.query())
        bot.request_del()