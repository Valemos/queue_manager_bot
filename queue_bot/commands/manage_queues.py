from queue_bot.bot import parsers as parsers
from queue_bot.bot.access_levels import AccessLevel
from queue_bot.languages import command_descriptions_rus as commands_descriptions

from command_handler import CommandHandler
from abstract_command import AbstractCommand
from logging_shortcuts import log_bot_queue, log_bot_user


class DeleteQueue(AbstractCommand):
    command_name = 'delete_queue'
    description = commands_descriptions.delete_queue_descr
    access_requirement = AccessLevel.ADMIN

    keyboard_message = None

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.queues.generate_choice_keyboard(cls)
        DeleteQueue.keyboard_message = \
            update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        queue_name = CommandHandler.get_arguments(update.callback_query.data)
        if queue_name is not None:
            if bot.queues.remove_queue(queue_name):
                update.effective_chat.send_message(bot.language_pack.queue_removed.format(queue_name))
                bot.refresh_last_queue_msg(update)

                # update keyboard
                if DeleteQueue.keyboard_message is not None:
                    keyboard = bot.queues.generate_choice_keyboard(cls)
                    DeleteQueue.keyboard_message.edit_text(
                        bot.language_pack.title_select_queue,
                        reply_markup=keyboard)
            else:
                log_bot_user(update, bot, 'queue not found, query: {0}', update.callback_query.data)
        else:
            log_bot_user(update, bot, 'request {0} in {1} has no arguments', update.callback_query.data,
                         cls.__qualname__)


class SelectOtherQueue(AbstractCommand):
    command_name = 'select_queue'
    description = commands_descriptions.select_queue_descr
    access_requirement = AccessLevel.USER
    check_chat_private = False

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.queues.generate_choice_keyboard(cls)
        update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        queue_name = CommandHandler.get_arguments(update.callback_query.data)
        if queue_name is not None:
            if bot.queues.set_current_queue(queue_name):
                if not bot.check_queue_selected():
                    update.effective_chat.send_message(bot.language_pack.queue_not_selected)
                    log_bot_user(update, bot, 'queue was selected by name, but it is not found')
                    return

                update.effective_chat.send_message(bot.language_pack.queue_set_format.format(bot.get_queue().name))
                bot.refresh_last_queue_msg(update)
                log_bot_queue(update, bot, 'selected queue')
            else:
                log_bot_queue(update, bot, 'queue not found, query: {0}', update.callback_query.data)
        else:
            log_bot_user(update, bot, 'request {0} in {1} has no arguments', update.callback_query.data,
                         cls.__qualname__)
        update.effective_message.delete()


class RenameQueue(AbstractCommand):
    command_name = 'rename_queue'
    description = commands_descriptions.rename_queue_descr
    access_requirement = AccessLevel.ADMIN

    old_queue_name = None

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.queues.generate_choice_keyboard(cls)
        update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        RenameQueue.old_queue_name = CommandHandler.get_arguments(update.callback_query.data)
        if RenameQueue.old_queue_name is not None:
            update.effective_chat.send_message(bot.language_pack.queue_rename_send_new_name
                                               .format(RenameQueue.old_queue_name))
            bot.request_set(cls)
        else:
            log_bot_user(update, bot, 'queue not selected while renaming')

    @classmethod
    def handle_request(cls, update, bot):
        if RenameQueue.old_queue_name is None:
            RenameQueue.old_queue_name = bot.language_pack.default_queue_name

        if parsers.check_queue_name(update.message.text):
            bot.queues.rename_queue(RenameQueue.old_queue_name, update.message.text)
            update.effective_chat.send_message(bot.language_pack.name_set)
            bot.request_del()
            log_bot_queue(update, bot, 'queue renamed', RenameQueue.old_queue_name)
        else:
            update.effective_chat.send_message(bot.language_pack.name_incorrect)
            update.effective_chat.send_message(bot.language_pack.queue_rename_send_new_name)


class SaveQueuesToGoogleDrive(AbstractCommand):
    command_name = 'sq'
    description = commands_descriptions.save_queues_to_drive
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_request(cls, update, bot):
        bot.save_to_cloud()
        update.effective_chat.send_message(bot.language_pack.queues_saved_to_cloud)
