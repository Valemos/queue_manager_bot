import logging

from queue_bot.bot import parsers as parsers
from queue_bot.bot.access_levels import AccessLevel
from queue_bot.languages import command_descriptions_rus as commands_descriptions

from queue_bot.command_handling import CommandHandler
from .abstract_command import AbstractCommand
from .logging_shortcuts import log_queue, log_user


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ShowMenu(AbstractCommand):
    command_name = 'edit_registered'
    description = commands_descriptions.edit_registered_descr
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.title_edit_registered,
                                           reply_markup=bot.keyboards.modify_registered)


class ShowListUsers(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.registered.get_users_str())


class AddListUsers(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.set_registered_students)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        new_users, errors = parsers.parse_users(update.effective_message.text)
        bot.registered.append_users(new_users)

        if len(errors) > 0:
            update.effective_chat.send_message(bot.language_pack.error_in_this_values.format('\n'.join(errors)))
        if len(new_users) > 0:
            update.effective_chat.send_message(bot.language_pack.users_added)

        bot.save_registered_to_file()
        bot.request_del()
        log.info(log_queue(update, bot, f'added users: {new_users}'))


class AddUser(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.get_user_message)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if update.message.forward_from is not None:
            bot.registered.add_user(update.message.forward_from.full_name,
                                    update.message.forward_from.telegram_id)
            update.message.reply_text(bot.language_pack.user_register_successful)
            bot.save_registered_to_file()
            log.info(log_queue(update, bot, f'added one user: {update.message.forward_from.full_name}'))
        else:
            update.message.reply_text(bot.language_pack.was_not_forwarded)

        bot.request_del()


class RenameAllUsers(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        update.effective_chat.send_message(bot.language_pack.enter_new_list_in_order)
        bot.request_set(cls)

    def handle_request(cls, update, bot):
        names = parsers.parse_names(update.message.text)
        if len(names) <= len(bot.registered):
            for i in range(len(names)):
                bot.registered.rename_user(i, names[i])
        else:
            update.effective_chat.send_message(bot.language_pack.names_more_than_users)
            bot.logger.log('names more than users - {0}'
                           .format(bot.registered.get_user_by_update(update)))
        bot.request_del()


class RenameUser(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    edited_user = None

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        cls.edited_user = None
        keyboard = bot.get_queue().get_keyboard(cls)
        update.effective_chat.send_message(bot.language_pack.select_student, reply_markup=keyboard)
        update.effective_chat.send_message(bot.language_pack.select_student)
        bot.request_set(cls)

    @classmethod
    def handle_keyboard(cls, update, bot):
        argument = CommandHandler.get_arguments(update.callback_query.data)
        cls.edited_user = parsers.parse_student(argument)
        update.effective_chat.send_message(bot.language_pack.enter_student_name)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if cls.edited_user is not None:
            bot.registered.rename_user(cls.edited_user, update.message.text)
            update.effective_chat.send_message(bot.language_pack.value_set)
            log.info(log_user(update, bot, f'student {cls.edited_user} renamed to {update.message.text}'))
        else:
            log.error(log_user(update, bot, f'error, student was None in {cls.__qualname__}'))


class RemoveListUsers(AbstractCommand):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.registered.get_users_keyboard(cls)
        update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        cls.handle_request(update, bot)
        keyboard = bot.registered.get_users_keyboard(cls)
        # if keyboards not equal
        if len(keyboard.inline_keyboard) != len(update.effective_message.reply_markup.inline_keyboard):
            update.effective_chat.send_message(bot.language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_request(cls, update, bot):
        student_str = CommandHandler.get_arguments(update.callback_query.data)
        user = parsers.parse_student(student_str)
        if user.get_id() is not None:
            bot.registered.remove_by_id(user.telegram_id)
            bot.refresh_last_queue_msg(update)

            bot.request_del()
            log.info(log_queue(update, bot, f'removed user {user}'))
        else:
            log.error(log_user(update, bot, f'error, user id is None in {cls.__qualname__}'))
