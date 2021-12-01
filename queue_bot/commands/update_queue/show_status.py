from queue_bot.commands.command import Command
from queue_bot.languages import command_descriptions_rus as commands_descriptions
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class ShowStatus(Command):
    command_name = 'current_and_next'
    description = commands_descriptions.current_and_next_descr

    @staticmethod
    def create_status_message(cur_stud, next_stud):
        msg = ''
        if cur_stud is not None:
            msg = 'Сдает - {0}'.format(cur_stud.description())

        if next_stud is not None:
            msg += '\nГотовится - {0}'.format(next_stud.description())

        return msg if msg != '' else language_pack.queue_finished

    @classmethod
    def handle_request(cls, update, bot):
        if not bot.check_queue_selected():
            update.effective_chat.send_message(language_pack.queue_not_selected)
            return

        queue = get_chat_queues(update.effective_chat.id).get_queue()
        current_name, next_name = queue.get_cur_and_next()
        message = cls.create_status_message(current_name, next_name)
        bot.cur_students_message.resend(message, update.effective_chat)
