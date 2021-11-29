from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot import language_pack


class ShowStatus(Command):
    command_name = 'current_and_next'
    description = commands_descriptions.current_and_next_descr

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        bot.cur_students_message.resend(get_chat_queues(update.effective_chat.id).get_queue().get_cur_and_next_str(), update.effective_chat)