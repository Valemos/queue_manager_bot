from queue_bot.commands.misc.logging import log_bot_queue
from queue_bot.commands.command import Command
from queue_bot.objects.access_level import AccessLevel
from queue_bot import language_pack
from queue_bot.objects.queues_manager import get_chat_queues


class ShowList(Command):
    access_requirement = AccessLevel.ADMIN

    @classmethod
    def handle_request(cls, update, bot):
        if bot.check_queue_selected():
            queues = get_chat_queues(update.effective_chat.id)

            member_names = queues.get_queue().get_member_names()
            queue_name = queues.get_queue().get_name()
            message = language_pack.queue_simple_format.format(name=queue_name, students='\n'.join(member_names))
            update.effective_chat.send_message(message)

            log_bot_queue(update, bot, 'showed list')
        else:
            update.effective_chat.send_message(language_pack.queue_not_selected)
            log_bot_queue(update, bot, 'queue not exists')
