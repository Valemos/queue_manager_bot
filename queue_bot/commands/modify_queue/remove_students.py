from queue_bot.bot import parsers as parsers
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack


class RemoveListStudents(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        keyboard = get_chat_queues(update.effective_chat.id).get_queue().get_students_keyboard(cls)
        update.effective_chat.send_message(language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_keyboard(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        cls.handle_request(update, bot)

        # after student deleted, message updates
        keyboard = get_chat_queues(update.effective_chat.id).get_queue().get_students_keyboard(cls)
        # keyboards not equal
        if len(keyboard.inline_keyboard) != len(update.effective_message.reply_markup.inline_keyboard):
            update.effective_chat.send_message(language_pack.select_students, reply_markup=keyboard)

    @classmethod
    def handle_request(cls, update, bot):
        student_str = cls.get_arguments(update.callback_query.data)
        student = parsers.parse_student(student_str)
        get_chat_queues(update.effective_chat.id).get_queue().remove_student(student)
        bot.refresh_last_queue_msg(update)

        bot.request_del()
        log_bot_queue(update, bot, 'removed student {0}', student)