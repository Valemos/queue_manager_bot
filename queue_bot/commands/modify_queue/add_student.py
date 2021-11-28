from queue_bot.bot import parsers as parsers
from queue_bot.commands.command import Command
from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.objects.access_level import AccessLevel


class AddStudent(Command):

    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_reply(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(bot.language_pack.queue_not_selected)
            return

        update.effective_chat.send_message(bot.queues_manager.get_queue_str())
        update.effective_chat.send_message(bot.language_pack.send_student_name_to_end)
        bot.request_set(cls)

    @classmethod
    def handle_request(cls, update, bot):
        if parsers.check_student_name(update.message.text):
            if bot.get_queue().append_by_name(update.message.text):
                log_msg = 'found student in registered \'' + update.message.text + '\''
            else:
                log_msg = 'searched similar student \'' + update.message.text + '\''

            update.effective_chat.send_message(bot.language_pack.student_set)
            bot.refresh_last_queue_msg(update)
            bot.request_del()
            log_bot_queue(update, bot, '{0}', log_msg)
        else:
            update.effective_chat.send_message(bot.language_pack.name_incorrect)