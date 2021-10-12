import logging

from queue_bot.bot import parsers as parsers
from queue_bot.bot.access_levels import AccessLevel
from queue_bot.command_handling import CommandHandler
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from .abstract_command import AbstractCommand
from .logging_shortcuts import log_user

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class AddAdmin(AbstractCommand):
    command_name = 'admin'
    description = commands_descriptions.admin_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.get_user_message)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if update.message.forward_from is not None:
            if bot.registered.set_admin(update.message.forward_from.telegram_id):
                update.message.reply_text(bot.language_pack.admin_set)
                bot.save_registered_to_file()
                log.info(log_user(update, bot, f'added admin {update.message.forward_from.full_name}'))
            else:
                bot.registered.add_user(
                    update.message.forward_from.full_name,
                    update.message.forward_from.telegram_id)
                bot.registered.set_admin(update.message.forward_from.telegram_id)
        else:
            update.message.reply_text(bot.language_pack.was_not_forwarded)
            log.info(log_user(update, bot, f'admin message not forwarded in {cls.__qualname__}'))
        bot.request_del()


class RemoveAdmin(AbstractCommand):
    command_name = 'del_admin'
    description = commands_descriptions.del_admin_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.registered.get_admins_keyboard(cls)
        update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        cls.handle_request(update, bot)
        keyboard = bot.registered.get_admins_keyboard(cls)
        if len(keyboard.inline_keyboard) != len(update.effective_message.reply_markup.inline_keyboard):
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_request(cls, update, bot):
        student_str = CommandHandler.get_arguments(update.callback_query.data)
        user = parsers.parse_student(student_str)
        if user.get_id() is not None:
            if bot.registered.set_user(user.telegram_id):
                bot.save_registered_to_file()
                update.message.reply_text(bot.language_pack.admin_deleted)
                log.info(log_user(update, bot, f'deleted admin {update.message.forward_from.full_name}'))
        else:
            log.info(log_user(update, bot, f'error, admin id was None in {cls.__qualname__}'))
        bot.request_del()
