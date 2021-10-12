import logging

from queue_bot.bot.access_levels import AccessLevel
from queue_bot.command_handling.command_handler import CommandHandler
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from .abstract_command import AbstractCommand
from .logging_shortcuts import log_queue, log_user

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class DeleteQueue(AbstractCommand):
    command_name = 'delete_queue'
    description = commands_descriptions.delete_queue_descr
    access_requirement = AccessLevel.ADMIN

    keyboard_message = None

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.queues.generate_keyboard(cls)
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
                    keyboard = bot.queues.generate_keyboard(cls)
                    DeleteQueue.keyboard_message.edit_text(
                        bot.language_pack.title_select_queue,
                        reply_markup=keyboard)
            else:
                log.error(log_user(update, bot, f'queue not found, query: {update.callback_query.data}'))
        else:
            log.error(log_user(update, bot, f'in {cls.__qualname__} request {update.callback_query.data} '
                                             'has no arguments'))


class SelectOtherQueue(AbstractCommand):
    command_name = 'select_queue'
    description = commands_descriptions.select_queue_descr
    access_requirement = AccessLevel.USER
    check_chat_private = False

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.queues.generate_keyboard(cls)
        update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        queue_name = CommandHandler.get_arguments(update.callback_query.data)
        if queue_name is not None:
            if bot.queues.select_queue(queue_name):
                if not bot.check_queue_selected():
                    update.effective_chat.send_message(bot.language_pack.queue_not_selected)
                    log.error(log_user(update, bot, f'queue was selected by name{queue_name}, but not found'))
                    return

                update.effective_chat.send_message(bot.language_pack.queue_set_format.format(bot.get_queue().name))
                bot.refresh_last_queue_msg(update)
                log.info(log_queue(update, bot, 'selected queue'))
            else:
                log.error(log_queue(update, bot, f'queue not found, query: {update.callback_query.data}'))
        else:
            log.error(log_user(update, bot, f'request {update.callback_query.data} has no arguments'))
        update.effective_message.delete()


class RenameQueue(AbstractCommand):
    command_name = 'rename_queue'
    description = commands_descriptions.rename_queue_descr
    access_requirement = AccessLevel.ADMIN

    old_queue_name = None

    @classmethod
    def handle_reply(cls, update, bot):
        keyboard = bot.queues.generate_keyboard(cls)
        update.message.reply_text(bot.language_pack.title_select_queue, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        RenameQueue.old_queue_name = CommandHandler.get_arguments(update.callback_query.data)
        if RenameQueue.old_queue_name is not None:
            update.effective_chat.send_message(bot.language_pack.queue_rename_send_new_name
                                               .format(RenameQueue.old_queue_name))
            RenameQueue.handle_request(update, bot)
        else:
            log.error(log_user(update, bot, 'keyboard argument is None while renaming queue'))

    @classmethod
    def handle_request(cls, update, bot):
        if bot.queues.rename_queue(RenameQueue.old_queue_name, update.message.text):
            update.effective_chat.send_message(bot.language_pack.name_set)
            log.info(log_queue(update, bot, f'queue {RenameQueue.old_queue_name} renamed to {update.message.text}'))
        else:
            update.effective_chat.send_message(bot.language_pack.name_incorrect)

        bot.request_del()


class SaveQueuesToGoogleDrive(AbstractCommand):
    command_name = 'sq'
    description = commands_descriptions.save_queues_to_drive
    access_requirement = AccessLevel.GOD

    @classmethod
    def handle_request(cls, update, bot):
        bot.save_to_cloud()
        update.effective_chat.send_message(bot.language_pack.queues_saved_to_cloud)
