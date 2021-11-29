from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack


class AddStudent(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        update.effective_chat.send_message(get_chat_queues(update.effective_chat.id).get_queue_str())
        update.effective_chat.send_message(language_pack.send_student_name_to_end)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        # todo add student by forwarding
        name = update.message.text
        if parsers.check_student_name(name):
            get_chat_queues(update.effective_chat.id).get_queue().append_by_name(name)
            update.effective_chat.send_message(language_pack.student_set)
            bot.refresh_last_queue_msg(update)
            bot.request_del()
            log_bot_queue(update, bot, 'added {0}', name)
        else:
            update.effective_chat.send_message(language_pack.name_incorrect)
